import requests
import json
import argparse
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
from github_code_fetcher import fetch_repo_contents # Import the new fetcher
from local_llm import LocalLLM
import whois
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

settings = {}

def load_settings(settings_path):
    global settings
    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
        else:
            settings = { "provider": "ollama", "url": "http://localhost:11434", "github_pat": "", "github_repo": "" }
    except Exception:
        settings = { "provider": "ollama", "url": "http://localhost:11434", "github_pat": "", "github_repo": "" }

histories = {}
ptys = {}

# --- RAG Manager Instances ---
rag_manager = RAGManager() # For general user chat
security_rag = SecurityRAGManager() # For good code examples and threat intel
repo_rag_manager = RAGManager(db_path="faiss_repo_db") # Dedicated RAG for user's repo code

ltm_manager = LongTermMemoryManager()
prompt_manager = PromptManager()
security_prompt_manager = SecurityPromptManager()
local_llm = LocalLLM()

# ... (core logic functions remain the same) ...

# --- New function to update the repository RAG ---
def update_repo_rag_from_github():
    """
    Fetches the latest code from the user's specified GitHub repository
    and updates a dedicated RAG index with its content.
    """
    print("[RepoSync] Starting GitHub repository sync...")
    repo_name = settings.get("github_repo")
    github_pat = settings.get("github_pat")

    if not repo_name or not github_pat:
        print("[RepoSync] GitHub repository name or PAT not configured in settings. Skipping sync.")
        return

    all_files = fetch_repo_contents(repo_name, github_pat)
    if all_files:
        # We are overwriting the RAG index each time to ensure it's fresh.
        # For very large repos, a more sophisticated update strategy might be needed.
        print(f"[RepoSync] Creating new RAG index for {len(all_files)} files...")
        texts = list(all_files.values())
        repo_rag_manager.create_new_index(texts)
        print("[RepoSync] Successfully updated repository RAG index.")
    else:
        print("[RepoSync] Failed to fetch repository contents.")


# ... (perform_self_analysis can now be expanded to use repo_rag_manager) ...

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VA21 Omni Agent Backend")
    parser.add_argument('--settings_path', type=str, required=True, help='Path to the settings JSON file.')
    args = parser.parse_args()

    load_settings(args.settings_path)

    seed_good_code_rag()

    workflow_tools = { # ... (tools remain the same) ...
    }

    workflow_engine = WorkflowEngine(tools=workflow_tools)

    # Schedule existing jobs
    workflow_engine.scheduler.add_job(update_security_rag_from_rss, 'interval', hours=1, id='update_rss_stories', replace_existing=True)
    workflow_engine.scheduler.add_job(perform_self_analysis, 'cron', hour=2, minute=0, id='self_analysis_job', replace_existing=True)

    # Schedule the new job for syncing the user's repo
    workflow_engine.scheduler.add_job(update_repo_rag_from_github, 'interval', hours=4, id='update_repo_rag', replace_existing=True)

    workflow_engine.start()

    # Run initial sync on startup
    update_repo_rag_from_github()

    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)

# NOTE: For brevity, the repeated functions from the original file are not included here.
# The final file should merge these changes with the existing, unchanged functions.
def analyze_tool_output(output: str) -> bool:
    if not output: return True
    print("--- Running Security Guardian Analysis ---")
    try:
        guardian_prompt = security_prompt_manager.render_prompt('security_guardian', {'tool_output': str(output)})
        analysis_result = local_llm.generate(guardian_prompt).strip().upper()
        print(f"Security Guardian Result: {analysis_result}")
        return not analysis_result.startswith("UNSAFE")
    except Exception as e:
        print(f"Error during security analysis: {e}")
        return False
def perform_web_search(query):
    try:
        results = DDGS().text(query, max_results=5)
        return "\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
    except Exception as e:
        return f"Error performing web search: {e}"
def create_backup(sid):
    backup_manager = BackupManager(settings)
    history = histories.get(sid, [])
    ltm = ltm_manager.get_all()
    backup_data = { "conversation_history": history, "long_term_memory": ltm }
    file_name = f"omni_agent_backup_{sid}"
    return backup_manager.backup(backup_data, file_name)
def remember(key, value):
    return ltm_manager.remember(key, value)
def recall(key):
    return ltm_manager.recall(key)
def check_email(query=""):
    gmail_manager = GmailManager()
    return gmail_manager.check_email(query)
def list_github_repos():
    github_manager = GitHubManager(settings.get("github_pat"))
    return github_manager.list_repos()
def create_github_issue(repo_full_name, title, body=""):
    github_manager = GitHubManager(settings.get("github_pat"))
    return github_manager.create_issue(repo_full_name, title, body)
def summarize(text):
    prompt = f"Please summarize the following text:\n\n{text}"
    try:
        response = get_llm_response([{"role": "user", "content": prompt}], stream=False)
        return response.get("message", {}).get("content", "")
    except Exception as e:
        return f"Error summarizing text: {e}"
def whois_lookup(url: str):
    try:
        domain = urlparse(url).netloc
        if not domain: return "Error: Could not parse domain from URL."
        w = whois.whois(domain)
        return f"Domain: {w.domain_name}\nRegistrar: {w.registrar}\nCreation Date: {w.creation_date}\nExpiration Date: {w.expiration_date}\nEmails: {w.emails}"
    except Exception as e:
        return f"Error performing WHOIS lookup: {e}"
def get_ollama_response(history, stream=False):
    url = f"{settings['url']}/api/chat"
    headers = {'Authorization': f"Bearer {settings['api_key']}"} if settings.get('api_key') else {}
    response = requests.post(url, headers=headers, json={"model": "gemma:2b", "messages": history, "stream": stream}, stream=stream)
    response.raise_for_status()
    return response
def get_gemini_response(history, stream=False):
    try:
        model = genai.GenerativeModel('gemini-pro')
        gemini_history = [{"role": "model" if msg["role"] == "assistant" else msg["role"], "parts": [{"text": msg["content"]}]} for msg in history if msg["role"] in ["user", "model"]]
        response = model.generate_content(gemini_history, stream=stream)
        if stream:
            class GeminiStreamWrapper:
                def __init__(self, stream): self.stream = stream
                def iter_lines(self):
                    for chunk in self.stream: yield json.dumps({"message": {"content": chunk.text}, "done": False}).encode('utf-8')
                    yield json.dumps({"message": {"content": ""}, "done": True}).encode('utf-8')
                def raise_for_status(self): pass
            return GeminiStreamWrapper(response)
        else:
            return {"message": {"content": response.text}}
    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return {"error": str(e)}
def get_llm_response(history, stream=False):
    provider = settings.get("provider", "ollama")
    if provider in ["ollama", "authenticated_ollama"]:
        response = get_ollama_response(history, stream)
        return response if stream else response.json()
    elif provider == "gemini":
        return get_gemini_response(history, stream)
    return None
class ChatNamespace(Namespace):
    def on_connect(self):
        system_prompt = prompt_manager.render_prompt('system_prompt.poml')
        histories[request.sid] = [{"role": "system", "content": system_prompt}]
        print(f'Chat client connected: {request.sid}')
        self.emit('response', {'data': 'Connected to server'})
    def on_disconnect(self):
        if request.sid in histories: del histories[request.sid]
        print(f'Chat client disconnected: {request.sid}')
    def _handle_tool_call(self, tool_call, current_history):
        intervention_url = ltm_manager.get_awaiting_intervention_url()
        if intervention_url:
            self.emit('response', {'data': f"\n\n[INTERVENTION REQUIRED]: I am blocked pending review of a critical issue. Please see: {intervention_url}"})
            return

        if ltm_manager.is_in_lockdown_mode():
            self.emit('response', {'data': "\n\n[LOCKDOWN MODE]: All agent actions are disabled due to a critical security alert."})
            return
        if ltm_manager.is_in_observation_mode(): self.emit('response', {'data': "\n\n[OBSERVATION MODE]: Agent is in a 5-day observation period..."})
        tool_name = tool_call.get("tool")
        result = None
        if tool_name == "resolve_intervention":
            ltm_manager.set_awaiting_intervention(None)
            result = "Intervention flag cleared. I can now proceed."
        elif result:
            if not analyze_tool_output(result):
                self.emit('response', {'data': "\n\n[Security Guardian: Potentially unsafe tool output detected and blocked.]"})
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
            if search_results: current_history.insert(-1, {"role": "system", "content": f"Context: {' '.join(search_results)}"})
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
                if "tool" in tool_call: self._handle_tool_call(tool_call, current_history)
                else: self.emit('response', {'data': full_response})
            except json.JSONDecodeError:
                self.emit('response', {'data': full_response})
        except Exception as e:
            print(f"Error during LLM call: {e}")
            self.emit('response', {'data': f"Error: {e}"})
            if current_history: current_history.pop()
class TerminalNamespace(Namespace):
    def on_connect(self):
        pid, fd = ptyprocess.fork()
        if pid == 0: os.execv('/bin/bash', ['/bin/bash'])
        else:
            ptys[request.sid] = fd
            threading.Thread(target=self.read_and_forward, args=[request.sid, fd]).start()
    def on_disconnect(self):
        if request.sid in ptys:
            os.close(ptys[request.sid])
            del ptys[request.sid]
    def on_terminal_in(self, data):
        if request.sid in ptys: os.write(ptys[request.sid], data.encode())
    def read_and_forward(self, sid, fd):
        while True:
            try:
                data = os.read(fd, 1024).decode()
                if data: self.emit('terminal_out', {'data': data}, to=sid)
                else: break
            except OSError: break
def sandbox_process_text(text: str) -> str:
    print(f"[SANDBOX] Processing text in sandbox...")
    return text
def update_security_rag_from_rss():
    print("Fetching RSS stories for security RAG...")
    stories = fetch_stories_from_rss(feed_urls=SECURITY_RSS_FEEDS, whois_lookup_func=whois_lookup, sandbox_func=sandbox_process_text)
    if stories:
        security_rag.add_texts(stories)
        print(f"Added {len(stories)} new stories to the security RAG.")
def seed_good_code_rag():
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
    print("[SELF-ANALYSIS] Starting self-analysis cycle.")
    files_to_analyze = ["app.py", "prompt_manager.py", "security_prompt_manager.py"]
    for filename in files_to_analyze:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file_content = f.read()
            rag_context = "\n---\n".join(security_rag.search(file_content, k=3))
            analysis_prompt = security_prompt_manager.render_prompt('code_analysis', {'file_content': file_content, 'rag_context': rag_context})
            analysis_result = local_llm.generate(analysis_prompt).strip()
            if "NO ISSUES FOUND" not in analysis_result.upper():
                print(f"[SELF-ANALYSIS] Potential issues found in {filename}:\n{analysis_result}")
                if filename == 'app.py':
                    print("[SELF-ANALYSIS] Critical issue found in app.py. Activating lockdown and requesting intervention.")
                    ltm_manager.set_lockdown_mode(True)

                    # Create GitHub issue
                    repo_name = settings.get("github_repo")
                    if repo_name:
                        issue_title = f"Guardian Alert: Critical Issue Detected in {filename}"
                        issue_body = f"The Guardian AI has detected a potential critical issue during self-analysis.\n\n**File:** `{filename}`\n\n**Guardian's Analysis:**\n```\n{analysis_result}\n```\n\nThe agent is now in lockdown mode and awaits human intervention."
                        issue_url = create_github_issue(repo_name, issue_title, issue_body)
                        if issue_url:
                            ltm_manager.set_awaiting_intervention(issue_url)
                else:
                    ltm_manager.set_observation_mode(5)
            else:
                print(f"[SELF-ANALYSIS] No issues found in {filename}.")
        except FileNotFoundError:
            print(f"[SELF-ANALYSIS] Could not find file {filename} to analyze.")
        except Exception as e:
            print(f"[SELF-ANALYSIS] An error occurred during analysis of {filename}: {e}")
def log_message(message):
    print(f"WORKFLOW LOG: {message}")
