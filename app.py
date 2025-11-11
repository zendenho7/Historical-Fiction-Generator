
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
    except Exception as e:
        st.error(f"❌ Failed to initialize generator: {str(e)}")
        st.info("💡 Make sure your `.env` file is configured with GEMINI_API_KEY")
        st.stop()

# Header
st.markdown('<div class="main-header">📚 Historical Fiction Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Chronology Generation with Advanced PCG Techniques</div>', unsafe_allow_html=True)

# Sidebar - Configuration and Parameters
with st.sidebar:
    st.header("⚙️ Configuration")
    
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
    
    # Custom Input
    st.subheader("✏️ Custom Details")
    custom_input = st.text_area(
        "Enter specific details (optional):",
        height=100,
        placeholder="e.g., A kingdom built inside a massive tree, ruled by dragon riders...",
        help="Provide specific context, characters, places, or events to incorporate"
    )
    
    st.divider()
    
    # Parameters
    st.subheader("🎛️ Generation Parameters")
    
    time_span = st.select_slider(
        "Time Span:",
        options=["brief", "moderate", "epic"],
        value="moderate",
        help="Brief: 50-100 years | Moderate: 200-500 years | Epic: 1000+ years"
    )
    
    event_density = st.select_slider(
        "Event Density:",
        options=["sparse", "moderate", "rich"],
        value="moderate",
        help="Sparse: 3-5 events | Moderate: 6-8 events | Rich: 10-12 events"
    )
    
    narrative_focus = st.selectbox(
        "Narrative Focus:",
        ["political", "cultural", "military", "economic", "personal"],
        help="Primary aspect of the chronology"
    )
    
    use_multi_stage = st.checkbox(
        "Enable Multi-Stage Generation",
        value=True,
        help="Uses 2-stage process for better coherence and entity tracking"
    )
    
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
                    time_span=time_span,
                    event_density=event_density,
                    narrative_focus=narrative_focus,
                    use_multi_stage=use_multi_stage
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
        
        if result['success']:
            # Content display
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.markdown(result['content'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download buttons
            st.subheader("💾 Export Options")
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            
            with col_dl1:
                # Text file download
                st.download_button(
                    label="📄 Download TXT",
                    data=result['content'],
                    file_name=f"chronology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col_dl2:
                # JSON download
                json_data = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_data,
                    file_name=f"chronology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col_dl3:
                # Save to output folder
                if st.button("💾 Save to Output Folder"):
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    txt_path = output_dir / f"chronology_{timestamp}.txt"
                    json_path = output_dir / f"chronology_{timestamp}.json"
                    
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(result['content'])
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    st.success(f"✅ Saved to output/ folder")

with col2:
    st.header("📊 Metadata & Evaluation")
    
    if 'current_result' in st.session_state and st.session_state.current_result:
        result = st.session_state.current_result
        
        # Quality metrics
        st.markdown('<div class="metadata-box">', unsafe_allow_html=True)
        st.subheader("📈 Quality Metrics")
        
        word_count = result['word_count']
        meets_req = result['meets_requirements']
        
        # Word count with color coding
        if meets_req:
            st.metric("Word Count", word_count, delta="✓ Within target", delta_color="normal")
        else:
            st.metric("Word Count", word_count, delta="⚠ Outside target", delta_color="off")
        
        st.metric("Generation Time", f"{result['generation_time_seconds']}s")
        st.metric("Model Used", result['model'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Parameters used
        st.subheader("🎛️ Parameters Used")
        params = result.get('parameters', {})
        st.json({
            "Theme": result['theme'],
            "Time Span": params.get('time_span', 'N/A'),
            "Event Density": params.get('event_density', 'N/A'),
            "Narrative Focus": params.get('narrative_focus', 'N/A'),
            "Multi-Stage": params.get('multi_stage', False),
            "Custom Input": result.get('custom_input', 'None')[:50] + "..." if len(result.get('custom_input', '')) > 50 else result.get('custom_input', 'None')
        })
        
        # Entity tracking (if available)
        if result.get('entities_tracked') and any(result['entities_tracked'].values()):
            st.subheader("🏷️ Entities Tracked")
            entities = result['entities_tracked']
            
            if entities.get('characters'):
                st.write("**Characters:**", ", ".join(entities['characters'][:5]))
            if entities.get('places'):
                st.write("**Places:**", ", ".join(entities['places'][:5]))
            if entities.get('items'):
                st.write("**Items:**", ", ".join(entities['items'][:3]))
        
        # Stage information (if multi-stage)
        if result.get('stages'):
            with st.expander("🔄 Generation Stages", expanded=False):
                for stage in result['stages']:
                    st.write(f"**Stage {stage['stage']}:** {stage['word_count']} words")
    
    else:
        st.info("👈 Configure parameters and click 'Generate Chronology' to begin")
    
    # Generation history
    st.divider()
    st.subheader("📜 Generation History")
    if st.session_state.generation_history:
        for i, item in enumerate(reversed(st.session_state.generation_history[-5:]), 1):
            st.caption(f"{i}. {item['timestamp']} - {item['theme']} ({item['word_count']} words)")
    else:
        st.caption("No generations yet")

# Footer
st.divider()
st.caption("🎓 Technical Design Project | Enhanced with Course Concepts (Grammar-based Prompts, State Management, Multi-Stage Pipeline)")
