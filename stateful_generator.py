
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
    """Generator with state tracking across generation stages"""
    
    def __init__(self, model):
        self.model = model
        self.tracked_entities = {
            'characters': set(),
            'places': set()
        }
    
    def _trim_to_word_limit(self, text, max_words=1000, min_words=500):
        """
        Enhanced trim with better sentence boundary detection
        PRESERVES metadata sections (anything after --- separator)
        """
        # FIRST: Check if there's a metadata section and extract it
        metadata_pattern = r'\n-{3,}\s*\n\s*CHARACTERS:\s*\n'
        import re
        
        metadata_match = re.search(metadata_pattern, text, re.IGNORECASE)
        metadata_section = ""
        narrative_only = text
        
        if metadata_match:
            # Separate narrative from metadata
            narrative_only = text[:metadata_match.start()].strip()
            metadata_section = text[metadata_match.start():].strip()
            print(f"📋 Detected metadata section ({len(metadata_section.split())} words)")
        
        # NOW: Trim only the NARRATIVE portion (not the metadata)
        words = narrative_only.split()
        word_count = len(words)
        
        # If within range, return as-is (with metadata reattached)
        if min_words <= word_count <= max_words:
            if metadata_section:
                return narrative_only + "\n\n" + metadata_section
            return narrative_only
        
        # If too short, return as-is
        if word_count < min_words:
            if metadata_section:
                return narrative_only + "\n\n" + metadata_section
            return narrative_only
        
        # If too long, trim intelligently
        if word_count > max_words:
            # Strategy: Trim to max_words, then find last complete paragraph
            trimmed_words = words[:max_words]
            trimmed_text = ' '.join(trimmed_words)
            
            # Find last paragraph break (double newline)
            last_para = trimmed_text.rfind('\n\n')
            if last_para > len(trimmed_text) * 0.85:
                trimmed_narrative = trimmed_text[:last_para]
            else:
                # Find last sentence
                sentence_ends = [
                    trimmed_text.rfind('.'),
                    trimmed_text.rfind('!'),
                    trimmed_text.rfind('?')
                ]
                last_sentence = max(sentence_ends)
                
                if last_sentence > len(trimmed_text) * 0.90:
                    trimmed_narrative = trimmed_text[:last_sentence + 1]
                else:
                    # Fallback: hard cut with ellipsis
                    trimmed_narrative = ' '.join(words[:max_words-1]) + "..."
            
            # Reattach metadata section
            if metadata_section:
                return trimmed_narrative + "\n\n" + metadata_section
            return trimmed_narrative
        
        # Default fallback
        if metadata_section:
            return narrative_only + "\n\n" + metadata_section
        return narrative_only
 
    def _extract_text(self, response):
        """Safely extract text from Gemini response"""
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            return part.text
        
        try:
            return response.text
        except:
            return None
    
    def generate_with_state(self, base_prompt, theme, custom_input="", 
                       stages=2, temperature=0.7, max_tokens=2000,
                       session_manager=None):
        """
        Generate with multi-stage pipeline and state tracking
        ENHANCED with word count enforcement
        """
        try:
            if stages == 1:
                # Single-stage generation
                response = self.model.generate_content(
                    base_prompt,
                    generation_config={
                        'temperature': temperature,
                        'max_output_tokens': max_tokens
                    }
                )
                
                content = self._extract_text(response)
                if not content:
                    return {
                        'success': False,
                        'error': 'Empty response from AI',
                        'final_text': '',
                        'entities': {},
                        'stages': None
                    }
                
                # CRITICAL: Enforce word count limit
                content = self._trim_to_word_limit(content, max_words=1000, min_words=500)
                
                # Extract entities (use session_manager if available)
                if session_manager:
                    # Let session_manager handle character tracking
                    entities = {
                        'characters': [c.name for c in session_manager.character_manager.get_active_characters()],
                        'places': []  # Can be enhanced later
                    }
                else:
                    # Fallback to old method
                    self._extract_entities(content)
                    entities = {
                        'characters': list(self.tracked_entities['characters'])[:15],
                        'places': list(self.tracked_entities['places'])[:15]
                    }

                return {
                    'success': True,
                    'final_text': content,
                    'entities': entities,
                    'stages': None
                }

            else:
                # Multi-stage generation (stages == 2)
                
                # STAGE 1: Generate initial skeleton
                stage1_prompt = f"""{base_prompt}

STAGE 1 INSTRUCTIONS:
Generate the initial skeleton chronology. Focus on:
- Main timeline structure
- Key events and dates
- Core entities (characters, places)
- Basic narrative flow

Target: 500-800 words for this initial stage. DO NOT EXCEED 800 WORDS.

IMPORTANT: If your prompt includes character metadata requirements, include them at the end AFTER your narrative content. If not required, do not include any metadata segment after the narrative content, keep it concise with proper formatting for the content.
"""   
                stage1_response = self.model.generate_content(
                    stage1_prompt,
                    generation_config={
                        'temperature': temperature,
                        'max_output_tokens': max_tokens
                    }
                )
                
                stage1_content = self._extract_text(stage1_response)
                if not stage1_content:
                    return {
                        'success': False,
                        'error': 'Empty Stage 1 response',
                        'final_text': '',
                        'entities': {},
                        'stages': None
                    }
                
                # Trim Stage 1 if needed (be aggressive - cap at 850 to leave room for refinement)
                stage1_content = self._trim_to_word_limit(stage1_content, max_words=850, min_words=500)
                stage1_word_count = len(stage1_content.split())
                
                # Extract entities from Stage 1
                self._extract_entities(stage1_content)
                
                # STAGE 2: Refinement with entity awareness
                characters_list = ', '.join(list(self.tracked_entities['characters'])[:10])
                places_list = ', '.join(list(self.tracked_entities['places'])[:10])
                
                # Calculate remaining word budget
                words_remaining = 1000 - stage1_word_count
                
                stage2_prompt = f"""Refine and enhance the following chronology while maintaining strict word count limits.

ORIGINAL CONTENT ({stage1_word_count} words):
{stage1_content}

TRACKED ENTITIES:
Characters: {characters_list if characters_list else 'None yet'}
Places: {places_list if places_list else 'None yet'}

CRITICAL WORD COUNT CONSTRAINTS:
- Current content: {stage1_word_count} words
- Maximum allowed: 1000 words TOTAL
- You can ADD up to {words_remaining} words (if beneficial)
- If current content is 900+ words, make MINIMAL refinements only
- DO NOT EXCEED 1000 WORDS IN YOUR OUTPUT

REFINEMENT TASKS:
1. Strengthen narrative flow and transitions between events
2. Add cross-references using the tracked entities above
3. Enhance cause-and-effect relationships
4. Improve temporal coherence and consistency
5. Add descriptive details ONLY if word count permits

OUTPUT REQUIREMENT: Generate the COMPLETE refined chronology (not just additions).
Count your words as you write. Stop at 1000 words maximum.

REMEMBER: Final output must be 500-1000 words. Currently at {stage1_word_count} words.

CRITICAL: If the original prompt required a metadata section (like CHARACTERS:), you MUST include it at the end of your output after the narrative content, separated by ---. If not required, do not include any metadata segment after the narrative content, keep it concise with proper formatting for the content.
"""
                
                stage2_response = self.model.generate_content(
                    stage2_prompt,
                    generation_config={
                        'temperature': temperature * 0.9,  # Slightly lower for refinement
                        'max_output_tokens': max_tokens
                    }
                )
                
                stage2_content = self._extract_text(stage2_response)
                if not stage2_content:
                    # Fall back to Stage 1 content if Stage 2 fails
                    stage2_content = stage1_content
                
                # CRITICAL: Enforce final word count limit
                final_content = self._trim_to_word_limit(stage2_content, max_words=1000, min_words=500)
                final_word_count = len(final_content.split())
                
                # Re-extract entities from final content
                self.tracked_entities = {'characters': set(), 'places': set()}

                # Extract entities (use session_manager if available)
                if session_manager:
                    # Let session_manager handle character tracking
                    entities = {
                        'characters': [c.name for c in session_manager.character_manager.get_active_characters()],
                        'places': []  # Can be enhanced later
                    }
                else:
                    # Fallback to old method
                    self._extract_entities(final_content)
                    entities = {
                        'characters': list(self.tracked_entities['characters'])[:15],
                        'places': list(self.tracked_entities['places'])[:15]
                    }

                # Calculate entity consistency (NEW)
                consistency_score = 0.0
                consistency_details = {}

                if session_manager.character_manager:
                    consistency_score, consistency_details = session_manager.character_manager.calculate_entity_consistency(final_content)
                    
                    # Log consistency issues for debugging
                    if consistency_score < 0.7:
                        print(f"⚠️ Low entity consistency: {consistency_score:.1%}")
                        if consistency_details.get('false_negatives'):
                            print(f"  Missing characters: {consistency_details['false_negatives']}")

                return {
                    'success': True,
                    'final_text': final_content,
                    'entities': entities,
                    'entity_consistency': consistency_score,
                    'consistency_details': consistency_details,
                    'stages': {
                        'stage1_word_count': stage1_word_count,
                        'stage2_word_count': final_word_count,
                        'stage1_preview': stage1_content[:300] + "..." if len(stage1_content) > 300 else stage1_content
                    }
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'final_text': '',
                'entities': {},
                'stages': None
            }
    
    def _extract_entities(self, text):
        """
        Extract entities with improved classification logic
        Placeholder - implement proper entity extraction
        """
        # Common words to exclude
        exclude_words = {
            'he', 'she', 'it', 'they', 'them', 'his', 'her', 'their', 'the', 
            'a', 'an', 'this', 'that', 'these', 'those', 'i', 'you', 'we'
        }
        
        # Event/concept words to exclude
        event_keywords = {
            'treaty', 'pact', 'war', 'battle', 'purge', 'alliance', 'rebellion',
            'revolution', 'council', 'academy', 'cult', 'dynasty', 'empire',
            'kingdom', 'era', 'age', 'period', 'reconciliation', 'conflict'
        }
        
        # Geographic indicators
        place_indicators = {
            'kingdom', 'city', 'town', 'village', 'forest', 'mountain', 'river',
            'valley', 'plain', 'desert', 'ocean', 'sea', 'lake', 'island',
            'castle', 'fortress', 'temple', 'woods', 'peak', 'creek', 'hills'
        }
        
        # Find capitalized words (potential proper nouns)
        sentences = re.split(r'[.!?]+', text)
        potential_entities = set()
        
        for sentence in sentences:
            words = sentence.strip().split()
            for i, word in enumerate(words):
                if i == 0:  # Skip sentence-starting words
                    continue
                
                clean_word = word.strip('.,;:!?"\'()[]{}')
                
                if clean_word and clean_word[0].isupper() and clean_word.lower() not in exclude_words:
                    # Check for multi-word proper nouns
                    if i + 1 < len(words) and len(words[i + 1]) > 0 and words[i + 1][0].isupper():
                        multi_word = clean_word
                        j = i + 1
                        while j < len(words) and len(words[j]) > 0 and words[j][0].isupper():
                            multi_word += " " + words[j].strip('.,;:!?"\'()[]{}')
                            j += 1
                        potential_entities.add(multi_word)
                    else:
                        potential_entities.add(clean_word)
        
        # Classify entities
        for entity in potential_entities:
            entity_lower = entity.lower()
            
            # Skip event keywords
            if any(keyword in entity_lower for keyword in event_keywords):
                continue
            
            # Check if it's a place
            is_place = any(indicator in entity_lower for indicator in place_indicators)
            
            if is_place:
                self.tracked_entities['places'].add(entity)
            else:
                # Check for person names (1-3 words, no event keywords)
                entity_words = entity_lower.split()
                if 1 <= len(entity_words) <= 3:
                    self.tracked_entities['characters'].add(entity)
        
        # Limit to 15 each
        if len(self.tracked_entities['characters']) > 15:
            self.tracked_entities['characters'] = set(list(self.tracked_entities['characters'])[:15])
        
        if len(self.tracked_entities['places']) > 15:
            self.tracked_entities['places'] = set(list(self.tracked_entities['places'])[:15])
        """Safely extract text from Gemini response"""
        if hasattr(re, "candidates") and re.candidates:
            for candidate in re.candidates:
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "text"):
                            return part.text
        try:
            return re.text
        except:
            return None
