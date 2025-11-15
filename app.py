
"""
Professional UI for GenAI Historical Fiction Tool
Instructor evaluation-friendly with all parameters exposed
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from ai_client import HistoricalFictionGenerator
from config import Config
import sys
import os

from session_manager import SessionManager
#from input_validator import InputValidator 

# Page configuration
st.set_page_config(
    page_title="Historical Fiction Generator",
    page_icon="📚",
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

# Initialize session state
if 'generator' not in st.session_state:
    try:
        st.session_state.generator = HistoricalFictionGenerator()
        st.session_state.generation_history = []
        st.session_state.session_manager = SessionManager()
        st.session_state.current_session_id = st.session_state.session_manager.session_id
    except Exception as e:
        st.error(f"❌ Failed to initialize generator: {str(e)}")
        st.info("💡 Make sure your `.env` file is configured with GEMINI_API_KEY")
        st.stop()

# Header
st.markdown('<div class="main-header">📚 Historical Fiction Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Chronology Generation with Advanced PCG Techniques</div>', unsafe_allow_html=True)

# Add "About" expandable section at the top
with st.expander("ℹ️ About This Tool - Click to Learn More", expanded=False):
    st.markdown("""
    ### 🎓 **Concepts Implemented**
    
    This tool demonstrates advanced **Procedural Content Generation (PCG)** techniques:
    
    #### 1️⃣ **Grammar-Based Prompts**
    - **What it does:** Uses theme-specific vocabulary domains and structured variable replacement
    - **How it works:** Each theme (Fantasy Kingdom, Alien Planet, etc.) has its own semantic field
    - **Example:** Fantasy Kingdom → uses terms like "coronations", "sieges", "wizards"
    - **Impact:** Ensures generated content feels authentic to the chosen theme
    
    #### 2️⃣ **State Management Across Generation**
    - **What it does:** Tracks entities (characters, places) throughout the chronology
    - **How it works:** Identifies proper nouns and maintains continuity across events
    - **Example:** If "King Alaric" appears in Year 1, later events reference him appropriately
    - **Impact:** Creates coherent cause-and-effect relationships between events
    
    #### 3️⃣ **Multi-Stage Generation Pipeline**
    - **What it does:** Generates content in two stages for higher quality
    - **How it works:**
        - **Stage 1:** Creates initial skeleton with core events (500-850 words)
        - **Stage 2:** Refines with entity awareness and narrative improvements (up to 1000 words)
    - **Impact:** Produces more coherent, polished chronologies with better internal consistency
    
    #### 4️⃣ **Parameter-Driven Content Variation**
    - **What it does:** Adjustable parameters control output characteristics
    - **Parameters available:**
        - **Time Span:** Controls chronology length (brief/moderate/epic)
        - **Event Density:** Controls detail level (sparse/moderate/rich)
        - **Narrative Focus:** Shapes content emphasis (political/cultural/military/economic/personal)
    - **Impact:** Same theme generates different stories based on parameter combinations
    
    ---
    
    ### 📊 **Target Output Quality**
    - **Word Count:** 500-1,000 words (enforced with AI prompting + post-processing)
    - **Format:** Chronological narrative with clear temporal markers
    - **Quality:** Believable, coherent history with cause-effect relationships
    
    ### 🔗 **External Resources Referenced**
    - GDC Talk: ["Procedurally Generating History in Caves of Qud"](https://www.youtube.com/watch?v=H0sLa1y3BW4)
    - Course Materials: Technical Design (Week 6, 9, 10)
    - Google Gemini AI API for content generation
    
    ### 📖 **How to Use**
    1. **Select a theme** from the dropdown (9 options available)
    2. **Adjust parameters** using sliders and dropdowns
    3. **Add custom details** (optional) to seed specific elements
    4. **Enable multi-stage generation** for higher quality (recommended)
    5. **Click "Generate Chronology"** and wait ~20-30 seconds
    6. **Export your results** in TXT or JSON format
    """)

st.markdown("---")  # Separator line

# Sidebar - Configuration and Parameters
with st.sidebar:
    st.header("⚙️ Configuration")

    # === SESSION CONTROLS ===
    st.subheader("💾 Session Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Session", use_container_width=True):
            try:
                filepath = st.session_state.session_manager.save()
                st.success(f"✅ Saved!")
                st.caption(f"File: {filepath}")
            except Exception as e:
                st.error(f"❌ Save failed: {e}")

    with col2:
        if st.button("🔄 New Session", use_container_width=True):
            # Clear all relevant session state
            st.session_state.session_manager = SessionManager()
            st.session_state.current_session_id = st.session_state.session_manager.session_id

    # Load existing session
    available_sessions = SessionManager.list_available_sessions()
    if available_sessions:
        with st.expander("📂 Load Previous Session", expanded=False):
            session_options = {
                f"{s['session_id']} - {s['theme']} ({s['events']} events)": s['session_id'] 
                for s in available_sessions
            }
            
            selected = st.selectbox(
                "Select session:",
                options=list(session_options.keys()),
                key="session_select"
            )
            
            if st.button("Load Selected", key="load_btn"):
                try:
                    session_id = session_options[selected]
                    st.session_state.session_manager = SessionManager.load(session_id)
                    st.session_state.current_session_id = session_id
                    st.success(f"✅ Loaded: {session_id}")
                    # Don't call st.rerun() here either
                except Exception as e:
                    st.error(f"❌ Load failed: {e}")

    # Display current session info
    st.caption(f"Current: {st.session_state.current_session_id}")
    st.caption(f"Events generated: {st.session_state.session_manager.metadata['generation_count']}")

    st.divider()

    # Model information
    with st.expander("🤖 Model Information", expanded=False):
        st.info(f"**Current Model:** {st.session_state.generator.model_name}")
        st.caption(f"Target: {Config.MIN_WORDS}-{Config.MAX_WORDS} words")
    
    st.divider()
    
    # Theme Selection
    st.subheader("🎨 Theme Selection")
    theme = st.selectbox(
        "Choose a theme:",
        Config.THEMES,
        help="Select the type of historical fiction to generate"
    )

    st.divider()

    # ========== Character Configuration ==========
    st.sidebar.subheader("🎭 Character Configuration")

    num_characters = st.sidebar.slider(
        "Number of Main Characters",
        min_value=3,
        max_value=10,
        value=5,
        step=1,
        help="How many major characters will drive your story. These will be tracked throughout the narrative.",
        key="num_characters_slider"
    )

    # Optional: Show character distribution hint
    with st.sidebar.expander("ℹ️ Character Distribution Guide"):
        st.write(f"""
        **For {num_characters} characters:**
        - ~{max(1, num_characters // 3)} Main protagonists
        - ~{max(1, num_characters // 2)} Supporting characters
        - ~{max(1, num_characters - (num_characters // 3) - (num_characters // 2))} Minor roles
        
        Characters will be automatically tracked and their fates monitored.
        """)

    # Store in session state for access across reruns
    if 'num_characters' not in st.session_state:
        st.session_state.num_characters = num_characters
    else:
        st.session_state.num_characters = num_characters
    
    st.divider()
    
    # Custom Input
    st.subheader("✏️ Custom Details")
    custom_input = st.text_area(
        "Enter specific details (optional):",
        height=100,
        placeholder="e.g., A kingdom built inside a massive tree, ruled by dragon riders...",
        help="Provide specific context, characters, places, or events to incorporate"
    )
    
    st.divider()
    
    # === GENERATION PARAMETERS (ENHANCED WITH TOOLTIPS) ===
    st.markdown("### 🎛️ Generation Parameters")
    
    # Time Span Parameter with tooltip
    st.markdown("#### ⏱️ Time Span")
    col1, col2 = st.columns([5, 1])
    with col1:
        time_span_value = st.select_slider(
            label="Time Span",
            options=['brief', 'moderate', 'epic'],
            value='moderate',
            key='time_span_slider',
            label_visibility='collapsed'
        )
    with col2:
        st.markdown("", help="""
**Time Span** controls the chronology's temporal scope:

• **Brief** (decades): 
  - Covers 20-100 years
  - 3-5 major events
  - Target: 500-700 words
  - Example: A kingdom's founding decade

• **Moderate** (centuries):
  - Covers 100-500 years
  - 5-8 major events
  - Target: 650-900 words
  - Example: Rise and fall of a dynasty

• **Epic** (millennia):
  - Covers 500+ years
  - 8-12 major events
  - Target: 800-1000 words
  - Example: Entire civilization history
        """)
    
    # Show estimated word count
    time_span_estimates = {
        'brief': '500-700',
        'moderate': '650-900',
        'epic': '800-1000'
    }
    st.caption(f"📊 Estimated: {time_span_estimates[time_span_value]} words")
    
    st.markdown("")  # Spacing
    
    # Event Density Parameter with tooltip
    st.markdown("#### 📊 Event Density")
    col1, col2 = st.columns([5, 1])
    with col1:
        event_density_value = st.select_slider(
            label="Event Density",
            options=['sparse', 'moderate', 'rich'],
            value='moderate',
            key='event_density_slider',
            label_visibility='collapsed'
        )
    with col2:
        st.markdown("", help="""
**Event Density** controls detail level and number of events:

• **Sparse** (3-5 events):
  - Major milestones only
  - Broad strokes narrative
  - More space between events
  - Example: Key turning points only

• **Moderate** (5-8 events):
  - Balanced coverage
  - Important events with context
  - Recommended for most uses

• **Rich** (8-12 events):
  - Detailed chronology
  - Many interconnected events
  - Dense narrative
  - Example: Year-by-year coverage
        """)
    
    # Show event count estimate
    event_counts = {
        'sparse': '3-5 events',
        'moderate': '5-8 events',
        'rich': '8-12 events'
    }
    st.caption(f"📈 Expected: {event_counts[event_density_value]}")
    
    st.markdown("")  # Spacing
    
    # Narrative Focus Parameter with tooltip
    st.markdown("#### 🎯 Narrative Focus")
    col1, col2 = st.columns([5, 1])
    with col1:
        narrative_focus_value = st.selectbox(
            label="Narrative Focus",
            options=['political', 'cultural', 'military', 'economic', 'personal'],
            index=0,
            key='narrative_focus_select',
            label_visibility='collapsed'
        )
    with col2:
        st.markdown("", help="""
**Narrative Focus** shapes content emphasis:

• **Political**: Governments, leaders, alliances, treaties
  - Focus on power dynamics and governance

• **Cultural**: Arts, traditions, religions, customs
  - Focus on societal values and cultural evolution

• **Military**: Wars, battles, conquests, defenses
  - Focus on conflicts and military campaigns

• **Economic**: Trade, resources, wealth, commerce
  - Focus on prosperity and economic systems

• **Personal**: Individuals, families, relationships
  - Focus on human stories and lineages
        """)
    
    focus_icons = {
        'political': '🏛️',
        'cultural': '🎨',
        'military': '⚔️',
        'economic': '💰',
        'personal': '👥'
    }
    st.caption(f"{focus_icons[narrative_focus_value]} Focus: {narrative_focus_value.capitalize()}")
    
    st.markdown("")  # Spacing
    
    # Multi-Stage Generation with tooltip
    col1, col2 = st.columns([5, 1])
    with col1:
        use_multistage = st.checkbox(
            "Enable Multi-Stage Generation",
            value=True,
            key='multistage_checkbox'
        )
    with col2:
        st.markdown("", help="""
**Multi-Stage Generation** uses a two-phase process:

✅ **Enabled** (Recommended):
  - Stage 1: Generate skeleton structure
  - Stage 2: Refine with entity tracking
  - Higher quality, more coherent output
  - Takes ~25-30 seconds

❌ **Disabled** (Faster):
  - Single-pass generation
  - Faster (~10-15 seconds)
  - Lower coherence and consistency
  - Not recommended for final outputs
        """)
    
    # Visual indicator for multi-stage
    if use_multistage:
        st.success("✨ Quality mode: Multi-stage pipeline active")
    else:
        st.warning("⚡ Speed mode: Single-stage generation")

    st.divider()
    
    # === PARAMETER VALIDATION SUMMARY ===
    st.markdown("### 📋 Generation Preview")
    
    # Calculate estimated metrics
    time_multiplier = {'brief': 0.7, 'moderate': 0.85, 'epic': 1.0}
    density_multiplier = {'sparse': 0.8, 'moderate': 1.0, 'rich': 1.2}
    
    base_word_estimate = 750  # Middle of 500-1000 range
    estimated_words = int(
        base_word_estimate * 
        time_multiplier[time_span_value] * 
        density_multiplier[event_density_value]
    )
    
    # Clamp to valid range
    estimated_words = max(500, min(1000, estimated_words))
    
    # Calculate estimated events
    event_base = {'sparse': 4, 'moderate': 6, 'rich': 10}
    estimated_events = event_base[event_density_value]
    
    # Display metrics in columns
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="Est. Word Count",
            value=f"~{estimated_words}",
            help="Estimated final word count based on your parameters"
        )
    
    with metric_col2:
        st.metric(
            label="Est. Events",
            value=f"~{estimated_events}",
            help="Approximate number of major events in the chronology"
        )
    
    with metric_col3:
        gen_time = "25-30s" if use_multistage else "10-15s"
        st.metric(
            label="Est. Time",
            value=gen_time,
            help="Approximate generation time"
        )
    
    # Show parameter combination insights
    st.info(f"""
    **Configuration:** {time_span_value.capitalize()} timeline with {event_density_value} detail, 
    focusing on {narrative_focus_value} aspects.
    
    **Expected:** ~{estimated_words} word chronology with ~{estimated_events} major events.
    """)
    
    st.divider()
    
    # Generation button
    generate_button = st.button("🚀 Generate Chronology", type="primary", use_container_width=True)

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📖 Generated Content")
    
    if generate_button:
        with st.spinner("🔄 Generating chronology..."):
            try:
                result = st.session_state.generator.generate(
                    theme=theme,
                    custom_input=custom_input,
                    time_span=time_span_value,
                    event_density=event_density_value,
                    narrative_focus=narrative_focus_value,
                    use_multi_stage=use_multistage,
                    session_manager=st.session_state.session_manager
                )
                
                # Store in session state
                st.session_state.current_result = result
                st.session_state.generation_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "theme": theme,
                    "word_count": result['word_count']
                })
                
                if result['success']:
                    st.success("✅ Generation completed successfully!")
                else:
                    st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error during generation: {str(e)}")
    
    # Display generated content
    if 'current_result' in st.session_state and st.session_state.current_result:
        result = st.session_state.current_result
        
        if result.get('success'):
            
            # Extract the generated content
            content = result.get('content', '')
            word_count = result.get('word_count', 0)
            
            # Display the generated chronology
            st.markdown(content)
            
            # === EXPORT OPTIONS ===
            st.markdown("---")
            st.markdown("### 💾 Export Options")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                st.download_button(
                    label="📄 Download TXT",
                    data=content,
                    file_name=f"{result.get('theme', 'chronology')}_{result.get('timestamp', '')}.txt",
                    mime="text/plain"
                )
            
            with export_col2:
                import json
                json_data = json.dumps(result, indent=2)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_data,
                    file_name=f"{result.get('theme', 'chronology')}_{result.get('timestamp', '')}.json",
                    mime="application/json"
                )
            
            with export_col3:
                if st.button("💾 Save to Output Folder"):
                    try:
                        import os
                        from datetime import datetime
                        
                        # Create output directory if it doesn't exist
                        os.makedirs('output', exist_ok=True)
                        
                        # Generate filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        theme_clean = result.get('theme', 'chronology').replace(' ', '_')
                        filename = f"output/{theme_clean}_{timestamp}.txt"
                        
                        # Save file
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)
                            f.write("\n\n" + "="*60 + "\n")
                            f.write("METADATA\n")
                            f.write("="*60 + "\n")
                            f.write(json.dumps(result, indent=2))
                        
                        st.success(f"✅ Saved to: {filename}")
                    except Exception as e:
                        st.error(f"❌ Error saving file: {e}")

with col2:
        # CHARACTER ROSTER DISPLAY ===
    st.header("👥 Character Roster")
    
    active_chars = st.session_state.session_manager.character_manager.get_active_characters()
    deceased_chars = st.session_state.session_manager.character_manager.get_deceased_characters()
    
    if active_chars:
        st.markdown("**Active Characters:**")
        for char in active_chars:
            st.markdown(f"- ✅ {char.name} ({char.role})")
    else:
        st.caption("No characters yet")
    
    if deceased_chars:
        st.markdown("**Deceased:**")
        for char in deceased_chars:
            st.markdown(f"- 💀 {char.name}")
    
    st.divider()
    
    if 'current_result' in st.session_state and st.session_state.current_result:
        result = st.session_state.current_result

        if result.get('success'):

            # === METADATA & EVALUATION SECTION ===
            st.markdown("---")
            st.markdown("## 📊 Metadata & Evaluation")

            # === EVENT CHAIN DISPLAY ===
            st.markdown("### 📊 Event Chain")
            
            events = st.session_state.session_manager.event_chain.events
            if events:
                st.caption(f"Total events in chain: {len(events)}")
                
                with st.expander("View Event Summaries", expanded=False):
                    for event in events:
                        st.markdown(f"**Event {event.event_number}:**")
                        st.caption(event.summary if event.summary else "No summary")
                        if event.affected_characters:
                            st.caption(f"Characters: {', '.join(event.affected_characters)}")
                        st.markdown("---")
            else:
                st.caption("No events in chain yet")
            
            st.divider()
            
            # === QUALITY METRICS WITH COLOR CODING ===
            st.markdown("### 📈 Quality Metrics")
            
            generation_time = result.get('generation_time_seconds', 0)
            
            # Create 3 columns for metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                # Word count with color coding
                if 500 <= word_count <= 1000:
                    status_icon = "✅"
                    status_text = "Within target"
                    status_color = "green"
                    percentage = int((word_count / 1000) * 100)
                elif 1000 < word_count <= 1200:
                    status_icon = "⚠️"
                    status_text = "Slightly over"
                    status_color = "orange"
                    percentage = int((word_count / 1000) * 100)
                elif word_count > 1200:
                    status_icon = "❌"
                    status_text = "Significantly over"
                    status_color = "red"
                    percentage = 120
                else:  # word_count < 500
                    status_icon = "⚠️"
                    status_text = "Under target"
                    status_color = "orange"
                    percentage = int((word_count / 1000) * 100)
                
                st.metric(
                    label="Word Count",
                    value=word_count,
                    delta=f"{word_count - 750} from ideal",
                    help="Target: 500-1,000 words. Ideal: 750 words"
                )
                
                # Progress bar for word count
                st.progress(min(percentage / 100, 1.0))
                st.markdown(f":{status_color}[{status_icon} {status_text} ({percentage}% of max)]")
            
            with metric_col2:
                st.metric(
                    label="Generation Time",
                    value=f"{generation_time}s",
                    help="Time taken to generate the chronology"
                )
                
                # Performance indicator
                if generation_time < 15:
                    st.markdown(":green[⚡ Fast generation]")
                elif generation_time < 30:
                    st.markdown(":blue[⏱️ Normal speed]")
                else:
                    st.markdown(":orange[🐢 Slower (high quality)]")
            
            with metric_col3:
                model_name = result.get('model', 'Unknown')
                # Extract short model name
                if 'gemini-2.0' in model_name.lower():
                    display_name = "Gemini 2.0"
                elif 'gemini-1.5' in model_name.lower():
                    display_name = "Gemini 1.5"
                else:
                    display_name = "Gemini"
                
                st.metric(
                    label="Model Used",
                    value=display_name,
                    help=f"Full model: {model_name}"
                )
                
                # Multi-stage indicator
                params = result.get('parameters', {})
                if params.get('multi_stage'):
                    st.markdown(":blue[✨ Multi-stage pipeline]")
                else:
                    st.markdown(":gray[⚡ Single-stage]")
            
            # === QUALITY SCORE CALCULATION ===
            st.markdown("---")
            st.markdown("### 🎯 Quality Assessment")
            
            # Calculate overall quality score
            quality_scores = {}
            
            # 1. Word Count Score (40 points max)
            if 500 <= word_count <= 1000:
                word_score = 40
            elif 1000 < word_count <= 1100 or 450 <= word_count < 500:
                word_score = 30
            elif 1100 < word_count <= 1200 or 400 <= word_count < 450:
                word_score = 20
            else:
                word_score = 10
            quality_scores['Word Count Compliance'] = word_score
            
            # 2. Entity Tracking Score (30 points max)
            entities = result.get('entities_tracked', {})
            char_count = len(entities.get('characters', []))
            place_count = len(entities.get('places', []))
            
            if char_count >= 3 and place_count >= 2:
                entity_score = 30
            elif char_count >= 2 or place_count >= 1:
                entity_score = 20
            else:
                entity_score = 10
            quality_scores['Entity Consistency'] = entity_score
            
            # 3. Generation Method Score (30 points max)
            if params.get('multi_stage'):
                method_score = 30
            else:
                method_score = 15
            quality_scores['Generation Quality'] = method_score
            
            # Calculate total score
            total_score = sum(quality_scores.values())
            max_score = 100
            
            # Display quality score with color coding
            score_col1, score_col2 = st.columns([2, 3])
            
            with score_col1:
                # Overall score with color
                if total_score >= 90:
                    score_color = "green"
                    score_label = "Excellent"
                    score_emoji = "🏆"
                elif total_score >= 75:
                    score_color = "blue"
                    score_label = "Good"
                    score_emoji = "✅"
                elif total_score >= 60:
                    score_color = "orange"
                    score_label = "Fair"
                    score_emoji = "⚠️"
                else:
                    score_color = "red"
                    score_label = "Needs Improvement"
                    score_emoji = "❌"
                
                st.markdown(f"### :{score_color}[{score_emoji} Overall Score: {total_score}/100]")
                st.markdown(f"**Quality Grade:** :{score_color}[{score_label}]")
                
                # Progress bar for overall score
                st.progress(total_score / 100)
            
            with score_col2:
                st.markdown("#### Score Breakdown")
                
                # Display individual scores
                for category, score in quality_scores.items():
                    max_category_score = 40 if 'Word' in category else 30
                    percentage = (score / max_category_score) * 100
                    
                    if percentage >= 80:
                        icon = "✅"
                        color = "green"
                    elif percentage >= 60:
                        icon = "⚠️"
                        color = "orange"
                    else:
                        icon = "❌"
                        color = "red"
                    
                    st.markdown(f":{color}[{icon} **{category}:** {score}/{max_category_score} ({int(percentage)}%)]")
    
            # === GENERATION STAGES (if multi-stage was used) ===
            if result.get('stages'):
                st.markdown("---")
                with st.expander("🔄 Generation Stages (Multi-Stage Pipeline)", expanded=False):
                    stages_data = result['stages']

                    # Handle dictionary format
                    if isinstance(stages_data, dict):
                        st.markdown("#### 📊 Pipeline Performance")
                        # Display stage metrics side by side
                        stage_col1, stage_col2, stage_col3 = st.columns(3)
                        with stage_col1:
                            stage1_words = stages_data.get('stage1_word_count', 0)
                            st.metric(
                                label="📝 Stage 1: Skeleton",
                                value=f"{stage1_words} words",
                                help="Initial chronology structure with core events"
                            )
                        with stage_col2:
                            stage2_words = stages_data.get('stage2_word_count', 0)
                            word_diff = stage2_words - stage1_words
                            st.metric(
                                label="✨ Stage 2: Refined",
                                value=f"{stage2_words} words",
                                delta=f"{word_diff:+d} words",
                                help="Enhanced with entity tracking and coherence improvements"
                            )
                        with stage_col3:
                            if word_diff > 0:
                                improvement = ((word_diff / stage1_words) * 100) if stage1_words > 0 else 0
                                st.metric(
                                    label="📈 Expansion",
                                    value=f"{improvement:.1f}%",
                                    help="Percentage increase from Stage 1 to Stage 2"
                                )
                            else:
                                st.metric(
                                    label="✂️ Trimmed",
                                    value=f"{abs(word_diff)} words",
                                    help="Content was trimmed to meet word count limits"
                                )
                        # Show Stage 1 preview
                        if stages_data.get('stage1_preview'):
                            st.markdown("---")
                            st.markdown("##### 📄 Stage 1 Preview (Initial Skeleton)")
                            st.text_area(
                                label="Initial skeleton content",
                                value=stages_data['stage1_preview'],
                                height=150,
                                disabled=True,
                                label_visibility="collapsed"
                            )
                        # Explain the process
                        st.markdown("---")
                        st.info(
                            "🔄 **Multi-Stage Pipeline Process:**\n\n"
                            "**Stage 1** generates the skeleton structure with core events and entities. "
                            "**Stage 2** refines the content by improving coherence, expanding details, and ensuring narrative flow. "
                            "Stage transition metrics and previews are shown above."
                        )
                
                    # Handle list format (backward compatibility)
                    elif isinstance(stages_data, list):
                        for stage_item in stages_data:
                            if isinstance(stage_item, dict):
                                stage_num = stage_item.get('stage', '?')
                                word_count = stage_item.get('word_count', 'N/A')
                                st.write(f"**Stage {stage_num}:** {word_count} words")
                                
                                if stage_item.get('preview'):
                                    with st.expander(f"View Stage {stage_num} Preview"):
                                        st.text(stage_item['preview'])
                    
                    else:
                        st.warning("⚠️ Stages data format not recognized")
    
    # === GENERATION HISTORY ===
    st.divider()
    st.subheader("📜 Generation History")
    if st.session_state.generation_history:
        for i, item in enumerate(reversed(st.session_state.generation_history[-5:]), 1):
            st.caption(f"{i}. {item['timestamp']} - {item['theme']} ({item['word_count']} words)")
    else:
        st.caption("No generations yet")

# Footer
st.divider()
st.caption("🎓 Generative Historical Fiction Tool By Technologia")
