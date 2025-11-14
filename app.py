"""
Professional UI for GenAI Historical Fiction Tool
Instructor evaluation-friendly with all parameters exposed
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from aiclient import HistoricalFictionGenerator
from config import Config
import sys
import os
import re
from collections import Counter

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_characters_from_result(result):
    """Extract character names from generated content using simple heuristics"""
    content = result.get('content', '')
    
    # Basic pattern: Look for capitalized names (proper nouns)
    potential_chars = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', content)
    
    # Return unique names that appear more than once (likely characters)
    char_counts = Counter(potential_chars)
    characters = [name for name, count in char_counts.items() if count >= 2][:10]
    
    return characters

def sanitize_input(text, max_length=500):
    """Sanitize user input with character limits and basic safety checks"""
    if not text:
        return text, True
    
    # Character limit
    if len(text) > max_length:
        return text[:max_length], False
    
    # Basic profanity/harmful content filter (expand as needed)
    banned_phrases = ['<script>', 'javascript:', 'onerror=', 'onclick=']
    text_lower = text.lower()
    
    for phrase in banned_phrases:
        if phrase in text_lower:
            return "", False
    
    return text, True

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Historical Fiction Generator",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .output-box {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #E2E8F0;
        margin: 1rem 0;
    }
    .metadata-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #FCD34D;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'generator' not in st.session_state:
    try:
        st.session_state.generator = HistoricalFictionGenerator()
        st.session_state.generation_history = []
    except Exception as e:
        st.error(f"Failed to initialize generator: {str(e)}")
        st.info("Make sure your .env file is configured with GEMINI_API_KEY")
        st.stop()

# Initialize character roster
if 'character_roster' not in st.session_state:
    st.session_state.character_roster = []

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<div class="main-header">📜 Historical Fiction Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Chronology Generation with Advanced PCG Techniques</div>', unsafe_allow_html=True)

# ============================================================================
# ABOUT SECTION
# ============================================================================

with st.expander("ℹ️ About This Tool - Click to Learn More", expanded=False):
    st.markdown("""
    This tool demonstrates advanced **Procedural Content Generation (PCG)** techniques:
    
    ### Concepts Implemented
    
    #### 1. Grammar-Based Prompts
    - **What it does**: Uses theme-specific vocabulary domains and structured variable replacement
    - **How it works**: Each theme (Fantasy Kingdom, Alien Planet, etc.) has its own semantic field
    - **Example**: Fantasy Kingdom uses terms like "coronations", "sieges", "wizards"
    - **Impact**: Ensures generated content feels authentic to the chosen theme
    
    #### 2. State Management Across Generation
    - **What it does**: Tracks entities (characters, places) throughout the chronology
    - **How it works**: Identifies proper nouns and maintains continuity across events
    - **Example**: If King Alaric appears in Year 1, later events reference him appropriately
    - **Impact**: Creates coherent cause-and-effect relationships between events
    
    #### 3. Multi-Stage Generation Pipeline
    - **What it does**: Generates content in two stages for higher quality
    - **How it works**:
      - **Stage 1**: Creates initial skeleton with core events (500-850 words)
      - **Stage 2**: Refines with entity awareness and narrative improvements (up to 1000 words)
    - **Impact**: Produces more coherent, polished chronologies with better internal consistency
    
    #### 4. Parameter-Driven Content Variation
    - **What it does**: Adjustable parameters control output characteristics
    - **Parameters available**:
      - Time Span: Controls chronology length (brief/moderate/epic)
      - Event Density: Controls detail level (sparse/moderate/rich)
      - Narrative Focus: Shapes content emphasis (political/cultural/military/economic/personal)
    - **Impact**: Same theme generates different stories based on parameter combinations
    
    ### Target Output Quality
    - **Word Count**: 500-1,000 words (enforced with AI prompting + post-processing)
    - **Format**: Chronological narrative with clear temporal markers
    - **Quality**: Believable, coherent history with cause-effect relationships
    
    ### External Resources Referenced
    - GDC Talk: "Procedurally Generating History in Caves of Qud"
    - Course Materials: Technical Design (Week 6, 9, 10)
    - Google Gemini AI API for content generation
    
    ### How to Use
    1. Select a theme from the dropdown (9 options available)
    2. Set the number of characters to generate for your roster
    3. Adjust parameters using sliders and dropdowns
    4. Add custom details (optional) to seed specific elements
    5. Enable multi-stage generation for higher quality (recommended)
    6. Click **Generate Chronology** and wait 20-30 seconds
    7. Export your results in TXT or JSON format
    """)

st.markdown("---")  # Separator line

# ============================================================================
# SIDEBAR - CONFIGURATION AND PARAMETERS
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model Information
    with st.expander("📊 Model Information", expanded=False):
        st.info(f"Current Model: {st.session_state.generator.model_name}")
        st.caption(f"Target: {Config.MIN_WORDS}-{Config.MAX_WORDS} words")
    
    st.divider()
    
    # ========================================================================
    # THEME SELECTION
    # ========================================================================
    
    st.subheader("🎨 Theme Selection")
    theme = st.selectbox(
        "Choose a theme:",
        Config.THEMES,
        help="Select the type of historical fiction to generate"
    )
    
    st.divider()
    
    # ========================================================================
    # CHARACTER GENERATION SLIDER
    # ========================================================================
    
    st.subheader("🎭 Character Generation")
    num_characters = st.slider(
        "Number of characters to generate", 
        min_value=1, 
        max_value=10, 
        value=3,
        help="Choose how many characters will be created for your story roster. These characters persist across story sessions."
    )
    
    st.caption(f"Generating {num_characters} character(s) for your story roster")
    st.divider()
    
    # ========================================================================
    # CUSTOM DETAILS INPUT (WITH SANITIZATION)
    # ========================================================================
    
    st.subheader("✍️ Custom Details")
    custom_input_raw = st.text_area(
        "Enter specific details (optional)",
        height=100,
        placeholder="e.g., A kingdom built inside a massive tree, ruled by dragon riders...",
        help="Provide specific context, characters, places, or events to incorporate",
        max_chars=500
    )
    
    # Sanitize input
    custom_input, is_valid = sanitize_input(custom_input_raw, max_length=500)
    
    if not is_valid and custom_input_raw:
        st.warning("⚠️ Input exceeded 500 characters or contained invalid content. Truncated or filtered.")
    
    st.divider()
    
    # ========================================================================
    # GENERATION PARAMETERS
    # ========================================================================
    
    st.markdown("### 🎛️ Generation Parameters")
    
    # Time Span Parameter
    st.markdown("**⏱️ Time Span**")
    col1, col2 = st.columns([5, 1])
    with col1:
        timespan_value = st.select_slider(
            label="Time Span",
            options=["brief", "moderate", "epic"],
            value="moderate",
            key="timespan_slider",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("ℹ️", help="""
        **Time Span** controls the chronology's temporal scope:

        **Brief (decades)**
        - Covers 20-100 years
        - 3-5 major events
        - Target: 500-700 words
        - Example: A kingdom's founding decade

        **Moderate (centuries)**
        - Covers 100-500 years
        - 5-8 major events
        - Target: 650-900 words
        - Example: Rise and fall of a dynasty

        **Epic (millennia)**
        - Covers 500+ years
        - 8-12 major events
        - Target: 800-1000 words
        - Example: Entire civilization history
        """)
    
    # Show estimated word count
    timespan_estimates = {"brief": "500-700", "moderate": "650-900", "epic": "800-1000"}
    st.caption(f"📊 Estimated: {timespan_estimates[timespan_value]} words")
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    
    # Event Density Parameter
    st.markdown("**📊 Event Density**")
    col1, col2 = st.columns([5, 1])
    with col1:
        eventdensity_value = st.select_slider(
            label="Event Density",
            options=["sparse", "moderate", "rich"],
            value="moderate",
            key="eventdensity_slider",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("ℹ️", help="""
        **Event Density** controls detail level and number of events:

        **Sparse (3-5 events)**
        - Major milestones only
        - Broad strokes narrative
        - More space between events
        - Example: Key turning points only

        **Moderate (5-8 events)**
        - Balanced coverage
        - Important events with context
        - Recommended for most uses

        **Rich (8-12 events)**
        - Detailed chronology
        - Many interconnected events
        - Dense narrative
        - Example: Year-by-year coverage
        """)
    
    # Show event count estimate
    event_counts = {"sparse": "3-5 events", "moderate": "5-8 events", "rich": "8-12 events"}
    st.caption(f"📊 Expected: {event_counts[eventdensity_value]}")
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    
    # Narrative Focus Parameter
    st.markdown("**🎯 Narrative Focus**")
    col1, col2 = st.columns([5, 1])
    with col1:
        narrativefocus_value = st.selectbox(
            label="Narrative Focus",
            options=["political", "cultural", "military", "economic", "personal"],
            index=0,
            key="narrativefocus_select",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("ℹ️", help="""
        **Narrative Focus** shapes content emphasis:

        **Political**
        Governments, leaders, alliances, treaties
        - Focus on power dynamics and governance

        **Cultural**
        Arts, traditions, religions, customs
        - Focus on societal values and cultural evolution

        **Military**
        Wars, battles, conquests, defenses
        - Focus on conflicts and military campaigns

        **Economic**
        Trade, resources, wealth, commerce
        - Focus on prosperity and economic systems

        **Personal**
        Individuals, families, relationships
        - Focus on human stories and lineages
        """)
    
    focus_icons = {
        "political": "🏛️",
        "cultural": "🎨",
        "military": "⚔️",
        "economic": "💰",
        "personal": "👥"
    }
    st.caption(f"{focus_icons[narrativefocus_value]} Focus: {narrativefocus_value.capitalize()}")
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    
    # Multi-Stage Generation Toggle
    col1, col2 = st.columns([5, 1])
    with col1:
        use_multistage = st.checkbox(
            "Enable Multi-Stage Generation",
            value=True,
            key="multistage_checkbox"
        )
    with col2:
        st.markdown("ℹ️", help="""
        **Multi-Stage Generation** uses a two-phase process:

        **Enabled (Recommended)**
        - Stage 1: Generate skeleton structure
        - Stage 2: Refine with entity tracking
        - Higher quality, more coherent output
        - Takes 25-30 seconds

        **Disabled (Faster)**
        - Single-pass generation
        - Faster (10-15 seconds)
        - Lower coherence and consistency
        - Not recommended for final outputs
        """)
    
    # Visual indicator for multi-stage
    if use_multistage:
        st.success("✅ Quality mode: Multi-stage pipeline active")
    else:
        st.warning("⚡ Speed mode: Single-stage generation")
    
    st.divider()
    
    # ========================================================================
    # PARAMETER VALIDATION SUMMARY
    # ========================================================================
    
    st.markdown("### 📊 Generation Preview")
    
    # Calculate estimated metrics
    time_multiplier = {"brief": 0.7, "moderate": 0.85, "epic": 1.0}
    density_multiplier = {"sparse": 0.8, "moderate": 1.0, "rich": 1.2}
    base_word_estimate = 750  # Middle of 500-1000 range
    
    estimated_words = int(base_word_estimate * time_multiplier[timespan_value] * density_multiplier[eventdensity_value])
    
    # Clamp to valid range
    estimated_words = max(500