# NovaOCR - Professional OCR Desktop Application

**OCR + AI-powered text cleanup** with a beautiful desktop interface and full SOLID architecture.

![NovaOCR](https://img.shields.io/badge/version-1.0.0-blue) ![Python](https://img.shields.io/badge/python-3.8+-green) ![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

- **🖥️ Desktop GUI** - Beautiful PyQt6 interface with drag-and-drop support
- **🤖 AI-Powered** - Mistral Large for intelligent text cleanup
- **📄 OCR Support** - Process PDFs and images (PNG, JPG, WEBP)
- **⚡ Batch Processing** - Process multiple files efficiently
- **🎯 Real-time Progress** - Live updates and statistics
- **⚙️ Fully Configurable** - Edit API keys, models, prompts via GUI or YAML
- **🔄 Pause/Resume** - Control processing flow
- **📝 Multiple Formats** - Output to DOCX or TXT
- **⌨️ CLI Mode** - Command-line interface for automation
- **🏗️ SOLID Architecture** - Extensible and maintainable codebase

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
cd d:\Git\NovaOCR
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Pandoc** (required for DOCX output)
   - Windows: Download from [Pandoc Releases](https://github.com/jgm/pandoc/releases)
   - Or use chocolatey: `choco install pandoc`

4. **Configure API Key**

Option A: Edit `config/config.yaml`
```yaml
api:
  mistral:
    api_key: "your-mistral-api-key-here"
```

Option B: Use environment variable
```bash
# Create .env file from template
copy .env.example .env

# Edit .env and add your key
MISTRAL_API_KEY=your-mistral-api-key-here
```

### Usage

**🖥️ Desktop GUI (Recommended)**
```bash
python src/main.py
```

**⌨️ CLI Mode**
```bash
# Basic usage
python src/main.py --cli --input-folder ./scans

# Custom output
python src/main.py --cli --input-folder ./scans --output-name mybook.docx

# Debug mode
python src/main.py --cli --input-folder ./scans --log-level DEBUG
```

## 📖 How It Works

1. **Select Folder** - Choose folder with images/PDFs (or drag and drop)
2. **OCR Processing** - Mistral OCR extracts text from each file
3. **Batch Cleanup** - Process files in batches for better context
4. **AI Enhancement** - Mistral Large cleans and formats the text
5. **Output Generation** - Save as DOCX or TXT

## ⚙️ Configuration

### GUI Settings
Click **Settings → Configuration** to edit:
- API keys
- Model selections
- Batch size
- Retry logic
- System prompts

### Manual Configuration
Edit `config/config.yaml`:
```yaml
api:
  mistral:
    api_key: ""
    ocr_model: "mistral-ocr-latest"
    llm_model: "mistral-large-latest"

processing:
  batch_size: 7
  max_retries: 3
  retry_backoff_base: 2
```

### Custom Prompts
Edit `config/prompts.yaml` to customize AI behavior:
```yaml
text_cleanup:
  system_prompt: |
    You are a professional book editor...
  temperature: 0
```

## 🏗️ Architecture

Built with **SOLID principles** for extensibility:

```
┌─────────────┐     ┌─────────────┐
│   Desktop   │────▶│     CLI     │
│     GUI     │     │  Interface  │
└─────────────┘     └─────────────┘
       │                   │
       └───────┬───────────┘
               ▼
    ┌──────────────────┐
    │  Application     │
    │  Controller      │
    └──────────────────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
    ┌────┐ ┌────┐ ┌────┐
    │OCR │ │LLM │ │Out │
    └────┘ └────┘ └────┘
```

### Key Components

- **Interfaces** - Abstract base classes (Open/Closed Principle)
- **Providers** - Mistral OCR & LLM implementations
- **Core** - Config manager, file handler, batch processor
- **GUI** - PyQt6 desktop application
- **Output** - DOCX and TXT generators

## 🔧 Extending NovaOCR

### Add New OCR Provider

```python
# src/providers/google_vision_ocr.py
from interfaces.ocr_provider import OCRProvider

class GoogleVisionOCR(OCRProvider):
    def extract_text(self, file_path: str) -> str:
        # Your implementation
        pass
```

### Add New LLM Provider

```python
# src/providers/openai_llm.py
from interfaces.llm_provider import LLMProvider

class OpenAILLM(LLMProvider):
    def clean_text(self, raw_text: str, ...) -> str:
        # Your implementation
        pass
```

**No modification to existing code required!** ✅

## 📁 Project Structure

```
NovaOCR/
├── config/
│   ├── config.yaml       # Main configuration
│   └── prompts.yaml      # Editable prompts
├── src/
│   ├── interfaces/       # Abstract interfaces
│   ├── providers/        # OCR & LLM providers
│   ├── output/           # Output generators
│   ├── core/             # Core business logic
│   ├── gui/              # Desktop GUI
│   ├── utils/            # Utilities
│   └── main.py           # Entry point
├── requirements.txt
└── README.md
```

## 🐛 Troubleshooting

**"API Key Missing"**
- Set API key in `config/config.yaml` or `.env` file

**"Pandoc not found"**
- Install Pandoc for DOCX output
- Fallback to TXT if Pandoc unavailable

**"No valid files found"**
- Check folder contains PDFs or images
- Supported formats: PDF, PNG, JPG, JPEG, WEBP

**GUI won't launch**
- Ensure PyQt6 is installed: `pip install PyQt6`
- Try CLI mode: `python src/main.py --cli`

## 📝 License

MIT License - feel free to use and modify!

## 🙏 Credits

- **Mistral AI** - OCR and LLM services
- **PyQt6** - Desktop GUI framework
- **Pypandoc** - Document conversion

---

Built with ❤️ using SOLID principles for maximum extensibility.
