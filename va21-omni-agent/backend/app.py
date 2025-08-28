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
from gmail_manager import GmailManager
from github_manager import GitHubManager
from prompt_manager import PromptManager
from security_rag_manager import SecurityRAGManager
from security_prompt_manager import SecurityPromptManager
from threat_intelligence import fetch_stories_from_rss, SECURITY_RSS_FEEDS
from local_llm import LocalLLM
import whois
from urllib.parse import urlparse

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Default settings
settings = {
    "provider": "ollama",
    "url": "http://localhost:11434",
    "api_key": "",
    "backup_provider": "local",
    "backup_path": "data/backups",
    "github_pat": ""
}

# Use a dictionary to store conversation history for each session
histories = {}
# Dictionary to store pty processes for each session
ptys = {}

rag_manager = RAGManager()
ltm_manager = LongTermMemoryManager()
prompt_manager = PromptManager()
security_prompt_manager = SecurityPromptManager()
local_llm = LocalLLM()

def analyze_tool_output(output: str) -> bool:
    """
    Analyzes tool output for security risks using the local LLM.
    Returns True if the output is safe, False otherwise.
    """
    if not output:
        return True # Nothing to analyze

    print("--- Running Security Guardian Analysis ---")
    try:
        guardian_prompt = security_prompt_manager.render_prompt(
            'security_guardian',
            {'tool_output': str(output)}
        )
        analysis_result = local_llm.generate(guardian_prompt).strip().upper()

        print(f"Security Guardian Result: {analysis_result}")

        if analysis_result.startswith("UNSAFE"):
            return False

        return True

    except Exception as e:
        print(f"Error during security analysis: {e}")
        return False

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

def check_email(query=""):
    """Searches for emails matching a query."""
    gmail_manager = GmailManager()
    return gmail_manager.check_email(query)

def list_github_repos():
    """Lists the user's GitHub repositories."""
    github_manager = GitHubManager(settings.get("github_pat"))
    return github_manager.list_repos()

def create_github_issue(repo_full_name, title, body=""):
    """Creates an issue in a GitHub repository."""
    github_manager = GitHubManager(settings.get("github_pat"))
    return github_manager.create_issue(repo_full_name, title, body)

def summarize(text):
    """Summarizes a piece of text."""
    prompt = f"Please summarize the following text:\n\n{text}"
    try:
        response = get_llm_response([{"role": "user", "content": prompt}], stream=False)
        return response.get("message", {}).get("content", "")
    except Exception as e:
        return f"Error summarizing text: {e}"

def whois_lookup(url: str):
    """
    Performs a WHOIS lookup on the domain of a given URL.
    Returns a summary of the WHOIS information.
    """
    try:
        domain = urlparse(url).netloc
        if not domain:
            return "Error: Could not parse domain from URL."

        w = whois.whois(domain)
        # Format the result into a readable string
        return f"Domain: {w.domain_name}\nRegistrar: {w.registrar}\nCreation Date: {w.creation_date}\nExpiration Date: {w.expiration_date}\nEmails: {w.emails}"
    except Exception as e:
        return f"Error performing WHOIS lookup: {e}"

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
        system_prompt = prompt_manager.render_prompt('system_prompt.poml')
        histories[request.sid] = [{"role": "system", "content": system_prompt}]
        print(f'Chat client connected: {request.sid}')
        self.emit('response', {'data': 'Connected to server'})

    def on_disconnect(self):
        if request.sid in histories:
            del histories[request.sid]
        print(f'Chat client disconnected: {request.sid}')

    def _handle_tool_call(self, tool_call, current_history):
        """Helper function to handle tool calls."""
        if ltm_manager.is_in_observation_mode():
            self.emit('response', {'data': "\n\n[OBSERVATION MODE]: Agent is in a 5-day observation period due to a recent self-correction. Tool use is being monitored."})

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
        elif tool_name == "check_email":
            query = tool_call.get("query", "")
            self.emit('response', {'data': f"Checking emails with query: \"{query}\"...\n\n"})
            result = check_email(query)
        elif tool_name == "list_github_repos":
            self.emit('response', {'data': "Listing GitHub repositories...\n\n"})
            result = list_github_repos()
        elif tool_name == "create_github_issue":
            repo_full_name = tool_call.get("repo_full_name")
            title = tool_call.get("title")
            body = tool_call.get("body", "")
            if repo_full_name and title:
                self.emit('response', {'data': f"Creating issue in {repo_full_name}...\n\n"})
                result = create_github_issue(repo_full_name, title, body)
        elif tool_name == "summarize":
            text = tool_call.get("text")
            if text:
                self.emit('response', {'data': "Summarizing text...\n\n"})
                result = summarize(text)
        elif tool_name == "whois_lookup":
            url = tool_call.get("url")
            if url:
                self.emit('response', {'data': f"Performing WHOIS lookup for {url}...\n\n"})
                result = whois_lookup(url)

        if result:
            if not analyze_tool_output(result):
                self.emit('response', {'data': "\n\n[Security Guardian: Potentially unsafe tool output detected and blocked.]"})
                # We do not append the unsafe result to history or process it further.
                return

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

class TerminalNamespace(Namespace):
    def on_connect(self):
        print(f'Terminal client connected: {request.sid}')
        # Start a new pty process for the session
        pid, fd = ptyprocess.fork()
        if pid == 0:
            # Child process
            os.execv('/bin/bash', ['/bin/bash'])
        else:
            # Parent process
            ptys[request.sid] = fd
            # Start a thread to read from the pty and forward to the client
            threading.Thread(target=self.read_and_forward, args=[request.sid, fd]).start()

    def on_disconnect(self):
        print(f'Terminal client disconnected: {request.sid}')
        if request.sid in ptys:
            os.close(ptys[request.sid])
            del ptys[request.sid]

    def on_terminal_in(self, data):
        if request.sid in ptys:
            os.write(ptys[request.sid], data.encode())

    def read_and_forward(self, sid, fd):
        """Reads from the pty and forwards to the client."""
        while True:
            try:
                data = os.read(fd, 1024).decode()
                if data:
                    self.emit('terminal_out', {'data': data}, to=sid)
                else:
                    # PTY has been closed
                    break
            except OSError:
                break

socketio.on_namespace(ChatNamespace('/chat'))
socketio.on_namespace(TerminalNamespace('/terminal'))

@app.route('/api/workflows/plan', methods=['POST'])
def plan_workflow_route():
    data = request.get_json()
    description = data.get('description')
    if not description:
        return jsonify({'error': 'No description provided'}), 400

    try:
        planner_prompt = prompt_manager.render_prompt(
            'workflow_planner.poml',
            {'description': description}
        )

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

def sandbox_process_text(text: str) -> str:
    """
    A placeholder for a future sandboxing feature.
    For now, it just logs and returns the text.
    """
    print(f"[SANDBOX] Processing text in sandbox...")
    # In the future, this could involve running analysis in a container or subprocess.
    return text

security_rag = SecurityRAGManager()

def update_security_rag_from_rss():
    """
    Fetches latest stories from RSS feeds, verifies their source, processes
    them in a sandbox, and adds them to the security RAG.
    """
    print("Fetching RSS stories for security RAG...")
    stories = fetch_stories_from_rss(
        feed_urls=SECURITY_RSS_FEEDS,
        whois_lookup_func=whois_lookup,
        sandbox_func=sandbox_process_text
    )
    if stories:
        security_rag.add_texts(stories)
        print(f"Added {len(stories)} new stories to the security RAG.")

def seed_good_code_rag():
    """
    Scans the good_code_examples directory and adds the content of each
    file to the security RAG. This is a one-time operation.
    """
    if ltm_manager.recall("good_code_seeded") == "True":
        print("Good code examples already seeded in Security RAG.")
        return

    print("Seeding Security RAG with good code examples...")
    code_examples_dir = "good_code_examples"
    all_code_texts = []

    if not os.path.exists(code_examples_dir):
        print(f"Directory not found: {code_examples_dir}")
        return

    for filename in os.listdir(code_examples_dir):
        if filename.endswith(".py"):
            file_path = os.path.join(code_examples_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                all_code_texts.append(f.read())

    if all_code_texts:
        security_rag.add_texts(all_code_texts)
        ltm_manager.remember("good_code_seeded", "True")
        print(f"Successfully seeded {len(all_code_texts)} good code examples.")

def perform_self_analysis():
    """
    Performs a self-analysis of the agent's own code by checking it
    against good code examples in the security RAG.
    """
    print("[SELF-ANALYSIS] Starting self-analysis cycle.")
    files_to_analyze = ["app.py", "prompt_manager.py", "security_prompt_manager.py"]

    for filename in files_to_analyze:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file_content = f.read()

            # Use the file content to find relevant good code examples
            rag_context = "\n---\n".join(security_rag.search(file_content, k=3))

            analysis_prompt = security_prompt_manager.render_prompt(
                'code_analysis',
                {
                    'file_content': file_content,
                    'rag_context': rag_context
                }
            )

            # Use the local LLM for the analysis.
            analysis_result = local_llm.generate(analysis_prompt).strip()

            if "NO ISSUES FOUND" not in analysis_result.upper():
                print(f"[SELF-ANALYSIS] Potential issues found in {filename}:\n{analysis_result}")
                # Trigger the 5-day observation mode
                ltm_manager.set_observation_mode(5)
            else:
                print(f"[SELF-ANALYSIS] No issues found in {filename}.")

        except FileNotFoundError:
            print(f"[SELF-ANALYSIS] Could not find file {filename} to analyze.")
        except Exception as e:
            print(f"[SELF-ANALYSIS] An error occurred during analysis of {filename}: {e}")

if __name__ == '__main__':
    # Perform one-time seeding of the security RAG with good code examples.
    seed_good_code_rag()

    # Define the tools available to the workflow engine
    workflow_tools = {
        "log_message": log_message,
        "check_email": check_email,
        "list_github_repos": list_github_repos,
        "create_github_issue": create_github_issue,
        "summarize": summarize,
        "create_backup": lambda: create_backup(None), # The workflow doesn't have a sid
        "remember": remember,
        "recall": recall,
        "whois_lookup": whois_lookup
    }

    # Initialize the workflow engine
    workflow_engine = WorkflowEngine(tools=workflow_tools)

    # Schedule the threat intelligence gathering job
    workflow_engine.scheduler.add_job(
        update_security_rag_from_rss,
        'interval',
        hours=1,
        id='update_rss_stories',
        replace_existing=True
    )

    # Schedule the self-analysis job to run daily at 2 AM
    workflow_engine.scheduler.add_job(
        perform_self_analysis,
        'cron',
        hour=2,
        minute=0,
        id='self_analysis_job',
        replace_existing=True
    )

    # Start the workflow engine (which also starts the scheduler)
    workflow_engine.start()

    # Use allow_unsafe_werkzeug=True for development with Flask 2.3+ and Socket.IO
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
