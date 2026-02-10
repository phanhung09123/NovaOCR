# NovaOCR

![NovaOCR](https://img.shields.io/badge/version-1.0.0-blue) ![Python](https://img.shields.io/badge/python-3.8+-green) ![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

- **🤖 AI-Powered** - Mistral Large for intelligent text cleanup
- **📄 OCR Support** - Process PDFs and images (PNG, JPG, WEBP)
- **⚡ Batch Processing** - Process multiple files efficiently
- **🎯 Real-time Progress** - Live updates and statistics
- **⚙️ Fully Configurable** - Edit API keys, models, prompts via GUI or YAML
- **📝 Multiple Formats** - Output to DOCX or TXT

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/phanhung09123/NovaOCR.git
cd NovaOCR
```

2. **Install dependencies**

**Option A - Use install script (Easy):**
```bash
install.bat
```

**Option B - Manual install:**
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

**Option A - Use launcher (Easy):**
```bash
run.bat
```

**Option B - Direct command:**
```bash
python -m src.main
```

**⌨️ CLI Mode**
```bash
# Basic usage
python -m src.main --cli --input-folder ./scans

# Custom output
python -m src.main --cli --input-folder ./scans --output-name mybook.docx

# Debug mode
python -m src.main --cli --input-folder ./scans --log-level DEBUG
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
- **Pypandoc** - Document conversion

---
