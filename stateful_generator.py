
"""
Multi-stage generation with state tracking
Implements entity tracking and coherence checking
"""
import google.generativeai as genai
from datetime import datetime
import time
import re
from config import Config

class StatefulHistoryGenerator:
    """
    Generates chronologies with state tracking across stages
    Implements the entity-event model from Caves of Qud
    """
    
    def __init__(self, model):
        self.model = model
        self.tracked_entities = {
            "characters": [],
            "places": [],
            "items": [],
            "factions": []
        }
        
    def extract_entities(self, text):
        """
        Extract named entities from generated text
        This represents the "state" that future generations can reference
        """
        # Simple pattern matching (could use NER in production)
        # Capitalized words likely to be names
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Filter out common words
        common_words = {'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'Of', 'By', 'With'}
        entities = [name for name in potential_names if name not in common_words]
        
        return list(set(entities))[:10]  # Top 10 unique entities
    
    def generate_with_state(self, base_prompt, theme, custom_input="", 
                           stages=2, **kwargs):
        """
        Multi-stage generation with state tracking
        
        Stage 1: Generate initial chronology skeleton
        Stage 2: Refine with entity callbacks and coherence
        
        Args:
            base_prompt: Base prompt template
            theme: Theme name
            custom_input: User specifications
            stages: Number of refinement stages
        """
        results = []
        current_text = ""
        
        # STAGE 1: Initial generation
        print(f"[Stage 1/{stages}] Generating initial chronology skeleton...")
        
        stage1_prompt = f"{base_prompt}\n\nGenerate the chronology:"
        
        response = self.model.generate_content(
            stage1_prompt,
            generation_config={
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', 1200)
            }
        )
        
        current_text = self._extract_text(response)
        if not current_text:
            return {"success": False, "content": None, "error": "No content generated in stage 1"}
        
        # Extract entities from stage 1
        entities = self.extract_entities(current_text)
        self.tracked_entities["characters"] = entities[:5]
        self.tracked_entities["places"] = entities[5:8]
        
        results.append({
            "stage": 1,
            "text": current_text,
            "entities_found": entities,
            "word_count": len(current_text.split())
        })
        
        # STAGE 2: Refinement with entity callbacks
        if stages > 1:
            print(f"[Stage 2/{stages}] Refining with entity callbacks...")
            
            entity_context = f"""
ENTITIES ESTABLISHED IN THIS CHRONOLOGY:
- Key characters: {', '.join(self.tracked_entities['characters'])}
- Key places: {', '.join(self.tracked_entities['places'])}

Now refine the chronology:
1. Ensure these entities appear consistently throughout
2. Create callbacks - later events should reference earlier events
3. Strengthen cause-and-effect relationships
4. Maintain chronological coherence
5. Target word count: {Config.MIN_WORDS}-{Config.MAX_WORDS} words

Original chronology to refine:
{current_text}

Provide the REFINED version:"""
            
            response = self.model.generate_content(
                entity_context,
                generation_config={
                    "temperature": kwargs.get('temperature', 0.6),  # Lower temp for coherence
                    "max_output_tokens": kwargs.get('max_tokens', 1500)
                }
            )
            
            refined_text = self._extract_text(response)
            if refined_text:
                current_text = refined_text
                results.append({
                    "stage": 2,
                    "text": refined_text,
                    "word_count": len(refined_text.split())
                })
        
        return {
            "success": True,
            "final_text": current_text,
            "stages": results,
            "entities": self.tracked_entities
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
