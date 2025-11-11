
"""
Enhanced AI client with grammar-based prompts, state tracking, and parameters
"""
import google.generativeai as genai
from datetime import datetime
import time
from config import Config
from prompt_grammar import PromptGrammar
from stateful_generator import StatefulHistoryGenerator

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
                use_multi_stage=True):
        """
        Generate with ALL course concepts applied:
        - Grammar-based prompts
        - Parameter-driven variation
        - Multi-stage pipeline (optional)
        - State tracking
        """
        start_time = time.time()
        
        try:
            # TECHNIQUE 1: Grammar-based prompt construction
            base_prompt = PromptGrammar.build_prompt(
                theme=theme,
                custom_input=custom_input,
                time_span=time_span,
                event_density=event_density,
                narrative_focus=narrative_focus,
                word_range=f"{Config.MIN_WORDS}-{Config.MAX_WORDS} words"
            )
            
            # TECHNIQUE 2 & 3: Multi-stage pipeline with state tracking
            if use_multi_stage:
                stateful_gen = StatefulHistoryGenerator(self.model)
                result = stateful_gen.generate_with_state(
                    base_prompt=base_prompt,
                    theme=theme,
                    custom_input=custom_input,
                    stages=2,
                    temperature=Config.TEMPERATURE,
                    max_tokens=Config.MAX_TOKENS
                )
                
                if not result["success"]:
                    raise Exception(result.get("error", "Generation failed"))
                
                content = result["final_text"]
                entities = result["entities"]
                stages_info = result["stages"]
                
            else:
                # Single-stage generation (faster, simpler)
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
                # NEW: Enhanced metadata
                "parameters": {
                    "time_span": time_span,
                    "event_density": event_density,
                    "narrative_focus": narrative_focus,
                    "multi_stage": use_multi_stage
                },
                "entities_tracked": entities,
                "stages": stages_info
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
