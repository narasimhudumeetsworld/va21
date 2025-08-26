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
from long_term_memory import LongTermMemoryManager
from workflow_engine import WorkflowEngine

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
ltm_manager = LongTermMemoryManager()

SYSTEM_PROMPT = """
You are a helpful assistant. You have access to the following tools:
- Web Search: To search the web for information. To use, output: {"tool": "web_search", "query": "your search query"}
- Create Backup: To save the current conversation history and long-term memory to your configured backup location. To use, output: {"tool": "create_backup"}
- Remember: To save a key-value pair to your long-term memory. To use, output: {"tool": "remember", "key": "the key", "value": "the value"}
- Recall: To recall a value from your long-term memory. To use, output: {"tool": "recall", "key": "the key"}
- Log Message: A simple tool that logs a message to the console. To use, output: {"tool": "log_message", "message": "your message"}
When you have the answer, reply to the user.
"""

def perform_web_search(query):
    """Performs a web search using DuckDuckGo and returns the results."""
    try:
        results = DDGS().text(query, max_results=5)
        return "\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
    except Exception as e:
        return f"Error performing web search: {e}"

def create_backup(sid):
    """Saves the conversation history and long-term memory using the configured backup provider."""
    backup_manager = BackupManager(settings)
    history = histories.get(sid, [])
    ltm = ltm_manager.get_all()
    backup_data = { "conversation_history": history, "long_term_memory": ltm }
    file_name = f"omni_agent_backup_{sid}"
    return backup_manager.backup(backup_data, file_name)

def remember(key, value):
    """Saves a key-value pair to long-term memory."""
    return ltm_manager.remember(key, value)

def recall(key):
    """Recalls a value from long-term memory."""
    return ltm_manager.recall(key)

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

    response = requests.post(
        url, headers=headers,
        json={"model": "gemma:2b", "messages": history, "stream": stream},
        stream=stream
    )
    response.raise_for_status()
    return response

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

        if stream:
            class GeminiStreamWrapper:
                def __init__(self, stream):
                    self.stream = stream
                def iter_lines(self):
                    for chunk in self.stream:
                        yield json.dumps({"message": {"content": chunk.text}, "done": False}).encode('utf-8')
                    yield json.dumps({"message": {"content": ""}, "done": True}).encode('utf-8')
                def raise_for_status(self): pass
            return GeminiStreamWrapper(response)
        else:
            return {"message": {"content": response.text}}
    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return {"error": str(e)}

def get_llm_response(history, stream=False):
    """Dispatcher function to get a response from the selected LLM."""
    provider = settings.get("provider", "ollama")
    if provider == "ollama" or provider == "authenticated_ollama":
        response = get_ollama_response(history, stream)
        if not stream:
            return response.json()
        return response
    elif provider == "gemini":
        return get_gemini_response(history, stream)
    else:
        # ... (mock response for invalid provider)
        return None

class ChatNamespace(Namespace):
    def on_connect(self):
        histories[request.sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
        print(f'Chat client connected: {request.sid}')
        self.emit('response', {'data': 'Connected to server'})

    def on_disconnect(self):
        if request.sid in histories:
            del histories[request.sid]
        print(f'Chat client disconnected: {request.sid}')

    def _handle_tool_call(self, tool_call, current_history):
        """Helper function to handle tool calls."""
        tool_name = tool_call.get("tool")
        result = None

        if tool_name == "web_search":
            query = tool_call.get("query")
            if query:
                self.emit('response', {'data': f"Running web search for: \"{query}\"...\n\n"})
                result = perform_web_search(query)
        elif tool_name == "create_backup":
            result = create_backup(request.sid)
        elif tool_name == "remember":
            key = tool_call.get("key")
            value = tool_call.get("value")
            if key and value:
                result = remember(key, value)
        elif tool_name == "recall":
            key = tool_call.get("key")
            if key:
                result = recall(key)
        elif tool_name == "log_message":
            message = tool_call.get("message")
            if message:
                log_message(message)
                result = f"Message logged: {message}"

        if result:
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

    def on_message(self, message):
        current_history = histories.get(request.sid, [])
        current_history.append({"role": "user", "content": message})

        try:
            search_results = rag_manager.search(message)
            if search_results:
                context = "\n\n".join(search_results)
                current_history.insert(-1, {"role": "system", "content": f"Context: {context}"})
        except Exception as e:
            print(f"Error during RAG search: {e}")

        try:
            response = get_llm_response(current_history, stream=True)
            full_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    data = json.loads(chunk)
                    full_response += data["message"]["content"]
                    if data.get("done"): break

            current_history.append({"role": "assistant", "content": full_response})

            try:
                tool_call = json.loads(full_response)
                if "tool" in tool_call:
                    self._handle_tool_call(tool_call, current_history)
                else:
                    self.emit('response', {'data': full_response})
            except json.JSONDecodeError:
                self.emit('response', {'data': full_response})
        except Exception as e:
            print(f"Error during LLM call: {e}")
            self.emit('response', {'data': f"Error: {e}"})
            if current_history: current_history.pop()

# ... (TerminalNamespace and other routes)

@app.route('/api/workflows/plan', methods=['POST'])
def plan_workflow_route():
    data = request.get_json()
    description = data.get('description')
    if not description:
        return jsonify({'error': 'No description provided'}), 400

    planner_prompt = f"""
You are a workflow planning assistant. Your task is to convert a natural language description of a workflow into a structured JSON plan.
The plan must have a 'name', a 'trigger', and a list of 'steps'.
The 'trigger' must be a schedule in cron format (e.g., "cron: 0 9 * * *").
Each 'step' in the plan must be a call to one of the available tools: log_message(message: str).
Example:
Description: "Every morning at 9, log a hello message"
JSON:
```json
{{
  "name": "Morning Greeting",
  "trigger": "cron: 0 9 * * *",
  "steps": [
    {{
      "tool": "log_message",
      "params": {{
        "message": "Hello from the scheduled workflow!"
      }}
    }}
  ]
}}
```

Natural language description: "{description}"

JSON plan:
"""

    try:
        response_data = get_llm_response([{"role": "user", "content": planner_prompt}], stream=False)
        plan_text = response_data.get("message", {}).get("content", "")

        # Extract JSON from the markdown code block
        plan_json_str = plan_text.split("```json")[1].split("```")[0].strip()
        plan = json.loads(plan_json_str)

        workflow_name = secure_filename(plan.get("name", "unnamed_workflow")) + ".json"
        workflow_path = os.path.join("workflows", workflow_name)
        os.makedirs("workflows", exist_ok=True)
        with open(workflow_path, 'w') as f:
            json.dump(plan, f, indent=2)

        return jsonify({'message': f'Workflow "{workflow_name}" created successfully.'})

    except Exception as e:
        return jsonify({'error': f'Error creating workflow plan: {e}'}), 500

# ... (other routes)

def log_message(message):
    """A simple tool that logs a message."""
    print(f"WORKFLOW LOG: {message}")

if __name__ == '__main__':
    # Define the tools available to the workflow engine
    workflow_tools = {
        "log_message": log_message
    }

    # Initialize and start the workflow engine
    workflow_engine = WorkflowEngine(tools=workflow_tools)
    workflow_engine.start()

    # Use allow_unsafe_werkzeug=True for development with Flask 2.3+ and Socket.IO
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
