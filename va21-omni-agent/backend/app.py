import requests
import json
from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO, emit, Namespace
from duckduckgo_search import DDGS
import google.generativeai as genai
import ptyprocess
import os
import threading
from werkzeug.utils import secure_filename
from rag_manager import RAGManager

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*")

# Default settings
settings = {
    "provider": "ollama",
    "url": "http://localhost:11434",
    "api_key": ""
}

# Use a dictionary to store conversation history for each session
histories = {}
# Dictionary to store pty processes for each session
ptys = {}

rag_manager = RAGManager()

SYSTEM_PROMPT = """
You are a helpful assistant with access to a web search tool.
To use the tool, output a JSON object with the following format:
{"tool": "web_search", "query": "your search query"}
When you have the answer, reply to the user.
"""

def perform_web_search(query):
    """Performs a web search using DuckDuckGo and returns the results."""
    try:
        results = DDGS().text(query, max_results=5)
        return "\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
    except Exception as e:
        return f"Error performing web search: {e}"

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
        # ... (same logic as before, but using self.emit)
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
                # Add the context to the history
                # Using a system message to provide context is a common pattern
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
                if "tool" in tool_call and tool_call["tool"] == "web_search":
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
            # For now, just echo the command
            # We will add the LLM logic in the next step
            pty.write(f"\r\nAgent Mode: Command received: '{command}'\r\n".encode('utf-8'))
            # Let's also write a newline to simulate command execution
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
        # Ensure the data directory exists
        os.makedirs(rag_manager.data_dir, exist_ok=True)
        file_path = os.path.join(rag_manager.data_dir, filename)
        file.save(file_path)

        try:
            rag_manager.add_document(file_path)
            return jsonify({'message': f'File "{filename}" uploaded and processed successfully.'})
        except Exception as e:
            return jsonify({'error': f'Error processing file: {e}'}), 500

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
