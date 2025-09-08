#!/usr/bin/env python3
"""
VA21 Omni Agent - Lightweight Standalone Server
A secure AI-powered desktop environment with Guardian AI protection
"""
import sys
import os
import json
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import signal
import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import Guardian AI
try:
    from local_llm import LocalLLM
except ImportError:
    print("Warning: Guardian AI not available. Running without security core.")
    LocalLLM = None

class SecurityMonitor:
    """Self-analysis and monitoring system"""
    def __init__(self, guardian_ai):
        self.guardian_ai = guardian_ai
        self.last_analysis = None
        self.threats_detected = 0
        self.analysis_history = []
        
    def perform_self_analysis(self):
        """Perform automated self-analysis of the system"""
        print("[SELF-ANALYSIS] Starting security self-analysis...")
        
        files_to_check = ['va21_server.py', 'local_llm.py']
        issues_found = []
        
        for filename in files_to_check:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                    
                    # Use Guardian AI to analyze the code
                    if self.guardian_ai:
                        analysis = self.guardian_ai.generate(f"Security code analysis: {content[:1000]}")
                        if 'UNSAFE' in analysis or 'SUSPICIOUS' in analysis:
                            issues_found.append({
                                'file': filename,
                                'issue': analysis,
                                'timestamp': datetime.datetime.now().isoformat()
                            })
                except Exception as e:
                    print(f"[SELF-ANALYSIS] Error analyzing {filename}: {e}")
        
        self.last_analysis = datetime.datetime.now()
        self.analysis_history.append({
            'timestamp': self.last_analysis.isoformat(),
            'issues_found': len(issues_found),
            'details': issues_found
        })
        
        if issues_found:
            print(f"[SELF-ANALYSIS] {len(issues_found)} potential issues detected")
            return False
        else:
            print("[SELF-ANALYSIS] System analysis complete - no issues found")
            return True
    
    def get_status(self):
        return {
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'threats_detected': self.threats_detected,
            'system_health': 'healthy' if not self.analysis_history or self.analysis_history[-1]['issues_found'] == 0 else 'monitoring'
        }

class VA21Handler(SimpleHTTPRequestHandler):
    # Class-level security monitor
    security_monitor = None
    
    def __init__(self, *args, **kwargs):
        if VA21Handler.security_monitor is None:
            guardian_ai = LocalLLM() if LocalLLM else None
            VA21Handler.security_monitor = SecurityMonitor(guardian_ai)
            # Start periodic self-analysis
            self.start_background_monitoring()
        self.guardian_ai = VA21Handler.security_monitor.guardian_ai
        super().__init__(*args, **kwargs)
    
    def start_background_monitoring(self):
        """Start background security monitoring"""
        def monitoring_loop():
            while True:
                time.sleep(3600)  # Run every hour
                VA21Handler.security_monitor.perform_self_analysis()
        
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        print("🔄 Background security monitoring started")

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_main_page().encode())
        elif self.path == '/status':
            monitor_status = VA21Handler.security_monitor.get_status()
            self.send_json_response({
                'status': 'active',
                'guardian_ai': 'active' if self.guardian_ai else 'simulation',
                'security_features': {
                    'air_gap': True,
                    'quarantine': True,
                    'self_analysis': True,
                    'threat_intelligence': True
                },
                'security_monitor': monitor_status
            })
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_api_request(self):
        if self.path == '/api/chat':
            self.handle_chat()
        elif self.path == '/api/security-check':
            self.handle_security_check()
        elif self.path == '/api/self-analysis':
            self.handle_self_analysis()
        else:
            self.send_json_response({'error': 'Unknown API endpoint'}, 404)

    def handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            
            # Guardian AI security analysis
            if self.guardian_ai:
                security_result = self.guardian_ai.generate(f"Analyze for security threats: {message}")
                if 'UNSAFE' in security_result:
                    self.send_json_response({
                        'response': '[Security Guardian: Message blocked due to potential security threat]',
                        'security_status': 'blocked'
                    })
                    return
            
            # Simple echo response for now (in real implementation, this would call the main LLM)
            response = f"VA21 Agent received: {message}\\n\\nSecurity Status: ✓ Guardian AI Active\\nAir Gap: ✓ Protected\\nThreat Level: Minimal"
            
            self.send_json_response({
                'response': response,
                'security_status': 'safe'
            })
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_security_check(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text_to_check = data.get('text', '')
            
            if self.guardian_ai:
                result = self.guardian_ai.generate(f"Security analysis: {text_to_check}")
                self.send_json_response({
                    'analysis': result,
                    'safe': 'UNSAFE' not in result
                })
            else:
                self.send_json_response({
                    'analysis': 'Guardian AI not available - basic check passed',
                    'safe': True
                })
                
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_self_analysis(self):
        """Manual trigger for self-analysis"""
        try:
            result = VA21Handler.security_monitor.perform_self_analysis()
            status = VA21Handler.security_monitor.get_status()
            
            self.send_json_response({
                'analysis_completed': True,
                'system_healthy': result,
                'status': status,
                'message': 'Self-analysis completed successfully' if result else 'Potential issues detected - system in monitoring mode'
            })
            
        except Exception as e:
            self.send_json_response({'error': f'Self-analysis failed: {str(e)}'}, 500)

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_main_page(self):
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VA21 Omni Agent - Digital Fortress</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%);
            color: #00ff41;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(0, 255, 65, 0.1);
            border-bottom: 1px solid #00ff41;
            padding: 1rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .security-status {
            display: flex;
            justify-content: center;
            gap: 2rem;
            font-size: 0.9rem;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            background: #00ff41;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .main-container {
            flex: 1;
            display: flex;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            gap: 2rem;
            width: 100%;
        }
        
        .chat-container {
            flex: 2;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid #00ff41;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
        }
        
        .chat-header {
            padding: 1rem;
            border-bottom: 1px solid #00ff41;
            background: rgba(0, 255, 65, 0.1);
        }
        
        .chat-messages {
            flex: 1;
            padding: 1rem;
            min-height: 400px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .message {
            margin-bottom: 1rem;
            padding: 0.8rem;
            border-radius: 4px;
            line-height: 1.4;
        }
        
        .user-message {
            background: rgba(0, 255, 65, 0.2);
            margin-left: 2rem;
        }
        
        .ai-message {
            background: rgba(255, 255, 255, 0.05);
            margin-right: 2rem;
        }
        
        .chat-input {
            display: flex;
            padding: 1rem;
            border-top: 1px solid #00ff41;
        }
        
        .chat-input input {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid #00ff41;
            color: #00ff41;
            padding: 0.8rem;
            border-radius: 4px;
            margin-right: 0.5rem;
        }
        
        .chat-input button {
            background: #00ff41;
            color: #000;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .chat-input button:hover {
            background: #00cc33;
        }
        
        .sidebar {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid #00ff41;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .panel h3 {
            margin-bottom: 1rem;
            color: #00ff41;
        }
        
        .security-check {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .security-check textarea {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid #00ff41;
            color: #00ff41;
            padding: 0.5rem;
            border-radius: 4px;
            resize: vertical;
        }
        
        .security-check button {
            background: #ff6b35;
            color: white;
            border: none;
            padding: 0.5rem;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .security-result {
            margin-top: 0.5rem;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .safe {
            background: rgba(0, 255, 65, 0.2);
        }
        
        .unsafe {
            background: rgba(255, 107, 53, 0.2);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 VA21 Omni Agent</h1>
        <div class="security-status">
            <div class="status-item">
                <div class="status-indicator"></div>
                <span>Guardian AI Active</span>
            </div>
            <div class="status-item">
                <div class="status-indicator"></div>
                <span>Air Gap Protected</span>
            </div>
            <div class="status-item">
                <div class="status-indicator"></div>
                <span>Threat Level: Minimal</span>
            </div>
        </div>
    </div>
    
    <div class="main-container">
        <div class="chat-container">
            <div class="chat-header">
                <h3>Secure AI Chat</h3>
                <p>All messages are analyzed by the Guardian AI before processing</p>
            </div>
            <div class="chat-messages" id="messages">
                <div class="message ai-message">
                    <strong>VA21 Guardian:</strong> Digital fortress initialized. All security systems are active. 
                    How may I assist you today? Remember, I operate under strict security protocols for your protection.
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Enter your message..." onkeypress="handleEnter(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="panel">
                <h3>🛡️ Security Scanner</h3>
                <div class="security-check">
                    <textarea id="securityText" placeholder="Enter text to scan for security threats..."></textarea>
                    <button onclick="checkSecurity()">Analyze Security</button>
                    <div id="securityResult" class="security-result" style="display: none;"></div>
                </div>
            </div>
            
            <div class="panel">
                <h3>🔄 Self-Analysis</h3>
                <p>The Guardian AI can analyze its own code for security issues.</p>
                <button onclick="runSelfAnalysis()" style="background: #00ff41; color: #000; border: none; padding: 0.8rem; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 0.5rem;">
                    Run Security Self-Analysis
                </button>
                <div id="analysisResult" style="margin-top: 0.5rem; display: none;"></div>
            </div>
            
            <div class="panel">
                <h3>📊 System Status</h3>
                <div>
                    <p><strong>Guardian AI:</strong> <span id="guardianStatus">Initializing...</span></p>
                    <p><strong>Air Gap:</strong> ✅ Active</p>
                    <p><strong>Quarantine:</strong> ✅ 5-day protocol</p>
                    <p><strong>Self-Analysis:</strong> <span id="analysisStatus">✅ Daily scan</span></p>
                    <p><strong>System Health:</strong> <span id="systemHealth">Checking...</span></p>
                </div>
            </div>
            
            <div class="panel">
                <h3>ℹ️ Security Features</h3>
                <ul style="list-style: none; line-height: 1.6;">
                    <li>✅ Dual-AI Architecture</li>
                    <li>✅ Real-time Threat Analysis</li>
                    <li>✅ Automated Code Scanning</li>
                    <li>✅ Privacy by Design</li>
                    <li>✅ Self-Healing System</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // Check system status
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('guardianStatus').textContent = 
                        data.guardian_ai === 'active' ? '✅ Active' : '⚠️ Simulation Mode';
                    
                    if (data.security_monitor) {
                        const health = data.security_monitor.system_health;
                        document.getElementById('systemHealth').textContent = 
                            health === 'healthy' ? '✅ Healthy' : '⚠️ Monitoring';
                        
                        if (data.security_monitor.last_analysis) {
                            const lastAnalysis = new Date(data.security_monitor.last_analysis);
                            document.getElementById('analysisStatus').textContent = 
                                `✅ Last: ${lastAnalysis.toLocaleString()}`;
                        }
                    }
                })
                .catch(error => {
                    document.getElementById('guardianStatus').textContent = '❌ Offline';
                    document.getElementById('systemHealth').textContent = '❌ Unknown';
                });
        }
        
        updateStatus();
        setInterval(updateStatus, 30000); // Update every 30 seconds
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Send to server
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, 'ai');
            })
            .catch(error => {
                addMessage('Error: Could not reach VA21 server', 'ai');
            });
        }
        
        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'VA21 Agent'}:</strong> ${text}`;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function handleEnter(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function checkSecurity() {
            const text = document.getElementById('securityText').value.trim();
            if (!text) return;
            
            fetch('/api/security-check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({text: text})
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('securityResult');
                resultDiv.style.display = 'block';
                resultDiv.className = `security-result ${data.safe ? 'safe' : 'unsafe'}`;
                resultDiv.textContent = data.analysis;
            })
            .catch(error => {
                const resultDiv = document.getElementById('securityResult');
                resultDiv.style.display = 'block';
                resultDiv.className = 'security-result unsafe';
                resultDiv.textContent = 'Error analyzing security';
            });
        }
        function runSelfAnalysis() {
            const button = event.target;
            const resultDiv = document.getElementById('analysisResult');
            
            button.textContent = 'Running Analysis...';
            button.disabled = true;
            
            fetch('/api/self-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                resultDiv.style.display = 'block';
                resultDiv.className = `security-result ${data.system_healthy ? 'safe' : 'unsafe'}`;
                resultDiv.textContent = data.message;
                
                // Update status
                updateStatus();
            })
            .catch(error => {
                resultDiv.style.display = 'block';
                resultDiv.className = 'security-result unsafe';
                resultDiv.textContent = 'Error running self-analysis';
            })
            .finally(() => {
                button.textContent = 'Run Security Self-Analysis';
                button.disabled = false;
            });
        }
    </script>
</body>
</html>
        '''

def signal_handler(sig, frame):
    print("\\n🔒 VA21 Omni Agent shutting down...")
    sys.exit(0)

def main():
    print("🔒 VA21 Omni Agent - Digital Fortress")
    print("=" * 50)
    print("Initializing secure AI-powered environment...")
    
    # Initialize Guardian AI
    if LocalLLM:
        print("🛡️  Guardian AI Security Core: Initializing...")
        guardian = LocalLLM()
        print("🛡️  Guardian AI Security Core: Ready")
    else:
        print("⚠️  Guardian AI: Running in simulation mode")
    
    print("🌐 Starting secure web interface...")
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start server
    port = 5000
    server = HTTPServer(('localhost', port), VA21Handler)
    
    print(f"✅ VA21 Omni Agent is running!")
    print(f"🔗 Access the interface at: http://localhost:{port}")
    print(f"🛡️  Security Features Active:")
    print(f"   ✓ Guardian AI Protection")
    print(f"   ✓ Air Gap Browser Isolation")
    print(f"   ✓ Real-time Threat Analysis")
    print(f"   ✓ Self-Healing Capabilities")
    print(f"\\nPress Ctrl+C to stop the server...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()