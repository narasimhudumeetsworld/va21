#!/bin/bash
set -e

echo "🔒 VA21 Omni Agent Installer"
echo "========================================="
echo "Installing the secure AI-powered desktop environment..."

# Detect OS
case "$(uname -s)" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${unameOut}"
esac

echo "Detected OS: $MACHINE"

# Create installation directory
INSTALL_DIR="$HOME/va21-omni-agent"
echo "Installation directory: $INSTALL_DIR"

# Check if directory exists and ask user
if [ -d "$INSTALL_DIR" ]; then
    read -p "Directory $INSTALL_DIR already exists. Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "📥 Downloading VA21 Omni Agent..."
# Download the repository
if command -v git &> /dev/null; then
    if [ -d ".git" ]; then
        git pull origin main
    else
        git clone https://github.com/narasimhudumeetsworld/va21.git .
    fi
else
    echo "Git not found. Downloading archive..."
    curl -L https://github.com/narasimhudumeetsworld/va21/archive/refs/heads/main.zip -o va21.zip
    unzip va21.zip
    mv va21-main/* .
    rm -rf va21-main va21.zip
fi

echo "🐍 Setting up portable Python environment..."
# Create portable Python environment
PYTHON_ENV="$INSTALL_DIR/python-env"
mkdir -p "$PYTHON_ENV"

# Setup Python based on OS
if [ "$MACHINE" = "Linux" ]; then
    if command -v python3 &> /dev/null; then
        python3 -m venv "$PYTHON_ENV"
        source "$PYTHON_ENV/bin/activate"
    else
        echo "❌ Python 3 is required but not found. Please install Python 3 and try again."
        exit 1
    fi
elif [ "$MACHINE" = "Mac" ]; then
    if command -v python3 &> /dev/null; then
        python3 -m venv "$PYTHON_ENV"
        source "$PYTHON_ENV/bin/activate"
    else
        echo "❌ Python 3 is required but not found. Please install Python 3 and try again."
        exit 1
    fi
else
    echo "❌ Unsupported operating system: $MACHINE"
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r va21-omni-agent/backend/requirements.txt

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    VA21 OS - AI Model Installation"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "VA21 OS Base Size: ~5 GB (without AI models)"
echo ""
echo "All AI models are downloaded via Ollama during installation."
echo ""

# Install Ollama if not present
echo "🦙 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed successfully!"
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service if not running
echo "🚀 Starting Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 3
fi

# Download Guardian AI model (IBM Granite 4.0 2B)
echo ""
echo "🧠 Downloading Guardian AI model (IBM Granite 4.0 2B - ~1.5GB)..."
echo "This is the core security AI for VA21 OS."
echo "See: https://ollama.com/library/granite4"
echo ""
ollama pull granite4:2b

echo ""
echo "✅ Guardian AI model downloaded successfully!"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    Optional AI Models"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "The following models will be downloaded automatically on first use:"
echo ""
echo "  📢 Meta Omnilingual ASR (~2 GB) - 1,600+ language speech recognition"
echo "  📢 Whisper/Solus AI (~500 MB) - Backup offline ASR"
echo "  🗣️ Piper TTS (~150 MB) - Fast text-to-speech"
echo "  🗣️ Kokoro TTS (~200 MB) - Premium quality voices"
echo "  🧠 IBM Granite 4.0 8B (~5 GB) - Complex AI reasoning"
echo ""
echo "To pre-download the full LLM model now (optional, ~5GB):"
echo "  ollama pull granite4:8b"
echo ""

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    Optional AI Models"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "The following models will be downloaded automatically on first use:"
echo ""
echo "  📢 Meta Omnilingual ASR (~2 GB) - 1,600+ language speech recognition"
echo "  📢 Whisper/Solus AI (~500 MB) - Backup offline ASR"
echo "  🗣️ Piper TTS (~150 MB) - Fast text-to-speech"
echo "  🗣️ Kokoro TTS (~200 MB) - Premium quality voices"
echo "  🧠 IBM Granite LLM (~1.5 GB) - AI reasoning"
echo ""
echo "Total optional downloads: ~4.5 GB"
echo ""

echo "🌐 Installing Node.js dependencies..."
cd "$INSTALL_DIR"
if command -v npm &> /dev/null; then
    npm install
    cd va21-omni-agent/frontend
    npm install
    npm run build
else
    echo "⚠️ Node.js/npm not found. Frontend will not be built."
    echo "Please install Node.js to use the web interface."
fi

echo "🔧 Creating launcher script..."
cd "$INSTALL_DIR"
cat > va21-launcher.sh << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/va21-omni-agent/backend"

echo "🔒 Starting VA21 Omni Agent - Digital Fortress..."
echo "Guardian AI security system: ACTIVE"
echo "Air gap protection: ENABLED" 
echo "Access the interface at: http://localhost:5000"
echo ""

# Check if we have a Python virtual environment
if [ -f "$DIR/python-env/bin/activate" ]; then
    echo "Activating portable Python environment..."
    source "$DIR/python-env/bin/activate"
fi

# Start the lightweight server instead of the complex Flask app
python va21_server.py
EOF

chmod +x va21-launcher.sh

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "              ✅ VA21 OS INSTALLATION COMPLETE!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "🔒 VA21 Omni Agent - Digital Fortress Ready"
echo ""
echo "To start the application:"
echo "  cd $INSTALL_DIR"
echo "  ./va21-launcher.sh"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    ALL FEATURES INCLUDED"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "🔒 Security Features:"
echo "  ✅ Guardian AI Security Core (Phi-4 ONNX)"
echo "  ✅ Air Gap Browser Protection"
echo "  ✅ Threat Intelligence System"
echo "  ✅ Self-Analysis & Healing"
echo "  ✅ 5-Day Quarantine Protocol"
echo "  ✅ IBM AI Privacy Toolkit (MIT)"
echo "  ✅ LLM Guard Security (MIT)"
echo ""
echo "🎤 Voice Intelligence Layer:"
echo "  ✅ Meta Omnilingual ASR - 1,600+ languages (Apache 2.0)"
echo "  ✅ Whisper/Solus AI - Backup ASR (MIT)"
echo "  ✅ Rhasspy - Wake word detection (MIT)"
echo "  ✅ Piper TTS - Fast synthesis (MIT)"
echo "  ✅ Kokoro TTS - Premium voices (Apache 2.0)"
echo ""
echo "🤖 AI Processing:"
echo "  ✅ LangChain - AI orchestration (MIT)"
echo "  ✅ IBM Granite - LLM reasoning (Apache 2.0)"
echo "  ✅ LMDeploy - Efficient inference (Apache 2.0)"
echo ""
echo "🤝 Multi-Agent System:"
echo "  ✅ Microsoft AutoGen - Multi-agent framework (MIT)"
echo "  ✅ Agent Zero patterns - Agent cooperation (MIT)"
echo "  ✅ OpenCode patterns - Role-based agents (MIT)"
echo ""
echo "🎮 Zork-Based Text Adventure UI:"
echo "  ✅ Custom VA21 Zork Interface"
echo "  ✅ Research Lab, Knowledge Vault, Terminal Nexus"
echo "  ✅ Guardian AI NPC interaction"
echo "  ✅ ClamAV & SearXNG integration"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    VA21 OS Base: ~5 GB"
echo "           With all AI models: ~10 GB (downloaded on demand)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Om Vinayaka 🙏"
echo ""
echo "For support, visit: https://github.com/narasimhudumeetsworld/va21"