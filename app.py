
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

#from input_validator import InputValidator 

st.session_state.needs_rerun = False

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
        from session_manager import SessionManager
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
    
    #### 5️⃣ **Character Lifecycle Management**
    - **What it does:** Automatically tracks character births, deaths, and revivals throughout the narrative
    - **How it works:** 
      - Uses regex pattern matching to detect death events ("died", "was killed", "sacrificed", etc.)
      - Tracks revival events ("revived", "returned to life", "resurrected")
      - Maintains character status and history across multiple events
    - **Example:** If "Queen Lyra passes away" appears in Year 145, she's moved to deceased characters with cause of death tracked
    - **Impact:** Creates realistic character arcs with mortality consequences and potential magical revivals
    
    #### 6️⃣ **Causal Event Chain System**
    - **What it does:** Maintains explicit cause-and-effect relationships between events
    - **How it works:**
      - Each event stores a "hook" that leads to the next event
      - Tracks which characters are affected by each event
      - Creates narrative threads that span multiple events
    - **Example:** "Discovery of ancient artifact" (Event 1) → "Quest to retrieve it" (Event 2) → "Dragon encounter" (Event 3)
    - **Impact:** Produces coherent narratives with clear consequences and narrative momentum
    
    #### 7️⃣ **Session Persistence & Memory**
    - **What it does:** Saves and loads complete story sessions with all metadata
    - **How it works:**
      - Stores character rosters, event chains, and generation parameters in JSON format
      - Allows resuming stories across multiple sessions
      - Maintains character lifecycle data and event history
    - **Example:** Save "Kingdom of Eldoria" session, close app, reload it later with all 5 characters and their fates intact
    - **Impact:** Enables iterative story development and long-term narrative continuity
    
    #### 8️⃣ **Advanced Character Analytics**
    - **What it does:** Provides statistical analysis of character lifecycles and mortality
    - **How it works:**
      - Calculates mortality rates, revival counts, and character action histories
      - Tracks character appearances across events
      - Monitors active vs. deceased character ratios
    - **Example:** "Mortality Rate: 60% (3/5 characters deceased)", "Total Revivals: 1"
    - **Impact:** Gives insight into narrative pacing and character importance
    
    ---
    
    ### 📊 **Target Output Quality**
    - **Word Count:** 500-1,000 words (enforced with AI prompting + post-processing)
    - **Format:** Chronological narrative with clear temporal markers
    - **Quality:** Believable, coherent history with cause-effect relationships
    - **Character Tracking:** Automated lifecycle monitoring with death/revival detection
    
    ### 🔗 **External Resources Referenced**
    - GDC Talk: ["Procedurally Generating History in Caves of Qud"](https://www.youtube.com/watch?v=H0sLa1y3BW4)
    - Course Materials: Technical Design (Week 6, 9, 10)
    - Google Gemini AI API for content generation
    
    ### 📖 **How to Use**
    1. **Select a theme** from the dropdown (9 options available)
    2. **Set character count** using the slider (3-10 characters)
    3. **Adjust parameters** using sliders and dropdowns
    4. **Add custom details** (optional) to seed specific elements
    5. **Enable multi-stage generation** for higher quality (recommended)
    6. **Click "Generate Chronology"** and wait ~20-30 seconds
    7. **Monitor character fates** in the Character Roster (deaths/revivals tracked automatically)
    8. **Save your session** to preserve all progress
    9. **Export your results** in TXT or JSON format
    """)

st.markdown("---")  # Separator line

# Sidebar - Configuration and Parameters
with st.sidebar:
    st.header("⚙️ Configuration")

    # === SESSION CONTROLS ===
    st.subheader("💾 Session Management")

    # Initialize flags (at top of script, only once)
    if 'pending_action' not in st.session_state:
        st.session_state.pending_action = None
    if 'confirm_new_session' not in st.session_state:
        st.session_state.confirm_new_session = False

    # Get current session info for display
    current_session = st.session_state.session_manager
    gen_count = current_session.metadata.get('generation_count', 0)
    theme = current_session.metadata.get('theme', 'Untitled')

    # Show current session name prominently
    if gen_count > 0:
        # Extract readable parts from session ID
        session_display = current_session.session_id.replace('_', ' ')
        st.markdown(f"**📖 Current Story:** `{session_display}`")
        st.caption(f"Events: {gen_count} | Characters: {len(current_session.character_manager.roster)}")
    else:
        st.markdown("**📖 New Session** (not yet saved)")
        st.caption("Generate your first event to create a session")

    st.markdown("")  # Spacing

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        # Save button (only enabled after first generation)
        if gen_count > 0:
            if st.button("💾 Save", use_container_width=True, type="primary"):
                try:
                    filepath = current_session.save()
                    st.success("✅ Saved!")
                    # Extract just filename
                    filename = Path(filepath).name
                    st.caption(f"📁 {filename}")
                except Exception as e:
                    st.error(f"❌ Save failed: {e}")
        else:
            st.button("💾 Save", use_container_width=True, disabled=True, 
                    help="Generate content first to enable saving")

    with col2:
  
        # Check if we're in confirmation state
        if st.session_state.confirm_new_session:
            # Show confirmation button
            if st.button("⚠️ Confirm New", use_container_width=True, type="secondary", key="confirm_new_btn"):
                # Create new session
                from session_manager import SessionManager
                st.session_state.session_manager = SessionManager()
                st.session_state.current_session_id = st.session_state.session_manager.session_id
                st.session_state.confirm_new_session = False  # Reset flag
                st.session_state.pending_action = 'new'
        else:
            # Show normal new button
            if st.button("🔄 New", use_container_width=True, key="new_btn", help="Start new session"):
                if gen_count > 0:
                    # Has content - need confirmation
                    st.session_state.confirm_new_session = True
                    st.session_state.pending_action = 'new_confirm'  # Trigger rerun to show confirm button
                else:
                    # No content - safe to reset immediately
                    from session_manager import SessionManager
                    st.session_state.session_manager = SessionManager()
                    st.session_state.current_session_id = st.session_state.session_manager.session_id
                    st.session_state.pending_action = 'new'

    with col3:
        if gen_count > 0:
            with st.expander("✏️ Rename Session", expanded=False):
                st.caption("Give your story a custom name for easier identification")
                
                current_name = current_session.session_id
                new_name = st.text_input(
                    "Session name:",
                    value=current_name,
                    max_chars=50,
                    key="rename_input",
                    help="Letters, numbers, hyphens, and underscores only"
                )
                
                if st.button("💾 Update Name", key="rename_btn"):
                    # Validate name
                    import re
                    if re.match(r'^[\w\-]+$', new_name) and new_name != current_name:
                        # Rename session
                        old_filepath = current_session.sessions_dir / f"{current_name}.json"
                        
                        # Update session ID
                        current_session.session_id = new_name
                        
                        # Save with new name
                        new_filepath = current_session.save()
                        
                        # Delete old file
                        if old_filepath.exists():
                            old_filepath.unlink()
                        
                        st.success(f"✅ Renamed to: {new_name}")
                        st.session_state.current_session_id = new_name
                        st.session_state.needs_rerun = True

    # Show warning message if in confirmation state
    if st.session_state.confirm_new_session:
        st.warning("⚠️ **Unsaved changes will be lost!** Click '⚠️ Confirm New' to proceed, or click elsewhere to cancel.")

    # Load existing sessions
    st.markdown("")  # Spacing
    from session_manager import SessionManager
    available_sessions = SessionManager.list_available_sessions()

    if available_sessions:
        with st.expander("📂 Load Previous Session", expanded=False):
            # Group sessions by theme for better organization
            sessions_by_theme = {}
            for s in available_sessions:
                theme_key = s['theme'] or 'Untitled'
                if theme_key not in sessions_by_theme:
                    sessions_by_theme[theme_key] = []
                sessions_by_theme[theme_key].append(s)
            
            # Create human-readable session options
            session_options = {}
            for theme_key, sessions in sessions_by_theme.items():
                for s in sessions:
                    # Extract readable name from session_id
                    display_name = s['session_id'].replace('_', ' ')
                    
                    # Add metadata for context
                    events = s.get('events', 0)
                    chars = s.get('characters', 0)
                    last_mod = s.get('last_modified', '')
                    
                    # Parse timestamp
                    try:
                        from datetime import datetime
                        mod_time = datetime.fromisoformat(last_mod)
                        time_str = mod_time.strftime("%b %d, %H:%M")
                    except:
                        time_str = "Unknown"
                    
                    # Build display string
                    option_text = f"📖 {display_name} • {events} events, {chars} chars • {time_str}"
                    session_options[option_text] = s['session_id']
            
            if session_options:
                selected = st.selectbox(
                    "Choose a session to load:",
                    options=list(session_options.keys()),
                    key="session_select",
                    label_visibility="collapsed"
                )
                
                col_load, col_delete = st.columns([3, 1])
                
                with col_load:
                    if st.button("📂 Load Selected", key="load_btn", use_container_width=True, type="primary"):
                        try:
                            session_id = session_options[selected]
                            from session_manager import SessionManager
                            st.session_state.session_manager = SessionManager.load(session_id)
                            st.session_state.current_session_id = session_id
                            st.success(f"✅ Loaded successfully!")
                            st.session_state.needs_rerun = True
                        except Exception as e:
                            st.error(f"❌ Load failed: {e}")
                
                with col_delete:
                    # Initialize session state for delete confirmation
                    if 'delete_confirm_id' not in st.session_state:
                        st.session_state.delete_confirm_id = None
                    
                    session_id = session_options[selected]
                    
                    # First click: Show confirmation state
                    if st.session_state.delete_confirm_id != session_id:
                        if st.button("🗑️", key="delete_btn", help="Delete selected session"):
                            st.session_state.delete_confirm_id = session_id
                            st.session_state.needs_rerun = True
                    else:
                        # Second click: Confirm delete
                        if st.button("⚠️ Confirm", key="confirm_delete", type="secondary"):
                            try:
                                from session_manager import SessionManager
                                SessionManager.delete_session(session_id)
                                st.session_state.delete_confirm_id = None  # Reset confirmation
                                st.success("🗑️ Deleted!")
                                st.session_state.needs_rerun = True  # Refresh to update list
                            except Exception as e:
                                st.error(f"❌ Delete failed: {e}")
                                st.session_state.delete_confirm_id = None
            else:
                st.caption("No saved sessions found")
    else:
        st.caption("💡 No saved sessions yet. Generate content and click 'Save' to create one.")

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
    events = st.session_state.session_manager.event_chain.events
    if len(events) == 0:
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
            
    else:
        # AFTER FIRST GENERATION: Show locked count with reset option
        current_count = len(st.session_state.session_manager.character_manager.get_active_characters()) + len(st.session_state.session_manager.character_manager.get_deceased_characters())
        
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            st.metric(
                label="Character Count",
                value=current_count,
                help="Number of main characters in this session"
            )
        
        st.sidebar.caption(f"""
        🔒 Character count was set during the first generation.
        
        **Current roster:**
        - {len(st.session_state.session_manager.character_manager.get_active_characters())} active
        - {len(st.session_state.session_manager.character_manager.get_deceased_characters())} deceased
        
        Click 🔓 to reset and change character count (⚠️ clears current characters).
        """)
        
        st.divider()
    
    # Custom Input WITH VALIDATION
    st.subheader("✏️ Custom Details")

    # Initialize validation state
    if 'input_validation_warnings' not in st.session_state:
        st.session_state.input_validation_warnings = []

    custom_input = st.text_area(
        "Enter specific details (optional):",
        height=100,
        max_chars=500,  # Hard limit at UI level
        placeholder="e.g., A kingdom built inside a massive tree, ruled by dragon riders...",
        help="Provide specific context, characters, places, or events to incorporate (max 500 characters)",
        key="custom_input_field"
    )

    # Real-time validation
    if custom_input:
        from input_validator import InputValidator
        
        is_valid, error_msg, warnings = InputValidator.validate(custom_input)
        
        # Show character count
        char_count = len(custom_input)
        char_color = "green" if char_count <= 400 else "orange" if char_count <= 500 else "red"
        st.caption(f":{char_color}[{char_count}/500 characters]")
        
        # Show validation status
        if not is_valid:
            st.error(f"❌ {error_msg}")
            st.caption("Please revise your input before generating.")
        elif warnings:
            st.warning(f"⚠️ Warnings: {', '.join(warnings)}")
            st.caption("Your input is accepted but may produce unexpected results.")
        else:
            st.success("✅ Input validated successfully!")
    
    st.divider()

    # === PERSONA SELECTION ===
    with st.expander("🎭 Narrative Persona Settings", expanded=False):
        st.markdown("""
        **Persona controls how the AI writes your story:**
        - Pacing and flow
        - Emotional depth
        - Continuity style
        - Transition smoothness
        """)
        
        from config import Config
        
        persona_options = list(Config.PERSONA_PRESETS.keys())
        selected_persona = st.selectbox(
            "Choose narrative style:",
            options=persona_options,
            index=0,  # Default to "Smooth Storyteller"
            key="persona_select"
        )
        
        # Show persona description
        persona_info = Config.PERSONA_PRESETS[selected_persona]
        st.info(f"**{selected_persona}:** {persona_info['description']}")
        
        # Store in session state
        st.session_state.selected_persona = selected_persona

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
        # validation check
        if custom_input:
            is_valid, error_msg, warnings = InputValidator.validate(custom_input)
            
            if not is_valid:
                st.error(f"❌ {error_msg}")
                st.stop()  # Block generation
            elif warnings:
                st.warning(f"⚠️ {'; '.join(warnings)}")


        with st.spinner("🔄 Generating chronology..."):
            try:
                result = st.session_state.generator.generate_with_character_validation(
                    max_retries=1,
                    theme=theme,
                    custom_input=custom_input,
                    time_span=time_span_value,
                    event_density=event_density_value,
                    narrative_focus=narrative_focus_value,
                    use_multi_stage=use_multistage,
                    session_manager=st.session_state.session_manager,
                    num_characters=st.session_state.num_characters,
                    persona_name=st.session_state.get('selected_persona', 'Smooth Storyteller')
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

                    # FORCE CHARACTER ROSTER REFRESH
                    # Clear any cached character roster display
                    if 'last_character_count' not in st.session_state:
                        st.session_state.last_character_count = 0
                    
                    current_count = len(st.session_state.session_manager.character_manager.roster)
                    if current_count != st.session_state.last_character_count:
                        st.session_state.last_character_count = current_count    
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
    revived_chars = st.session_state.session_manager.character_manager.get_revived_characters()

    # === CHARACTER COUNT VALIDATION ===
    if active_chars or deceased_chars:
        target_count = st.session_state.get('num_characters', 5)
        actual_count = len(active_chars) + len(deceased_chars)

        # Show summary with validation
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Target Characters", target_count, help="Set before first generation")

        with col2:
            delta = actual_count - target_count
            delta_text = f"{delta:+d}" if delta != 0 else "Perfect"
            delta_color = "off" if delta == 0 else "inverse"
            
            st.metric("Actual Characters", actual_count, delta=delta_text, delta_color=delta_color)

        with col3:
            if actual_count == target_count:
                st.success("✅ Count matches!")
            elif actual_count < target_count:
                st.warning(f"⚠️ {target_count - actual_count} missing")
            else:
                st.error(f"❌ {actual_count - target_count} extra")

    # === ACTIVE CHARACTERS ===
    if active_chars:
        st.markdown("**Active Characters:**")
        for char in sorted(active_chars, key=lambda c: c.role):
            # Role-based emoji
            role_emoji = {
                'main': '⭐',
                'supporting': '✅', 
                'minor': '○'
            }.get(char.role, '✅')
            
            # Build display string
            display = f"{role_emoji} **{char.name}** ({char.role})"
            
            # 🆕 ADD REVIVAL INDICATOR
            if char.revival_event:
                display += f" ✨"  # Sparkle indicates revival
            
            # Add first appearance
            display += f" • Introduced: Event {char.first_appearance}"
            
            # 🆕 ADD REVIVAL INFO
            if char.revival_event:
                display += f" • Revived: Event {char.revival_event}"
            
            # Add action count
            if char.notable_actions:
                display += f" • {len(char.notable_actions)} actions"
            
            st.markdown(display)
            
            # Show latest action in small text
            if char.notable_actions:
                latest_action = char.notable_actions[-1]
                
                # 🆕 HIGHLIGHT REVIVAL IN LATEST ACTION
                if "Revived:" in latest_action:
                    st.caption(f"✨ {latest_action}")
                else:
                    st.caption(f"Latest: {latest_action}")
    else:
        st.caption("No characters yet")

    # === DECEASED CHARACTERS ===
    if deceased_chars:
        st.markdown("")  # Spacer
        with st.expander(f"⚰️ Deceased Characters ({len(deceased_chars)})", expanded=False):
            for char in deceased_chars:
                death_event = char.death_event if char.death_event else "Unknown"
                
                st.markdown(f"💀 **{char.name}** ({char.role})")
                st.caption(f"└─ Died in Event {death_event}")
                
                # Show death cause if available
                if char.notable_actions:
                    # Find the death action
                    death_action = None
                    for action in char.notable_actions:
                        if "Died:" in action:
                            death_action = action
                            break
                    
                    if death_action:
                        cause = death_action.replace("Died:", "").strip()
                        st.caption(f"└─ Cause: {cause}")
                
                st.markdown("")  # Spacer between characters

    # === REVIVAL HISTORY SECTION ===
    if revived_chars:
        st.markdown("")  # Spacer
        with st.expander(f"✨ Characters with Revival History ({len(revived_chars)})", expanded=False):
            for char in revived_chars:
                # Determine current status
                status_emoji = "✅" if char.status == "alive" else "💀"
                status_text = char.status.upper()
                
                st.markdown(f"🔄 **{char.name}** ({char.role}) - {status_emoji} {status_text}")
                
                # Death info
                if char.death_event:
                    st.caption(f"├─ 💀 Died: Event {char.death_event}")
                    
                    # Find death cause
                    death_action = None
                    for action in char.notable_actions:
                        if "Died:" in action:
                            death_action = action.replace("Died:", "").strip()
                            break
                    
                    if death_action:
                        # Truncate if too long
                        death_display = death_action[:80] + "..." if len(death_action) > 80 else death_action
                        st.caption(f"│  └─ {death_display}")
                
                # Revival info
                if char.revival_event:
                    st.caption(f"├─ ✨ Revived: Event {char.revival_event}")
                    
                    # Find revival reason
                    revival_reason = None
                    for action in char.notable_actions:
                        if "Revived:" in action:
                            revival_reason = action.replace("Revived:", "").strip()
                            break
                    
                    if revival_reason:
                        # Clean up the reason display
                        if " - " in revival_reason:
                            # Format: "via magic - context..."
                            parts = revival_reason.split(" - ", 1)
                            mechanism = parts
                            context = parts if len(parts) > 1 else ""
                            
                            st.caption(f"│  ├─ Method: {mechanism}")
                            if context:
                                context_display = context[:100] + "..." if len(context) > 100 else context
                                st.caption(f"│  └─ {context_display}")
                        else:
                            # Simple reason
                            reason_display = revival_reason[:100] + "..." if len(revival_reason) > 100 else revival_reason
                            st.caption(f"│  └─ {reason_display}")
                
                # Calculate lifecycle stats
                death_count = len([a for a in char.notable_actions if "Died:" in a])
                revival_count = len([a for a in char.notable_actions if "Revived:" in a])
                
                if death_count > 1 or revival_count > 1:
                    st.caption(f"└─ 📊 Deaths: {death_count} | Revivals: {revival_count}")
                
                st.markdown("")  # Spacer between characters

    # === LIFECYCLE STATISTICS ===
    if active_chars or deceased_chars:
        total_chars = len(active_chars) + len(deceased_chars)
        total_deaths = len(deceased_chars) + len([c for c in active_chars if c.death_event])
        total_revivals = len(revived_chars)
        
        if total_deaths > 0 or total_revivals > 0:
            st.markdown("")  # Spacer
            with st.expander("📊 Lifecycle Statistics", expanded=False):
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                
                with stat_col1:
                    st.metric("Total Deaths", total_deaths)
                
                with stat_col2:
                    st.metric("Total Revivals", total_revivals)
                
                with stat_col3:
                    mortality_rate = (len(deceased_chars) / total_chars * 100) if total_chars > 0 else 0
                    st.metric("Currently Dead", f"{mortality_rate:.0f}%")
    st.divider()
    
    if 'current_result' in st.session_state and st.session_state.current_result:
        result = st.session_state.current_result

        if result.get('success'):

            # === EVENT CHAIN DISPLAY ===
            st.markdown("### 📊 Event Chain")
            
            events = st.session_state.session_manager.event_chain.events
            if events:
                st.caption(f"Total events in chain: {len(events)}")
                
                # Create timeline visualization
                for i, event in enumerate(events):
                    with st.expander(f"**Event {event.event_number}**"):
   
                        # Event summary
                        st.caption(event.summary if event.summary else "No summary")
                        
                        # Characters involved
                        if event.affected_characters:
                            char_tags = ' '.join([f"`{c}`" for c in event.affected_characters[:3]])
                            st.markdown(f"👥 {char_tags}")
                        
                        # Hook to next event
                        if event.hook and i < len(events) - 1:
                            st.markdown(f"→ *{event.hook}*")
                    
                    if i < len(events) - 1:
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
            
            # === GENERATION STAGES (if multi-stage was used) ===
            if result.get('stages'):
                st.divider()
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
    
            st.divider()

    # === GENERATION HISTORY ===
    st.subheader("📜 Generation History")
    if st.session_state.generation_history:
        for i, item in enumerate(reversed(st.session_state.generation_history[-5:]), 1):
            st.caption(f"{i}. {item['timestamp']} - {item['theme']} ({item['word_count']} words)")
    else:
        st.caption("No generations yet")

if st.session_state.needs_rerun:
    st.session_state.needs_rerun = False
    st.rerun()

# Footer
st.divider()
st.caption("🎓 Generative Historical Fiction Tool By Technologia")
