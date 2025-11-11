# Historical Fiction Generator - Enhanced with Course Concepts

Complete implementation with advanced procedural generation techniques from Technical Design course.

## 🎯 Course Concepts Applied

### 1. **Grammar-Based Prompt System** (Week 10 - PCG Techniques)
- Theme-specific vocabulary domains
- Structured variable replacement
- Semantic guidance for coherent output

### 2. **State Management Across Generation** (Week 9 - Dynamic Storytelling)
- Entity tracking (characters, places, items)
- Cross-referencing earlier events
- Cause-and-effect relationship building

### 3. **Multi-Stage Generation Pipeline** (Week 6 - Dynamic Content)
- Stage 1: Initial chronology skeleton
- Stage 2: Refinement with entity callbacks
- Progressive coherence checking

### 4. **Parameter-Driven Content Variation** (Week 10 - Utility Design)
- Time span control (brief/moderate/epic)
- Event density adjustment (sparse/moderate/rich)
- Narrative focus selection (political/cultural/military/economic/personal)

## 📦 Installation

### System Requirements
- **Python Version:** 3.11.x (Required)
  - ⚠️ **Python 3.14+ is NOT compatible** due to Streamlit/Pillow dependencies
  - ✅ **Download Python 3.11.9**: https://www.python.org/downloads/release/python-3119/

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- `google-generativeai>=0.3.0` - Gemini API client
- `python-dotenv>=1.0.0` - Environment configuration
- `streamlit==1.28.0` - Web UI framework
- `pyinstaller>=6.0.0` - EXE building

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 🔑 Configuration

1. Get your Gemini API key from: https://aistudio.google.com/app/apikey
2. Create `.env` file in the project root
3. Add your API key and configuration:

```plaintext
# Gemini API Configuration
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash-exp
MAX_TOKENS=1500
TEMPERATURE=0.7
```

## 🚀 Usage

### Quick Test (Single Generation)
```bash
python manual_test.py --quick
```

### Interactive Mode (Full Parameter Control)
```bash
python manual_test.py
```

This launches an interactive session where you can:
- Select theme from 9 options
- Enter custom details
- Choose time span (brief/moderate/epic)
- Set event density (sparse/moderate/rich)
- Select narrative focus (political/cultural/military/economic/personal)
- Enable/disable multi-stage generation

### Full Test Suite (20+ Test Cases)
```bash
python test_runner.py
```

### Quick Test Suite (3 Test Cases)
```bash
python test_runner.py --quick
```

## Build EXE
Ensure your .env is already configured before building exe
```bash
build.bat
```

## 📊 Output Files

### Automated Test Results
All automated test results are saved in `test_results/` directory:

- `*_TIMESTAMP.json` - Complete data with all metadata
- `*_TIMESTAMP.csv` - Spreadsheet format with parameters
- `*_TIMESTAMP_detailed.txt` - Full content with analysis

### Manual Test Results
Manual test outputs are saved in `output/` directory:

- `filename.json` - Complete generation data with metadata
- `filename.txt` - Pure text content
- `quick_test_TIMESTAMP.json` - Auto-saved quick test results
- `quick_test_TIMESTAMP.txt` - Auto-saved quick test content

### EXE Output
- `dist\HistoricalFictionGenerator\HistoricalFictionGenerator.exe` - exe output
