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

pip install -r requirements.txt

## 🔑 Configuration

1. Get your Gemini API key from: https://aistudio.google.com/app/apikey
2. Create `.env` file:
3. Set up env file with params:
    GEMINI_API_KEY=your_api_key_here
    MODEL_NAME=gemini-2.0-flash-exp
    MAX_TOKENS=2000
    TEMPERATURE=0.7

## 🚀 Usage

### Quick Test (Single Generation)
python manual_test.py --quick

### Interactive Mode (Full Parameter Control)
python manual_test.py

This launches an interactive session where you can:
- Select theme from 9 options
- Enter custom details
- Choose time span (brief/moderate/epic)
- Set event density (sparse/moderate/rich)
- Select narrative focus (political/cultural/military/economic/personal)
- Enable/disable multi-stage generation

### Full Test Suite (20+ Test Cases)
python test_runner.py

### Quick Test Suite (3 Test Cases)
python test_runner.py --quick

## 📊 Output Files
All results saved in `test_results/` directory:

- `*_TIMESTAMP.json` - Complete data with all metadata
- `*_TIMESTAMP.csv` - Spreadsheet format with parameters
- `*_TIMESTAMP_detailed.txt` - Full content with analysis