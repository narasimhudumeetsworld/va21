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

echo "🧠 Downloading Guardian AI model..."
# Create model directory and download Phi-4 mini model files
MODEL_DIR="$INSTALL_DIR/va21-omni-agent/backend"
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

# Model files to download from HuggingFace
MODEL_BASE_URL="https://huggingface.co/microsoft/Phi-4-mini-reasoning-onnx/resolve/main/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4"
MODEL_FILES=(
    "added_tokens.json"
    "config.json"
    "configuration_phi3.py"  
    "genai_config.json"
    "merges.txt"
    "model.onnx"
    "model.onnx.data"
    "special_tokens_map.json"
    "tokenizer.json"
    "tokenizer_config.json"
    "vocab.json"
)

echo "Downloading Guardian AI model files..."
for file in "${MODEL_FILES[@]}"; do
    echo "Downloading $file..."
    curl -L "$MODEL_BASE_URL/$file" -o "$file"
done

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

echo "✅ Installation complete!"
echo ""
echo "🔒 VA21 Omni Agent - Digital Fortress Ready"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  cd $INSTALL_DIR"
echo "  ./va21-launcher.sh"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "Security Features Active:"
echo "  ✓ Guardian AI Security Core"
echo "  ✓ Air Gap Browser Protection"
echo "  ✓ Threat Intelligence System"
echo "  ✓ Self-Analysis & Healing"
echo "  ✓ 5-Day Quarantine Protocol"
echo ""
echo "For support, visit: https://github.com/narasimhudumeetsworld/va21"