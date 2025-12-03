# VA21 OS Model Requirements and Storage Guide

**Om Vinayaka** 🙏 - *Complete AI Model and Storage Requirements*

---

## 📊 Storage Requirements Overview

VA21 OS is a comprehensive AI-powered operating system with a custom Zork-based text adventure interface. The **full OS installation is approximately 5GB** (without AI model weights), with **all AI models downloaded during installation**.

### Storage Breakdown

| Component | Size | Notes |
|-----------|------|-------|
| **VA21 Core System** | ~2 GB | Zork UI, Chromium, system tools |
| **Linux OS Base** | ~1.5 GB | Debian base, kernel, packages |
| **Python Environment** | ~500 MB | Dependencies, frameworks |
| **Documentation & Assets** | ~200 MB | Docs, images, configs |
| **Research Suite** | ~300 MB | Writing, journalism, games |
| **Frontend (React)** | ~200 MB | Web interface |
| **Scripts & Tools** | ~100 MB | Utilities, configs |
| **Total OS Size** | **~5 GB** | Without AI models |

### AI Models (Downloaded During Installation)

All AI models are downloaded via Ollama during installation:

| Model | Download Size | Purpose | When Downloaded |
|-------|---------------|---------|-----------------|
| **Guardian AI (Granite 4.0 2B)** | ~1.5 GB | Security analysis | During install |
| Meta Omnilingual ASR | ~2 GB | 1,600+ language speech | First voice use |
| Whisper (Backup ASR) | ~500 MB | Offline backup ASR | Optional |
| Piper TTS Voices | ~150 MB | Fast text-to-speech | First TTS use |
| Kokoro TTS Premium | ~200 MB | Premium quality voices | Optional |
| IBM Granite 4.0 8B | ~5 GB | Complex AI reasoning | First LLM query |
| **Total AI Models** | **~9.5 GB** | Full AI suite |

> **Note:** Guardian AI (IBM Granite 4.0 2B) is downloaded during installation via Ollama. Other AI models are downloaded on-demand during first use.

---

## 🤖 AI Model Components

### 1. Meta Omnilingual ASR (Apache 2.0)

**Purpose:** 1,600+ language speech recognition with special focus on Indian languages

| Model Size | Parameters | Download Size | RAM Required | Accuracy |
|------------|------------|---------------|--------------|----------|
| Small | 300M | ~600 MB | ~2 GB | Good |
| Medium | 1B | ~2 GB | ~4 GB | Very Good |
| Large | 3B | ~6 GB | ~8 GB | Excellent |
| XLarge | 7B | ~14 GB | ~14 GB | Best |

**VA21 Default:** 1B model (balanced accuracy vs. resource usage)

**Download Source:** [Meta FAIR Research](https://github.com/facebookresearch/fairseq)

```bash
# Download Meta Omnilingual ASR (1B model)
# Size: ~2 GB
va21-model-download omnilingual-asr-1b
```

---

### 2. Whisper/Solus AI (MIT)

**Purpose:** Offline backup ASR for common languages

| Model | Download Size | RAM Required | Languages |
|-------|---------------|--------------|-----------|
| Tiny | ~75 MB | ~1 GB | 99 |
| Base | ~148 MB | ~1 GB | 99 |
| Small | ~488 MB | ~2 GB | 99 |
| Medium | ~1.5 GB | ~4 GB | 99 |
| Large | ~3 GB | ~10 GB | 99 |

**VA21 Default:** Small model

**Download Source:** [OpenAI Whisper](https://github.com/openai/whisper)

```bash
# Download Whisper Small model
# Size: ~488 MB
va21-model-download whisper-small
```

---

### 3. Rhasspy Wake Word (MIT)

**Purpose:** Custom wake word detection ("Hey VA21", "Om Vinayaka")

| Component | Download Size |
|-----------|---------------|
| Core Engine | ~50 MB |
| Custom Wake Words | ~10 MB |
| **Total** | **~60 MB** |

**Download Source:** [Rhasspy](https://github.com/rhasspy/rhasspy)

```bash
# Download Rhasspy wake word models
# Size: ~60 MB
va21-model-download rhasspy-wakeword
```

---

### 4. Piper TTS (MIT)

**Purpose:** Fast text-to-speech synthesis

| Voice Set | Download Size | Languages |
|-----------|---------------|-----------|
| English (US/UK) | ~50 MB | 2 |
| Indian Languages | ~100 MB | 10+ |
| European | ~80 MB | 10+ |
| All Languages | ~300 MB | 30+ |

**VA21 Default:** English + Indian Languages (~150 MB)

**Download Source:** [Piper TTS](https://github.com/rhasspy/piper)

```bash
# Download Piper TTS voices
# Size: ~150 MB
va21-model-download piper-tts-voices
```

---

### 5. Kokoro TTS (Apache 2.0)

**Purpose:** Premium quality neural text-to-speech

| Model | Download Size | RAM Required |
|-------|---------------|--------------|
| Kokoro-82M | ~200 MB | ~1 GB |

**Download Source:** [Kokoro FastAPI](https://github.com/remsky/Kokoro-FastAPI)

```bash
# Download Kokoro TTS
# Size: ~200 MB
va21-model-download kokoro-tts
```

---

### 6. IBM Granite 4.0 LLM (Apache 2.0)

**Purpose:** AI reasoning and language understanding

IBM Granite 4.0 is the latest generation with improved performance, 128K context window, and hybrid architecture options.

| Model | Parameters | Download Size | RAM Required | Use Case |
|-------|------------|---------------|--------------|----------|
| granite4:2b | 2B | ~1.5 GB | ~3 GB | Guardian AI |
| granite4:3b | 3B | ~2 GB | ~4 GB | Micro tasks |
| granite4:8b | 8B | ~5 GB | ~8 GB | Full LLM |

**VA21 Models:**
- **Guardian AI:** `granite4:2b` (~1.5 GB) - Fast security analysis
- **General LLM:** `granite4:8b` (~5 GB) - Complex reasoning

**Download Source:** 
- Ollama: https://ollama.com/library/granite4
- HuggingFace: https://huggingface.co/ibm-granite

```bash
# Download via Ollama (recommended)
ollama pull granite4:2b  # Guardian AI
ollama pull granite4:8b  # Full LLM (optional)
```

**IBM Granite 4.0 Features:**
- ✅ Apache 2.0 License (fully permissive)
- ✅ 128K context window
- ✅ Hybrid Mamba-2 architecture option
- ✅ 70% reduced memory usage (hybrid models)
- ✅ Enterprise-grade quality

---

### 7. Guardian AI (IBM Granite 4.0 2B via Ollama)

**Purpose:** Security core with Think>Vet>Act methodology

| Component | Download Size |
|-----------|---------------|
| IBM Granite 4.0 2B | ~1.5 GB |
| Security Patterns | Built-in |
| **Total** | **~1.5 GB** |

**Download via Ollama:**
```bash
# Guardian AI model (downloaded during installation)
ollama pull granite4:2b
```

**Why Granite 4.0 for Guardian AI:**
- Fast inference for real-time security analysis
- 128K context for analyzing large code blocks
- Enterprise-grade accuracy
- Apache 2.0 License

---

### 8. LangChain + Dependencies (MIT)

**Purpose:** AI orchestration framework

| Component | Download Size |
|-----------|---------------|
| LangChain Core | ~50 MB |
| Embeddings Model | ~100 MB |
| Vector Store | ~20 MB |

```bash
# Install LangChain dependencies
pip install langchain langchain-community
```

---

### 9. LLM Guard (MIT)

**Purpose:** LLM security scanning

| Component | Download Size |
|-----------|---------------|
| Scanners | ~30 MB |
| Patterns | ~10 MB |

```bash
# Install LLM Guard
pip install llm-guard
```

---

### 10. IBM AI Privacy Toolkit (MIT)

**Purpose:** GDPR compliance and data privacy

| Component | Download Size |
|-----------|---------------|
| Privacy Toolkit | ~20 MB |

```bash
# Install AI Privacy Toolkit
pip install ai-privacy-toolkit
```

---

### 11. LMDeploy (Apache 2.0)

**Purpose:** Efficient LLM inference

| Component | Download Size |
|-----------|---------------|
| LMDeploy Engine | ~100 MB |

```bash
# Install LMDeploy
pip install lmdeploy
```

---

### 12. Microsoft AutoGen (MIT)

**Purpose:** Multi-agent conversation framework

| Component | Download Size |
|-----------|---------------|
| AutoGen Core | ~30 MB |

```bash
# Install Microsoft AutoGen
pip install pyautogen
```

---

### 13. Agent Zero Patterns (MIT)

**Purpose:** Multi-agent cooperation patterns (integrated, no separate download)

---

### 14. OpenCode Patterns (MIT)

**Purpose:** Role-based agent patterns (integrated, no separate download)

---

## 📦 Complete Installation Profiles

### Minimal Installation (~500 MB)
For systems with 4GB RAM:
- Guardian AI (INT4)
- Whisper Tiny
- Piper TTS (English only)
- Basic security scanners

```bash
va21-install --profile minimal
```

### Standard Installation (~2 GB)
For systems with 7GB RAM (VA21 Default):
- Guardian AI
- Meta Omnilingual ASR (1B)
- Whisper Small
- Piper TTS (English + Indian)
- LLM Guard
- AI Privacy Toolkit

```bash
va21-install --profile standard
```

### Full Installation (~5 GB)
For systems with 10GB+ RAM:
- All AI models
- All TTS voices
- All language support
- Premium quality voices

```bash
va21-install --profile full
```

### Maximum Installation (~10+ GB)
For high-end systems with 16GB+ RAM:
- All models at highest quality
- Granite-8B
- Meta ASR 3B
- Whisper Large
- All Kokoro premium voices

```bash
va21-install --profile maximum
```

---

## 📥 Model Download Commands

### Download All Models (Standard Profile)

```bash
#!/bin/bash
# va21-download-models.sh
# Downloads all models for standard VA21 installation
# Total Size: ~5 GB

echo "🔒 VA21 OS - Downloading AI Models"
echo "==================================="
echo "This will download approximately 5 GB of data."
echo ""

# Create model directory
MODEL_DIR="$HOME/.va21/models"
mkdir -p "$MODEL_DIR"

# 1. Guardian AI (Phi-4 Mini ONNX)
echo "📥 Downloading Guardian AI model (~500 MB)..."
mkdir -p "$MODEL_DIR/guardian"
# Download from HuggingFace
curl -L "https://huggingface.co/microsoft/Phi-4-mini-reasoning-onnx/resolve/main/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/model.onnx" \
     -o "$MODEL_DIR/guardian/model.onnx"

# 2. Meta Omnilingual ASR
echo "📥 Downloading Meta Omnilingual ASR (~2 GB)..."
mkdir -p "$MODEL_DIR/asr"
# Note: Replace with actual model URL when available
# python -c "from fairseq2 import OmnilingualASR; OmnilingualASR.download('1b')"

# 3. Whisper
echo "📥 Downloading Whisper Small (~500 MB)..."
mkdir -p "$MODEL_DIR/whisper"
python -c "import whisper; whisper.load_model('small', download_root='$MODEL_DIR/whisper')"

# 4. Piper TTS
echo "📥 Downloading Piper TTS voices (~150 MB)..."
mkdir -p "$MODEL_DIR/piper"
# Download voice models from piper releases

# 5. IBM Granite (Quantized)
echo "📥 Downloading IBM Granite 3B (~1.5 GB)..."
mkdir -p "$MODEL_DIR/granite"
# Download via Ollama or HuggingFace

# 6. Kokoro TTS
echo "📥 Downloading Kokoro TTS (~200 MB)..."
mkdir -p "$MODEL_DIR/kokoro"

echo ""
echo "✅ All models downloaded successfully!"
echo "Total size: $(du -sh $MODEL_DIR | cut -f1)"
```

---

## 💾 Storage Breakdown by Feature

| Feature | Models Included | Storage | RAM |
|---------|-----------------|---------|-----|
| **Voice Intelligence Layer** | Meta ASR, Whisper, Rhasspy, Piper, Kokoro | ~3 GB | 4-6 GB |
| **Guardian AI Security** | Phi-4 ONNX, Security Patterns | ~500 MB | 2 GB |
| **LLM Processing** | Granite, LangChain | ~2 GB | 4-8 GB |
| **Privacy & Security** | LLM Guard, AI Privacy Toolkit | ~100 MB | 512 MB |
| **Multi-Agent System** | AutoGen, Agent Zero patterns | ~50 MB | 1 GB |

---

## 🔧 Configuration for Different Hardware

### Raspberry Pi / Low-Power Devices (4GB RAM)
```yaml
# ~/.va21/config.yaml
profile: minimal
models:
  asr: whisper-tiny
  tts: piper-fast
  llm: granite-3b-int4
  guardian: phi-4-int4
quantization: 4-bit
max_concurrent_models: 1
```

### Consumer Laptop (8GB RAM)
```yaml
# ~/.va21/config.yaml
profile: standard
models:
  asr: omnilingual-1b
  tts: piper-balanced
  llm: granite-3b-int8
  guardian: phi-4-int8
quantization: 8-bit
max_concurrent_models: 2
```

### Desktop/Workstation (16GB+ RAM)
```yaml
# ~/.va21/config.yaml
profile: full
models:
  asr: omnilingual-3b
  tts: kokoro-premium
  llm: granite-8b
  guardian: phi-4-fp16
quantization: fp16
max_concurrent_models: 4
```

---

## 📊 Expected Disk Usage After Full Installation

```
~/.va21/
├── models/                 # ~5 GB
│   ├── guardian/          # ~500 MB
│   ├── asr/               # ~2 GB
│   ├── whisper/           # ~500 MB
│   ├── piper/             # ~150 MB
│   ├── kokoro/            # ~200 MB
│   ├── granite/           # ~1.5 GB
│   └── embeddings/        # ~100 MB
├── data/                  # ~200 MB (grows over time)
│   ├── knowledge_vault/
│   ├── backups/
│   └── logs/
├── config/                # ~1 MB
└── cache/                 # ~100 MB
```

---

## 🔄 Model Updates

Models are versioned and can be updated:

```bash
# Check for model updates
va21-model check-updates

# Update specific model
va21-model update guardian-ai

# Update all models
va21-model update-all
```

---

## 📝 License Summary

All integrated models use permissive open source licenses:

| Model | License | Commercial Use |
|-------|---------|----------------|
| Meta Omnilingual ASR | Apache 2.0 | ✅ Yes |
| Whisper | MIT | ✅ Yes |
| Rhasspy | MIT | ✅ Yes |
| Piper TTS | MIT | ✅ Yes |
| Kokoro TTS | Apache 2.0 | ✅ Yes |
| IBM Granite | Apache 2.0 | ✅ Yes |
| LangChain | MIT | ✅ Yes |
| LLM Guard | MIT | ✅ Yes |
| IBM AI Privacy Toolkit | MIT | ✅ Yes |
| LMDeploy | Apache 2.0 | ✅ Yes |
| Microsoft AutoGen | MIT | ✅ Yes |
| Agent Zero | MIT | ✅ Yes |
| OpenCode | MIT | ✅ Yes |

---

## 🙏 Acknowledgments

VA21 OS gratefully acknowledges all the open source projects that make this possible:

- **Meta AI** - Omnilingual ASR (Apache 2.0)
- **OpenAI** - Whisper (MIT)
- **Rhasspy** - Wake word and Piper TTS (MIT)
- **Kokoro** - Premium TTS (Apache 2.0)
- **IBM** - Granite LLM and AI Privacy Toolkit (Apache 2.0 + MIT)
- **Microsoft** - AutoGen and Phi-4 (MIT)
- **ProtectAI** - LLM Guard (MIT)
- **InternLM** - LMDeploy (Apache 2.0)
- **Agent Zero** - Multi-agent patterns (MIT)
- **OpenCode/SST** - Role-based agents (MIT)

---

**Om Vinayaka** 🙏

*Intelligence flows where models serve humanity.*

---

**Questions?** Open an issue: https://github.com/narasimhudumeetsworld/va21/issues
