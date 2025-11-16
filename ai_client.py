
"""
Enhanced AI client with grammar-based prompts, state tracking, and parameters
"""
import google.generativeai as genai
from datetime import datetime
import time
from config import Config
from prompt_grammar import PromptGrammar
from stateful_generator import StatefulHistoryGenerator
from session_manager import SessionManager

class HistoricalFictionGenerator:
    """Enhanced generator with course concepts applied"""
    
    def __init__(self):
        Config.validate()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Model selection with fallback
        model_list = list(genai.list_models())
        available_models = [
            m.name for m in model_list
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        
        fallback_models = [
            Config.MODEL_NAME,
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-2.0-flash-exp"
        ]
        
        selected = None
        for candidate in fallback_models:
            for available in available_models:
                if candidate == available or candidate == available.replace("models/", "") or f"models/{candidate}" == available:
                    selected = available
                    break
            if selected:
                break
        
        if not selected and available_models:
            selected = available_models[0]
        
        if not selected:
            raise RuntimeError("No suitable Gemini models found")
        
        print(f"✓ Using model: {selected}")
        self.model_name = selected
        self.model = genai.GenerativeModel(self.model_name)
        
    def generate(self, theme, custom_input="", time_span="moderate",
                event_density="moderate", narrative_focus="political",
                use_multi_stage=True, session_manager=None, num_characters=5,
                persona_name="Smooth Storyteller"):
        """
        Generate with ALL course concepts applied + NEW session integration
        """
        start_time = time.time()
        
        try:
            # Get session manager (use provided or create temporary)
            if session_manager is None:
                session_manager = SessionManager()
                session_manager.update_metadata(theme=theme)
            
            # Increment event number
            current_event = session_manager.metadata['generation_count'] + 1
            session_manager.character_manager.update_event_number(current_event)
            
            # Get character roster summary
            character_roster_summary = session_manager.character_manager.get_roster_summary()
            
            # Get causal context (if events exist)
            causal_context = ""
            if session_manager.event_chain.events:
                causal_context = session_manager.event_chain.build_causal_prompt(
                    next_event_number=current_event,
                    character_roster=character_roster_summary
                )

            # Get persona instructions
            from config import Config
            persona_config = Config.PERSONA_PRESETS.get(persona_name, Config.PERSONA_PRESETS[Config.DEFAULT_PERSONA])
            persona_instructions = persona_config['instructions']
            persona_temperature = persona_config['temperature']
            
            # TECHNIQUE 1: Grammar-based prompt construction WITH character/causal context
            base_prompt = PromptGrammar.build_prompt(
                theme=theme,
                custom_input=custom_input,
                time_span=time_span,
                event_density=event_density,
                narrative_focus=narrative_focus,
                word_range=f"{Config.MIN_WORDS}-{Config.MAX_WORDS} words",
                character_roster_summary=character_roster_summary,
                causal_context=causal_context,
                num_characters=num_characters,
                persona_instructions=persona_instructions
            )

            def is_streamlit_available():
                """Check if Streamlit is available and in active context"""
                try:
                    import streamlit as st
                    from streamlit.runtime.scriptrunner import get_script_run_ctx
                    return get_script_run_ctx() is not None
                except:
                    return False

            # Then in your code:
            if session_manager:
                if is_streamlit_available():
                    import streamlit as st
                    with st.expander("🐛 DEBUG: View Generated Prompt", expanded=False):
                        st.code(base_prompt, language="text")
            
            # TECHNIQUE 2 & 3: Multi-stage pipeline with state tracking
            if use_multi_stage:
                stateful_gen = StatefulHistoryGenerator(self.model)
                result = stateful_gen.generate_with_state(
                    base_prompt=base_prompt,
                    theme=theme,
                    custom_input=custom_input,
                    stages=2,
                    temperature=persona_temperature,
                    max_tokens=Config.MAX_TOKENS,
                    session_manager=session_manager  # Pass session manager
                )
                
                if not result["success"]:
                    raise Exception(result.get("error", "Generation failed"))
                
                content = result["final_text"]
                entities = result["entities"]
                stages_info = result["stages"]
                
            else:
                # Single-stage generation
                response = self.model.generate_content(
                    base_prompt,
                    generation_config={
                        "temperature": Config.TEMPERATURE,
                        "max_output_tokens": Config.MAX_TOKENS
                    }
                )
                
                content = self._extract_text(response)
                entities = {}
                stages_info = []
            
            if not content:
                raise Exception("No content generated")
            
            if is_streamlit_available():
                import streamlit as st
                with st.expander("🐛 DEBUG: View Generated Content", expanded=False):
                    st.code(content, language="text")
            
            # Update session with generated content
            event_node = session_manager.event_chain.add_event(current_event, content)

            # Separate content from metadata
            narrative_content, character_metadata = self._separate_content_and_metadata(content)

            # Update content to be ONLY the narrative (without metadata)
            content = narrative_content
            
            # Extract and track characters from generated text
            # ONLY if this is the first event (to establish roster)
            if current_event == 1:
                # Set story-based session ID on first generation
                session_manager.set_story_context(theme, custom_input)
                
                if character_metadata:
                    # Extract from structured metadata (PREFERRED METHOD)
                    print(f"✅ Using structured metadata extraction")
                    import re
                    for char_line in character_metadata:
                        # Parse: "1. King Aldric III - Role: main"
                        match = re.match(r'^\d+\.\s+(.+?)\s+-\s+Role:\s+(main|supporting|minor)', char_line, re.IGNORECASE)
                        if match:
                            char_name = match.group(1).strip()
                            role = match.group(2).strip().lower()
                            
                            if not session_manager.character_manager.get_character(char_name):
                                session_manager.character_manager.add_character(char_name, role=role, event_num=current_event)
                                print(f"  ✓ Added {char_name} ({role})")
                else:
                    # Fallback to old method if metadata section not found
                    print(f"⚠️ Metadata section not found, falling back to text extraction")
                    extracted_chars = session_manager.character_manager.extract_characters_from_text(content, max_characters=num_characters)
                    for char_name in extracted_chars:
                        if not session_manager.character_manager.get_character(char_name):
                            role = session_manager.character_manager.determine_character_role(char_name, content)
                            session_manager.character_manager.add_character(char_name, role=role, event_num=current_event)

            # Analyze event for consequences AND deaths
            session_manager.event_chain.analyze_event_and_update(
                event_node, 
                character_manager=session_manager.character_manager
            )
            
            # Validate no dead characters appear
            is_valid, violations = session_manager.character_manager.validate_character_usage(content)
            if not is_valid:
                print(f"⚠️ Warning: Dead characters detected in output: {violations}")
            
            # Increment generation count
            session_manager.increment_generation_count()
            
            word_count = len(content.split())
            generation_time = time.time() - start_time
            
            # Build comprehensive result
            result = {
                "success": True,
                "theme": theme,
                "custom_input": custom_input,
                "content": content,
                "word_count": word_count,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "generation_time_seconds": round(generation_time, 2),
                "tokens_used": "-",
                "prompt_tokens": "-",
                "completion_tokens": "-",
                "meets_requirements": Config.MIN_WORDS <= word_count <= Config.MAX_WORDS,
                "error": None,
                "parameters": {
                    "time_span": time_span,
                    "event_density": event_density,
                    "narrative_focus": narrative_focus,
                    "multi_stage": use_multi_stage
                },
                "entities_tracked": entities,
                "stages": stages_info,
                # NEW: Session information
                "session_id": session_manager.session_id,
                "event_number": current_event,
                "character_validation": {
                    "is_valid": is_valid,
                    "violations": violations
                }
            }
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            return {
                "success": False,
                "theme": theme,
                "custom_input": custom_input,
                "content": None,
                "word_count": 0,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "generation_time_seconds": round(generation_time, 2),
                "tokens_used": 0,
                "meets_requirements": False,
                "error": str(e),
                "parameters": {
                    "time_span": time_span,
                    "event_density": event_density,
                    "narrative_focus": narrative_focus,
                    "multi_stage": use_multi_stage
                },
                "entities_tracked": {},
                "stages": []
            }

    def _extract_text(self, response):
        """Safely extract text from Gemini response"""
        if hasattr(response, "candidates") and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "text"):
                            return part.text
        try:
            return response.text
        except:
            return None
    
    def _separate_content_and_metadata(self, raw_output):
        """
        Separate narrative content from character metadata section
        
        Returns:
            tuple: (narrative_content, character_metadata_lines)
        """
        # Look for the separator pattern
        separator_pattern = r'\n-{3,}\s*\n'
        
        import re
        match = re.search(separator_pattern, raw_output, re.IGNORECASE)
        
        if match:
            # Split at the separator
            narrative = raw_output[:match.start()].strip()
            metadata_section = raw_output[match.end():].strip()
            
            # Extract character lines (format: "1. Name - Role: main")
            char_lines = []
            for line in metadata_section.split('\n'):
                line = line.strip()
                # Match: "1. Character Name - Role: main"
                if re.match(r'^\d+\.\s+.+\s+-\s+Role:\s+(main|supporting|minor)', line, re.IGNORECASE):
                    char_lines.append(line)
            
            print(f"✅ Found metadata section with {len(char_lines)} characters")
            return narrative, char_lines
        else:
            print("⚠️ No metadata section found in output")
            return raw_output, []

    def generate_with_character_validation(self, max_retries=1, **kwargs):
        """
        Generate content and retry if character count is wrong.
        Only applies to first generation (when characters are introduced).
        
        This wrapper ensures the AI generates exactly the requested number of characters,
        retrying up to max_retries times if the count doesn't match.
        
        Args:
            max_retries: Number of retry attempts (default 1, recommend 1-2)
            **kwargs: Same parameters as generate() method
            
        Returns:
            Same dict as generate() method with 'success', 'content', 'error' keys
            
        Example:
            result = generator.generate_with_character_validation(
                max_retries=1,
                theme="Fantasy Kingdom",
                num_characters=5,
                session_manager=my_session
            )
        """
        num_characters = kwargs.get('num_characters', 5)
        session_manager = kwargs.get('session_manager')
        
        # Only validate on first generation (when characters are introduced)
        if not session_manager or session_manager.metadata.get('generation_count', 0) > 0:
            # Not first generation, skip validation and use normal generate
            return self.generate(**kwargs)
        
        print(f"\\n{'='*70}")
        print(f"CHARACTER COUNT VALIDATION ENABLED")
        print(f"Target: {num_characters} characters | Max attempts: {max_retries + 1}")
        print(f"{'='*70}\\n")
        
        for attempt in range(max_retries + 1):
            print(f"\\n{'='*70}")
            print(f"GENERATION ATTEMPT {attempt + 1}/{max_retries + 1}")
            print(f"{'='*70}")
            
            result = self.generate(**kwargs)
            
            if not result['success']:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                return result
            
            # Check character count
            actual_count = len(session_manager.character_manager.roster)
            
            print(f"\\n{'='*70}")
            print(f"CHARACTER COUNT CHECK")
            print(f"Target: {num_characters} | Actual: {actual_count}")
            print(f"{'='*70}")
            
            if actual_count == num_characters:
                print(f"✅ CHARACTER COUNT CORRECT: {actual_count}/{num_characters}")
                print(f"✅ Validation passed on attempt {attempt + 1}")
                print(f"{'='*70}\\n")
                return result
            
            print(f"⚠️  CHARACTER COUNT MISMATCH: {actual_count}/{num_characters}")
            
            if attempt < max_retries:
                print(f"\\n🔄 RETRY TRIGGERED")
                print(f"   Resetting session and retrying with emphasis...")
                print(f"   Attempts remaining: {max_retries - attempt}")
                
                # Reset session for retry
                session_manager.character_manager.roster.clear()
                session_manager.event_chain.events.clear()
                session_manager.metadata['generation_count'] = 0
                
                # Add strong emphasis to custom_input
                original_input = kwargs.get('custom_input', '')
                emphasis = f"""
🚨 CRITICAL REQUIREMENT 🚨
You MUST generate EXACTLY {num_characters} main characters.
Previous attempt generated {actual_count} characters, which is WRONG.
Count carefully: {num_characters} characters total.
List all {num_characters} characters in the CHARACTERS section at the end.

"""
                kwargs['custom_input'] = emphasis + original_input
                
            else:
                print(f"\\n❌ VALIDATION FAILED after {max_retries + 1} attempts")
                print(f"   Final count: {actual_count} (expected {num_characters})")
                print(f"   Accepting result with incorrect count.")
                print(f"{'='*70}\\n")
                return result
        
        return result

    def batch_generate(self, test_cases):
        """
        Generate content for multiple test cases
        Now with enhanced parameter support
        """
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"Generating {i}/{len(test_cases)}: {test_case['theme']}")
            
            # Extract parameters from test case
            result = self.generate(
                theme=test_case['theme'],
                custom_input=test_case.get('custom_input', ''),
                time_span=test_case.get('time_span', 'moderate'),
                event_density=test_case.get('event_density', 'moderate'),
                narrative_focus=test_case.get('narrative_focus', 'political'),
                use_multi_stage=test_case.get('use_multi_stage', True)
            )
            results.append(result)
            
            if i < len(test_cases):
                time.sleep(1)
        
        return results
