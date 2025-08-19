import subprocess
import os
import threading
import git
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ollama
from mitmproxy import http, options
from mitmproxy.tools.dump import DumpMaster

WATCH_PATH = "./chromium_src"
CLANG_TIDY_PATH = "/opt/homebrew/opt/llvm/bin/clang-tidy"

class CodeHealHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.cc') or event.src_path.endswith('.h'):
            run_clang_tidy(event.src_path)

def run_clang_tidy(target_file):
    print(f"[HEALER] Analysing: {target_file}")
    result = subprocess.run(
        [CLANG_TIDY_PATH, target_file, "--"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        print("[HEALER] clang-tidy warnings found, creating LLM patch prompt.")
        with open(target_file, 'r') as src:
            file_content = src.read()
        prompt = (
            "Bug Fixing Context:\n"
            f"File: {target_file}\n"
            f"Warnings:\n{result.stdout}\n"
            "File Content:\n"
            f"{file_content}\n"
            "Please generate a unified diff patch (.patch format) that resolves the clang-tidy warnings."
        )
        patch = ollama.Chat(model="codellama:7b-q4_0", messages=[{"role": "user", "content": prompt}])['message']['content']
        with open("llm_patch.patch", "w") as pf:
            pf.write(patch)
        test_and_commit_patch(target_file, "llm_patch.patch")
    else:
        print("[HEALER] No issues found.")

def test_and_commit_patch(target_file, patch_file):
    print("[HEALER] Testing patch in sandbox...")
    test_dir = "./healing_sandbox"
    os.makedirs(test_dir, exist_ok=True)
    subprocess.run(["cp", target_file, test_dir], check=True)
    subprocess.run(["cp", patch_file, test_dir], check=True)
    sandbox_profile = '(version 1)\n(deny default)\n(allow file-read* file-write* (regex "^' + test_dir + '"))\n(allow process-exec (regex "^/usr/bin/clang.*"))\n'
    with open("sandbox.profile", "w") as sb:
        sb.write(sandbox_profile)
    sandboxed_cmd = f"""
    cd {test_dir}
    patch < llm_patch.patch
    /usr/bin/sandbox-exec -f ../sandbox.profile clang++ {target_file}
    """
    proc = subprocess.run(["/bin/bash", "-c", sandboxed_cmd], capture_output=True)
    if proc.returncode == 0:
        print("[HEALER] Patch passed sandboxed build, committing to git.")
        repo = git.Repo('./')
        repo.git.add(target_file)
        repo.git.commit('-m', f"[auto-fix] Applied patch fixing clang-tidy warnings in {target_file}")
    else:
        print("[HEALER] Patch failed tests; NOT applied.\n", proc.stderr.decode())

def start_code_healer():
    event_handler = CodeHealHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    print("[HEALER] Code healing daemon is monitoring source changes...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

class TrafficAddon:
    def request(self, flow: http.HTTPFlow):
        suspect = any([
            "eval(" in flow.request.text if flow.request.text else False,
            len(flow.request.text) > 10000 if flow.request.text else False,
        ])
        if suspect:
            analysis = ollama.Chat(model="codellama:7b-q4_0", messages=[
                {"role": "user", "content": f"Is the following HTTP request payload malicious? Respond only with 'YES' or 'NO'.\n{flow.request.text}"}
            ])['message']['content'].strip()
            if analysis.upper() == "YES":
                print("[GUARDIAN] Malicious request blocked!")
                flow.response = http.HTTPResponse.make(200, b"Blocked for security", {})
                return

def start_traffic_guardian():
    opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
    m = DumpMaster(opts)
    m.addons.add(TrafficAddon())
    print("[GUARDIAN] Real-time traffic inspection proxy running on localhost:8080.")
    m.run()

def main():
    th_healer = threading.Thread(target=start_code_healer)
    th_proxy = threading.Thread(target=start_traffic_guardian)
    th_healer.start()
    th_proxy.start()
    th_healer.join()
    th_proxy.join()

if __name__ == "__main__":
    main()
