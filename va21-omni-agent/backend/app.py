import requests
import json
from flask import Flask, send_from_directory, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit, Namespace
from duckduckgo_search import DDGS
import google.generativeai as genai
import ptyprocess
import os
import threading
from werkzeug.utils import secure_filename
from rag_manager import RAGManager
import google_auth
from backup_manager import BackupManager

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Default settings
settings = {
    "provider": "ollama",
    "url": "http://localhost:11434",
    "api_key": "",
    "backup_provider": "local",
    "backup_path": "data/backups"
}

# Use a dictionary to store conversation history for each session
histories = {}
# Dictionary to store pty processes for each session
ptys = {}

rag_manager = RAGManager()

SYSTEM_PROMPT = """
You are a helpful assistant. You have access to the following tools:
- Web Search: To search the web for information. To use, output: {"tool": "web_search", "query": "your search query"}
- Backup Conversation: To save the current conversation history to your configured backup location (Local or Google Drive). To use, output: {"tool": "backup_conversation"}
When you have the answer, reply to the user.
"""

def perform_web_search(query):
    """Performs a web search using DuckDuckGo and returns the results."""
    try:
        results = DDGS().text(query, max_results=5)
        return "\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
    except Exception as e:
        return f"Error performing web search: {e}"

def backup_conversation(history, sid):
    """Saves the conversation history using the configured backup provider."""
    backup_manager = BackupManager(settings)
    file_name = f"omni_agent_chat_{sid}" # The manager will add the .enc extension
    return backup_manager.backup(history, file_name)

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

def get_ollama_response(history, stream=False):
    """Gets a response from the Ollama LLM."""
    url = f"{settings['url']}/api/chat"
    headers = {}
    if settings.get('api_key'):
        headers['Authorization'] = f"Bearer {settings['api_key']}"

    return requests.post(
        url,
        headers=headers,
        json={"model": "gemma:2b", "messages": history, "stream": stream},
        stream=True
    )

def get_gemini_response(history, stream=False):
    """Gets a response from the Gemini LLM."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        gemini_history = []
        for msg in history:
            role = msg["role"]
            if role == "assistant":
                role = "model"
            if role in ["user", "model"]:
                gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})
        response = model.generate_content(gemini_history, stream=stream)

        class GeminiStreamWrapper:
            def __init__(self, stream):
                self.stream = stream
            def iter_lines(self):
                for chunk in self.stream:
                    yield json.dumps({"message": {"content": chunk.text}, "done": False}).encode('utf-8')
                yield json.dumps({"message": {"content": ""}, "done": True}).encode('utf-8')
            def raise_for_status(self):
                pass
        return GeminiStreamWrapper(response)
    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        class ErrorResponse:
            def iter_lines(self):
                yield json.dumps({"message": {"content": f"Error communicating with Gemini: {e}"}, "done": True}).encode('utf-8')
            def raise_for_status(self):
                pass
        return ErrorResponse()

def get_llm_response(history, stream=False):
    """Dispatcher function to get a response from the selected LLM."""
    provider = settings.get("provider", "ollama")
    if provider == "ollama" or provider == "authenticated_ollama":
        return get_ollama_response(history, stream)
    elif provider == "gemini":
        return get_gemini_response(history, stream)
    else:
        class MockResponse:
            def iter_lines(self):
                yield json.dumps({"message": {"content": "Invalid LLM provider."}, "done": True}).encode('utf-8')
            def raise_for_status(self):
                pass
        return MockResponse()

class ChatNamespace(Namespace):
    def on_connect(self):
        histories[request.sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
        print(f'Chat client connected: {request.sid}')
        self.emit('response', {'data': 'Connected to server'})

    def on_disconnect(self):
        if request.sid in histories:
            del histories[request.sid]
        print(f'Chat client disconnected: {request.sid}')

    def on_message(self, message):
        current_history = histories.get(request.sid)
        if not current_history:
            current_history = histories[request.sid] = [{"role": "system", "content": SYSTEM_PROMPT}]

        print(f'Received message from {request.sid}: ' + message)
        current_history.append({"role": "user", "content": message})

        # RAG Integration
        try:
            search_results = rag_manager.search(message)
            if search_results:
                context = "\n\n".join(search_results)
                current_history.insert(-1, {"role": "system", "content": f"Here is some context from uploaded documents that might be relevant:\n{context}"})
        except Exception as e:
            print(f"Error during RAG search: {e}")

        try:
            response = get_llm_response(current_history, stream=True)
            response.raise_for_status()
            full_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    data = json.loads(chunk)
                    full_response += data["message"]["content"]
                    if data.get("done"):
                        break
            current_history.append({"role": "assistant", "content": full_response})
            try:
                tool_call = json.loads(full_response)
                if "tool" in tool_call:
                    if tool_call["tool"] == "web_search":
                        query = tool_call["query"]
                        self.emit('response', {'data': f"Running web search for: \"{query}\"...\n\n"})
                        search_results = perform_web_search(query)
                        current_history.append({"role": "tool", "content": search_results})
                        response = get_llm_response(current_history, stream=True)
                        response.raise_for_status()
                        final_response = ""
                        for chunk in response.iter_lines():
                            if chunk:
                                data = json.loads(chunk)
                                token = data["message"]["content"]
                                final_response += token
                                self.emit('response', {'data': token})
                        current_history.append({"role": "assistant", "content": final_response})
                    elif tool_call["tool"] == "backup_conversation":
                        result = backup_conversation(current_history, request.sid)
                        current_history.append({"role": "tool", "content": result})
                        response = get_llm_response(current_history, stream=True)
                        response.raise_for_status()
                        final_response = ""
                        for chunk in response.iter_lines():
                            if chunk:
                                data = json.loads(chunk)
                                token = data["message"]["content"]
                                final_response += token
                                self.emit('response', {'data': token})
                        current_history.append({"role": "assistant", "content": final_response})
                else:
                    self.emit('response', {'data': full_response})
            except json.JSONDecodeError:
                self.emit('response', {'data': full_response})
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            self.emit('response', {'data': f"Error connecting to Ollama: {e}"})
            if current_history:
                current_history.pop()

class TerminalNamespace(Namespace):
    def on_connect(self):
        print(f"Terminal client connected: {request.sid}")
        pty = ptyprocess.PtyProcess.spawn(['/bin/bash'])
        ptys[request.sid] = pty
        thread = threading.Thread(target=self.read_and_forward_pty_output, args=(request.sid, pty))
        thread.daemon = True
        thread.start()

    def on_disconnect(self):
        print(f"Terminal client disconnected: {request.sid}")
        if request.sid in ptys:
            ptys[request.sid].close()
            del ptys[request.sid]

    def on_terminal_in(self, data):
        if request.sid in ptys:
            ptys[request.sid].write(data.encode('utf-8'))

    def on_agent_command(self, command):
        if request.sid in ptys:
            pty = ptys[request.sid]
            pty.write(f"\r\nAgent Mode: Command received: '{command}'\r\n".encode('utf-8'))
            pty.write(b'\n')

    def read_and_forward_pty_output(self, sid, pty):
        while pty.isalive():
            try:
                output = pty.read(1024).decode('utf-8')
                self.emit('terminal_out', {'output': output}, room=sid)
            except EOFError:
                break

socketio.on_namespace(ChatNamespace('/'))
socketio.on_namespace(TerminalNamespace('/terminal'))

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        os.makedirs(rag_manager.data_dir, exist_ok=True)
        file_path = os.path.join(rag_manager.data_dir, filename)
        file.save(file_path)

        try:
            rag_manager.add_document(file_path)
            return jsonify({'message': f'File "{filename}" uploaded and processed successfully.'})
        except Exception as e:
            return jsonify({'error': f'Error processing file: {e}'}), 500

@app.route('/api/google/auth')
def google_auth_route():
    try:
        flow = google_auth.get_google_auth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        session['state'] = state
        return redirect(authorization_url)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500

@app.route('/api/google/callback')
def google_callback_route():
    state = session.get('state')
    if not state or state != request.args.get('state'):
        return jsonify({'error': 'State mismatch'}), 400

    try:
        flow = google_auth.get_google_auth_flow()
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        google_auth.save_credentials(credentials)
        return redirect(url_for('serve_index'))
    except Exception as e:
        return jsonify({'error': f'An error occurred during token exchange: {e}'}), 500

@app.route('/api/google/status')
def google_status_route():
    credentials = google_auth.get_credentials()
    if credentials:
        return jsonify({'status': 'connected'})
    else:
        return jsonify({'status': 'disconnected'})

@app.route('/api/settings', methods=['GET'])
def get_settings_route():
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings_route():
    global settings
    data = request.get_json()
    if 'provider' in data:
        settings = data
        if settings.get("provider") == "gemini":
            try:
                genai.configure(api_key=settings.get("api_key"))
            except Exception as e:
                return jsonify({'error': f'Failed to configure Gemini: {e}'}), 400
        return jsonify({'message': 'Settings updated successfully'})
    return jsonify({'error': 'Invalid request'}), 400

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
