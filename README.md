# VA21 Omni Agent - Digital Fortress

## 🔒 Security-First AI-Powered Desktop Environment

The VA21 Omni Agent represents a revolutionary approach to secure AI interaction, implementing a "digital fortress" philosophy where user safety and privacy are paramount.

![VA21 Interface](https://github.com/user-attachments/assets/a6013877-03bd-40c1-8bb5-d41e3385f1da)

## 🛡️ Core Security Architecture

### Dual-AI System
- **Guardian AI (Security Core)**: Always-active security analysis using ONNX models
- **Orchestrator AI**: User-facing reasoning engine with flexible LLM integration
- **Air Gap Protection**: Complete isolation from screen content and sensitive data
- **Principle of Least Privilege**: No direct website interactions or form submissions

### Security Features
- ✅ **Real-time Threat Analysis**: Every input analyzed before processing
- ✅ **Self-Analysis & Healing**: Autonomous code security scanning
- ✅ **5-Day Quarantine Protocol**: Safe integration of external intelligence
- ✅ **Localhost-Only Operation**: No external network exposure
- ✅ **Pattern-Based Detection**: Advanced malware and injection detection

## 🔬 Research Command Center

The VA21 Research Command Center is a researcher's dream environment featuring:

### Multiple Sandboxed Terminals
- **Tiling Window Management**: Run multiple terminal sessions with quad, triple, or six-pane layouts
- **Isolation Levels**: Minimal, Standard, and Strict sandbox levels for different security needs
- **Session Logging**: All terminal activity logged to the knowledge vault
- **Security Controls**: Blocked dangerous commands and restricted paths

### Obsidian-Style Knowledge Vault
- **Wiki-Style Links**: Create interconnected notes with `[[link]]` syntax
- **Knowledge Graph**: Visual representation of your research connections
- **LLM Memory Integration**: Persistent memory for AI context
- **Research Sessions**: Organized research with objectives and findings
- **Tag-Based Organization**: Easily categorize and find research

### Sensitive Information Protection
- **Automatic Redaction**: Detect and redact API keys, passwords, tokens, and more
- **Category-Based Filtering**: Control what gets redacted (credentials, PII, network info)
- **Audit Logging**: Track all redactions for security compliance
- **Consistent Replacement**: Hash-based replacement for pattern tracking

## 🚀 Quick Installation

### One-Line Install (Linux/macOS)
```bash
curl -fsSL https://raw.githubusercontent.com/narasimhudumeetsworld/va21/main/install.sh | bash
```

### Docker Installation
```bash
cd va21-omni-agent
docker-compose up -d
```

Access the interface at: **http://localhost:5000**

### Manual Installation
```bash
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21
chmod +x install.sh
./install.sh
```

### Launch
```bash
cd ~/va21-omni-agent  # or your installation directory
./va21-launcher.sh    # Linux/macOS
# or
va21-launcher.bat     # Windows
```

## 📋 System Requirements

- **Python 3.8+** (for portable environment)
- **2GB RAM minimum** (4GB recommended)
- **1GB disk space** (for models and dependencies)
- **Internet connection** (initial setup only)
- **Docker** (optional, for containerized deployment)

## 🎯 Key Capabilities

### Enhanced Orchestrator AI
- Multi-agent coordination for complex tasks
- Task queue management with priorities
- Dependency resolution between tasks
- Self-healing error recovery
- Context sharing between agents

### RSS Threat Intelligence Feeds
- Integration with security blogs (Google, Microsoft, Project Zero)
- Zero-trust domain verification
- Sandboxed content processing
- Automatic RAG indexing for security context

### Advanced Self-Healing
- Multiple health check strategies
- Automatic recovery actions
- System integrity verification
- State snapshots and rollback
- Anomaly detection and alerting

### Security Scanner
- Real-time analysis of text, code, and commands
- Malicious pattern detection (eval, exec, shell commands)
- Suspicious content identification (passwords, tokens, URLs)

### Self-Analysis System
- Automated daily security self-scans
- Manual trigger for immediate analysis
- System health monitoring and alerts
- Lockdown mode for critical issues

### Secure Chat Interface
- Guardian AI pre-screening of all messages
- Threat blocking and user notification
- Air-gapped browser simulation
- Real-time security status display

## 🏗️ Technical Implementation

### Architecture
- **Backend**: Flask + Socket.IO Python server
- **Frontend**: React.js security dashboard
- **Guardian AI**: ONNX-based local inference with simulation fallback
- **Security**: Multiple layers of protection and monitoring
- **Deployment**: Docker-ready with health checks

### Files Structure
```
va21-omni-agent/
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── local_llm.py                # Guardian AI implementation
│   ├── enhanced_orchestrator.py    # Multi-agent coordination
│   ├── obsidian_vault_manager.py   # Knowledge graph & memory
│   ├── sandboxed_terminal_manager.py # Multiple terminals
│   ├── sensitive_info_redactor.py  # Data protection
│   ├── advanced_self_healing.py    # System recovery
│   ├── research_command_center.py  # API & Socket.IO namespaces
│   └── threat_intelligence.py      # RSS security feeds
├── frontend/
│   └── src/components/
│       ├── ResearchCommandCenter.js # Research UI
│       ├── TilingTerminals.js       # Terminal tiling
│       └── ...
├── Dockerfile                       # Container build
├── docker-compose.yml               # Easy deployment
├── install.sh                       # Automated installer
├── va21-launcher.sh                 # Unix launcher
└── va21-launcher.bat                # Windows launcher
```

## 🔧 Advanced Features

### Portable Environment
- Self-contained Python environment
- All dependencies bundled
- Cross-platform compatibility
- No system Python conflicts

### Security Monitoring
- Background threat intelligence gathering
- Automated security updates
- System integrity verification
- Emergency lockdown capabilities

### Docker Deployment
```yaml
# Quick start with Docker
docker-compose up -d

# View logs
docker-compose logs -f va21-research-center

# Stop
docker-compose down
```

## 🛡️ Security Guarantees

1. **Air Gap Isolation**: No access to live screen content or sensitive data
2. **Local Processing**: All AI inference happens locally or in simulation
3. **Quarantine Protocol**: External data undergoes 5-day security review
4. **Self-Monitoring**: Continuous analysis of own security posture
5. **Principle of Least Privilege**: Minimal permissions and capabilities
6. **Sensitive Data Redaction**: Automatic protection of credentials and PII

## 📞 Support & Documentation

- **Repository**: https://github.com/narasimhudumeetsworld/va21
- **Issues**: https://github.com/narasimhudumeetsworld/va21/issues
- **Security**: Report security issues via GitHub Issues with "Security" label

## 📄 License

This project is licensed under the Prayaga Vaibhav Proprietary License - All Rights Reserved.
Protected under comprehensive intellectual property terms covering 218+ inventions.
See the full license terms at: https://github.com/narasimhudumeetsworld/Om-vinayaka-prayaga-vaibhav-inventions-Copy-Right-License/blob/main/LICENSE

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.

---

**⚠️ Security Notice**: VA21 Omni Agent is designed as a security-first system. Always keep your installation updated and report any suspicious behavior through our GitHub repository.
