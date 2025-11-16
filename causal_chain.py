
import json
import re
from typing import List, Dict, Optional
from datetime import datetime


class EventNode:
    """Represents a single event in the chronology with causal relationships"""
    
    def __init__(self, event_number: int, content: str):
        self.event_number = event_number
        self.content = content
        self.summary = ""  # 1-2 sentence summary
        self.consequences = []  # What this event causes (open threads)
        self.affected_characters = []  # Characters involved
        self.emotional_tone = ""  # "tense", "hopeful", "tragic", etc.
        self.hook = ""  # Setup for next event (1 sentence)
        self.timestamp = datetime.now().isoformat()
    
    def set_summary(self, summary: str):
        """Set concise summary of this event"""
        self.summary = summary[:200]  # Max 200 chars
    
    def add_consequence(self, consequence: str):
        """Add an open thread/consequence that needs follow-up"""
        self.consequences.append(consequence)
    
    def add_affected_character(self, character_name: str):
        """Track which characters were in this event"""
        if character_name not in self.affected_characters:
            self.affected_characters.append(character_name)
    
    def set_hook(self, hook: str):
        """Set the hook for next event"""
        self.hook = hook[:150]  # Max 150 chars
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'event_number': self.event_number,
            'content': self.content,
            'summary': self.summary,
            'consequences': self.consequences,
            'affected_characters': self.affected_characters,
            'emotional_tone': self.emotional_tone,
            'hook': self.hook,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Create EventNode from dictionary"""
        node = EventNode(data['event_number'], data.get('content', ''))
        node.summary = data.get('summary', '')
        node.consequences = data.get('consequences', [])
        node.affected_characters = data.get('affected_characters', [])
        node.emotional_tone = data.get('emotional_tone', '')
        node.hook = data.get('hook', '')
        node.timestamp = data.get('timestamp', datetime.now().isoformat())
        return node


class CausalEventChain:
    """Manages the causal chain of events ensuring continuity"""
    
    def __init__(self):
        self.events: List[EventNode] = []
        self.open_threads: List[str] = []  # Unresolved plot points
        self.current_tone = "neutral"  # Track emotional progression
    
    def add_event(self, event_number: int, content: str) -> EventNode:
        """Add a new event to the chain"""
        node = EventNode(event_number, content)
        self.events.append(node)
        return node
    
    def get_last_event(self) -> Optional[EventNode]:
        """Get the most recent event"""
        return self.events[-1] if self.events else None
    
    def get_last_n_events(self, n: int = 3) -> List[EventNode]:
        """Get the last N events for context"""
        return self.events[-n:] if len(self.events) >= n else self.events
    
    def get_causation_context(self, num_events: int = 2) -> str:
        """
        Get formatted context of recent events for AI prompt
        This tells the AI what happened before so it can create cause-and-effect
        """
        recent = self.get_last_n_events(num_events)
        
        if not recent:
            return "This is the first event. Establish the initial scenario."
        
        context = "PREVIOUS EVENTS (must influence the next event):\n\n"
        
        for event in recent:
            context += f"Event {event.event_number}:\n"
            context += f"  Summary: {event.summary if event.summary else 'No summary yet'}\n"
            
            if event.affected_characters:
                context += f"  Characters involved: {', '.join(event.affected_characters)}\n"
            
            if event.consequences:
                context += f"  Open threads: {', '.join(event.consequences)}\n"
            
            if event.hook:
                context += f"  Hook: {event.hook}\n"
            
            context += "\n"
        
        return context
    
    def get_open_threads_prompt(self) -> str:
        """Get formatted list of open plot threads"""
        if not self.open_threads:
            return "No open threads yet. You may introduce new ones."
        
        prompt = "OPEN PLOT THREADS (address at least one):\n"
        for i, thread in enumerate(self.open_threads, 1):
            prompt += f"  {i}. {thread}\n"
        
        return prompt
    
    def add_open_thread(self, thread: str):
        """Add an unresolved plot point"""
        if thread and thread not in self.open_threads:
            self.open_threads.append(thread)
    
    def resolve_thread(self, thread: str):
        """Mark a plot thread as resolved"""
        if thread in self.open_threads:
            self.open_threads.remove(thread)
    
    def clear_stale_threads(self, max_threads: int = 5):
        """Keep only the most recent threads to avoid clutter"""
        if len(self.open_threads) > max_threads:
            self.open_threads = self.open_threads[-max_threads:]
    
    def extract_summary_from_event(self, content: str) -> str:
        """
        Extract a concise summary from event content
        IMPROVED: Gets the first substantial paragraph, not the whole thing
        """
        # Remove title if present (lines starting with # or **)
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip title lines
            if line.startswith('#') or line.startswith('**'):
                continue
            # Skip empty lines
            if not line:
                continue
            # Skip lines that are just dates (e.g., "**1 AE:**")
            if re.match(r'^\*?\*?\d+\s+\w+:?\*?\*?$', line):
                continue
            
            text_lines.append(line)
            
            # Stop after first paragraph (50-200 chars)
            if len(' '.join(text_lines)) > 50:
                break
        
        # Join lines and take first 2 sentences
        text = ' '.join(text_lines)
        sentences = re.split(r'[.!?]+', text)
        
        # Take first 2 meaningful sentences
        summary_sentences = []
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if sentence and len(sentence) > 20:  # Must be substantial
                summary_sentences.append(sentence)
                if len(summary_sentences) >= 2:
                    break
        
        if not summary_sentences:
            # Fallback: take first 150 chars
            return text[:150] + "..." if len(text) > 150 else text
        
        summary = '. '.join(summary_sentences) + '.'
        
        # Ensure it's not too long
        if len(summary) > 250:
            summary = summary[:247] + "..."
        
        return summary
    
    def extract_consequences_from_event(self, content: str) -> List[str]:
        """
        Try to identify open threads/consequences from event text
        Looks for phrases like "but", "however", "this would lead to", etc.
        """
        consequences = []
        
        # Keywords that often indicate consequences
        consequence_patterns = [
            r"this (would|will|could) lead to (.+?)[.!?]",
            r"however[,\s]+(.+?)[.!?]",
            r"but (.+?)[.!?]",
            r"(?:this|which) set[s]? the stage for (.+?)[.!?]",
            r"(?:leaving|creating|causing) (.+?)[.!?]"
        ]
        
        for pattern in consequence_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Extract the consequence text
                if isinstance(match, tuple):
                    consequence = match[-1]  # Get last capture group
                else:
                    consequence = match
                
                consequence = consequence.strip()
                if len(consequence) > 10:  # Must be substantial
                    consequences.append(consequence[:100])  # Truncate if too long
        
        return consequences[:3]  # Max 3 consequences per event
    
    def _split_into_sentences(self, text: str) -> list:
        """
        Split text into sentences with proper handling of edge cases.
        
        Handles:
        - Common abbreviations (Mr., Dr., etc.)
        - Decimal numbers (3.14, Year 1.5)
        - Ellipsis (...)
        - Multiple punctuation marks
        - Dialogue and quotations
        
        Returns:
            List of sentence strings
        """
        if not text or not text.strip():
            return []
        
        # Common abbreviations that shouldn't trigger sentence splits
        abbreviations = {
            'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
            'St.', 'Ave.', 'Blvd.', 'Rd.', 'vs.', 'etc.', 'i.e.', 'e.g.',
            'Corp.', 'Inc.', 'Ltd.', 'Co.', 'Vol.', 'Rev.', 'Gen.',
            'Capt.', 'Lt.', 'Sgt.', 'No.', 'Nos.'
        }
        
        # Replace abbreviations temporarily to avoid false splits
        # Use placeholder that won't appear in normal text
        abbrev_placeholder = "<!ABR{}!>"
        abbrev_map = {}
        
        for idx, abbrev in enumerate(abbreviations):
            if abbrev in text:
                placeholder = abbrev_placeholder.format(idx)
                abbrev_map[placeholder] = abbrev
                text = text.replace(abbrev, placeholder)
        
        # Handle ellipsis - don't split on "..."
        text = text.replace('...', '<!ELLIPSIS!>')
        
        # Split on sentence boundaries: . ! ? followed by space and capital letter
        # Also handle dialogue: ." or !" or ?"
        sentence_pattern = r'(?<=[.!?])(?:(?=["\']?\s+[A-Z])|(?=["\']?\s*$))'
        
        raw_sentences = re.split(sentence_pattern, text)
        
        # Clean and restore sentences
        sentences = []
        for sentence in raw_sentences:
            # Restore abbreviations
            for placeholder, abbrev in abbrev_map.items():
                sentence = sentence.replace(placeholder, abbrev)
            
            # Restore ellipsis
            sentence = sentence.replace('<!ELLIPSIS!>', '...')
            
            # Strip whitespace
            sentence = sentence.strip()
            
            # Only add non-empty sentences
            if sentence:
                sentences.append(sentence)
        
        return sentences
    
    def _process_death_detection(self, char_name: str, character_manager, 
                             event_node: EventNode, sentence: str, 
                             detected_set: set, confidence: str = 'HIGH'):
        """
        Process and register a detected character death.
        
        Args:
            char_name: Extracted character name from pattern match
            character_manager: CharacterManager instance
            event_node: Current event being analyzed
            sentence: Sentence where death was detected
            detected_set: Set tracking already-processed deaths (avoid duplicates)
            confidence: Detection confidence level ('HIGH' or 'MEDIUM')
        """
        # Skip if already processed
        if char_name in detected_set:
            return
        
        # Normalize name and check if character exists in roster
        normalized_name = character_manager._normalize_name(char_name)
        
        if normalized_name not in character_manager.roster:
            # Try fuzzy matching for partial/multi-word names
            matched_char = self._fuzzy_match_character(char_name, character_manager)
            if matched_char:
                char_name = matched_char.name
                normalized_name = character_manager._normalize_name(char_name)
            else:
                # Not a tracked character - skip
                return
        
        char = character_manager.roster[normalized_name]
        
        # Only register death if character is currently alive
        if char.status != "alive":
            print(f"   ⚠️  {char.name} already marked as {char.status} - skipping")
            return
        
        # Extract cause of death from sentence context
        cause = self._extract_death_context(sentence, char_name, event_node.event_number)
        
        # Register the death in character manager
        try:
            character_manager.kill_character(char.name, cause=cause)
            detected_set.add(char_name)
            
            # Add to event's affected characters
            event_node.add_affected_character(char.name)
            
            # Log the detection
            print(f"   💀 [{confidence}] Marked {char.name} as deceased")
            print(f"      Context: {sentence[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error registering death for {char_name}: {e}")


    def _process_revival_detection(self, char_name: str, character_manager,
                                event_node: EventNode, sentence: str,
                                detected_set: set):
        """
        Process and register a detected character revival.
        
        Args:
            char_name: Extracted character name from pattern match
            character_manager: CharacterManager instance
            event_node: Current event being analyzed
            sentence: Sentence where revival was detected
            detected_set: Set tracking already-processed revivals (avoid duplicates)
        """
        # Skip if already processed
        if char_name in detected_set:
            return
        
        # Normalize name and check if character exists
        normalized_name = character_manager._normalize_name(char_name)
        
        if normalized_name not in character_manager.roster:
            # Try fuzzy matching
            matched_char = self._fuzzy_match_character(char_name, character_manager)
            if matched_char:
                char_name = matched_char.name
                normalized_name = character_manager._normalize_name(char_name)
            else:
                # Not a tracked character
                return
        
        char = character_manager.roster[normalized_name]
        
        # CRITICAL: Only revive if character is actually dead
        if char.status != "dead":
            print(f"   ℹ️  Revival pattern matched {char.name} but character is {char.status} - skipping")
            return
        
        # Extract revival mechanism/reason from context
        revival_reason = self._extract_revival_context(sentence, char_name, event_node.event_number)
        
        # Register the revival
        try:
            success = character_manager.revive_character(char.name, reason=revival_reason)
            
            if success:
                detected_set.add(char_name)
                
                # Add to event's affected characters
                event_node.add_affected_character(char.name)
                
                # Log the detection
                print(f"   ✨ Revived {char.name} in Event {event_node.event_number}")
                print(f"      Reason: {revival_reason[:100]}...")
            else:
                print(f"   ⚠️  Revival failed for {char.name} (character_manager returned False)")
                
        except Exception as e:
            print(f"   ❌ Error registering revival for {char_name}: {e}")


    def _fuzzy_match_character(self, partial_name: str, character_manager) -> object:
        """
        Attempt fuzzy matching for partial character names.
        
        Handles cases like:
        - "Lyra" matching "Queen Lyra"
        - "Kaelen" matching "Lord Kaelen"
        
        Args:
            partial_name: Partial character name extracted from text
            character_manager: CharacterManager instance
            
        Returns:
            Character object if match found, None otherwise
        """
        partial_lower = partial_name.lower().strip()
        
        # Try exact substring match first
        for char in character_manager.roster.values():
            if partial_lower in char.name.lower() or char.name.lower() in partial_lower:
                return char
        
        # Try word-level matching (handles "Queen Lyra" vs "Lyra")
        partial_words = set(partial_lower.split())
        for char in character_manager.roster.values():
            char_words = set(char.name.lower().split())
            # If any words match, consider it a match
            if partial_words & char_words:
                return char
        
        return None


    def _extract_death_context(self, sentence: str, char_name: str, event_number: int) -> str:
        """
        Extract death cause/context from sentence.
        
        Args:
            sentence: Sentence containing death mention
            char_name: Character name
            event_number: Current event number
            
        Returns:
            Death cause description string
        """
        # Look for common death cause patterns
        cause_patterns = [
            r'(?:killed|slain|murdered)\s+(?:by|in)\s+([^.!?]{5,50})',
            r'died\s+(?:from|of|in)\s+([^.!?]{5,50})',
            r'succumbed\s+to\s+([^.!?]{5,50})',
            r'(?:execution|assassination)\s+(?:by|of)\s+([^.!?]{5,50})',
        ]
        
        for pattern in cause_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                cause = match.group(1).strip()
                return f"{cause} (Event {event_number})"
        
        # Fallback: use sentence excerpt
        # Find position of character name in sentence
        try:
            name_pos = sentence.lower().find(char_name.lower())
            if name_pos >= 0:
                # Get 80 chars around the name
                start = max(0, name_pos - 30)
                end = min(len(sentence), name_pos + 50)
                context = sentence[start:end].strip()
                
                # Clean up
                if not context.endswith(('.', '!', '?')):
                    context += '...'
                
                return context
        except:
            pass
        
        # Ultimate fallback
        return f"Died in Event {event_number}"


    def _extract_revival_context(self, sentence: str, char_name: str, event_number: int) -> str:
        """
        Extract revival mechanism/reason from sentence.
        
        Args:
            sentence: Sentence containing revival mention
            char_name: Character name
            event_number: Current event number
            
        Returns:
            Revival reason description string
        """
        # Look for revival mechanism keywords
        mechanism_keywords = {
            'magic': 'via magic',
            'spell': 'via spell',
            'ritual': 'via ritual',
            'necromancy': 'via necromancy',
            'phoenix': 'via phoenix',
            'miracle': 'via miracle',
            'divine intervention': 'via divine intervention',
            'healed': 'healed',
            'cured': 'cured',
            'saved': 'saved',
            'resurrected': 'resurrected',
            'not dead': 'was not actually dead',
            'survived': 'survived',
            'false death': 'false death',
            'faked death': 'faked death',
        }
        
        sentence_lower = sentence.lower()
        
        # Check for mechanism keywords
        for keyword, description in mechanism_keywords.items():
            if keyword in sentence_lower:
                # Try to get more context
                try:
                    keyword_pos = sentence_lower.find(keyword)
                    start = max(0, keyword_pos - 30)
                    end = min(len(sentence), keyword_pos + 70)
                    context = sentence[start:end].strip()
                    
                    return f"{description} - {context[:80]}..."
                except:
                    return f"{description} in Event {event_number}"
        
        # Fallback: use sentence excerpt around character name
        try:
            name_pos = sentence_lower.find(char_name.lower())
            if name_pos >= 0:
                start = max(0, name_pos - 30)
                end = min(len(sentence), name_pos + 70)
                context = sentence[start:end].strip()
                
                return f"Revived - {context[:80]}..."
        except:
            pass
        
        # Ultimate fallback
        return f"Revived in Event {event_number}"


    def analyze_event_and_update(self, event_node: EventNode, character_manager=None):
        """Analyze event content and extract metadata"""
        content = event_node.content
        
        # Extract summary
        if not event_node.summary:
            event_node.set_summary(self.extract_summary_from_event(content))
        
        # Extract consequences
        consequences = self.extract_consequences_from_event(content)
        for cons in consequences:
            event_node.add_consequence(cons)
            self.add_open_thread(cons)
        
        # ENHANCED: Extract deaths & revivals and update CharacterManager
        if character_manager:
            # Get all active and deceased characters for matching
            all_characters = list(character_manager.roster.values())
            
            # ===============================================================
            # STAGE 1: DEATH DETECTION
            # ===============================================================
            
            print(f"\n🔍 Analyzing Event {event_node.event_number} for character deaths...")
            
            # Split content into sentences for better context analysis
            sentences = self._split_into_sentences(content)
            
            # Comprehensive death patterns - organized by confidence level
            death_patterns_high_confidence = [
                # === EXPLICIT DEATH VERBS (99% confidence) ===
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|were|is|are)\s+(?:killed|slain|murdered|executed|assassinated|beheaded|hanged|burned\s+alive|crucified)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:died|perished|expired|succumbed|fell)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:passed\s+away|passes\s+away|met\s+(?:his|her|their)\s+(?:death|end|demise|fate))',
                
                # === DEATH OF / POSSESSIVE DEATH (95% confidence) ===
                r'\b(?:death|demise|execution|assassination|killing|murder|slaying|passing|loss)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\'?s\s+(?:death|demise|execution|assassination|passing|end|fate|murder)',
                
                # === SACRIFICE / NOBLE DEATH (90% confidence) ===
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:sacrificed|sacrificing)\s+(?:herself|himself|themselves|their\s+life|her\s+life|his\s+life)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:gave|gives|giving)\s+(?:her|his|their)\s+life',
                
                # === CAUSATIVE DEATH (85% confidence) ===
                r'\b(?:killed|slew|slays|slaying|murdered|executing|executed|assassinated)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b(?:kills|murders|slays)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ]
            
            death_patterns_medium_confidence = [
                # === BATTLE/COMBAT DEATHS (70% confidence - needs context validation) ===
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:fell|falls)\s+(?:in\s+)?(?:battle|combat|war|the\s+siege|the\s+fight)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|were)\s+(?:struck\s+down|cut\s+down|defeated|vanquished)\s+(?:by|in)',
                
                # === SUCCUMB PATTERNS (75% confidence) ===
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:succumbs?|succumbed)\s+to\s+(?:wounds|injuries|illness|disease|poison|age)',
                
                # === FINAL BREATH / END OF LIFE (80% confidence) ===
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:drew|draws|takes|took)\s+(?:her|his|their)\s+(?:final|last)\s+breath',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:breathed|breathes)\s+(?:her|his|their)\s+last',
                
                # === LOSS / MOURNING (65% confidence - requires validation) ===
                r'\b(?:loss|mourning|grief|funeral)\s+(?:of|for|over)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ]
            
            # FALSE POSITIVE FILTERS - Exclude these patterns
            death_exclusion_patterns = [
                r'almost\s+died',
                r'nearly\s+(?:died|killed)',
                r'could\s+have\s+died',
                r'would\s+have\s+died',
                r'should\s+have\s+died',
                r'might\s+have\s+died',
                r'threatened\s+to\s+kill',
                r'wanted\s+to\s+kill',
                r'trying\s+to\s+kill',
                r'attempted\s+to\s+kill',
                r'failed\s+to\s+kill',
                r'plot\s+to\s+kill',
                r'plan\s+to\s+kill',
                r'vowed\s+to\s+kill',
                r'death\s+(?:threat|wish|sentence)(?!\s+(?:was\s+)?(?:carried\s+out|executed))',
                r'(?:fake|faked|false|staged)\s+(?:death|dying)',
                r'(?:pretend|pretended|feign|feigned)\s+(?:death|to\s+die)',
                r'near-death',
                r'cheat(?:ed)?\s+death',
                r'escape(?:d)?\s+death',
                r'avoid(?:ed)?\s+death',
                r'death\s+of\s+(?:the|a|an)\s+(?!character|person|leader|king|queen|emperor)',
            ]
            
            detected_deaths = set()
            
            # Process each sentence for death detection
            for sentence in sentences:
                sentence_lower = sentence.lower()
                
                # FILTER: Skip if sentence contains exclusion patterns
                if any(re.search(pattern, sentence_lower) for pattern in death_exclusion_patterns):
                    continue
                
                # Try high confidence patterns first
                for pattern in death_patterns_high_confidence:
                    matches = re.finditer(pattern, sentence, re.IGNORECASE)
                    for match in matches:
                        char_name = match.group(1).strip()
                        self._process_death_detection(
                            char_name, 
                            character_manager, 
                            event_node, 
                            sentence, 
                            detected_deaths,
                            confidence="HIGH"
                        )
                
                # Try medium confidence patterns with additional validation
                for pattern in death_patterns_medium_confidence:
                    matches = re.finditer(pattern, sentence, re.IGNORECASE)
                    for match in matches:
                        char_name = match.group(1).strip()
                        
                        # ADDITIONAL VALIDATION for medium confidence
                        death_keywords = ['death', 'die', 'died', 'kill', 'murder', 'slay', 
                                        'dead', 'perish', 'fatal', 'demise', 'end', 'last']
                        
                        if any(keyword in sentence_lower for keyword in death_keywords):
                            self._process_death_detection(
                                char_name, 
                                character_manager, 
                                event_node, 
                                sentence, 
                                detected_deaths,
                                confidence="MEDIUM"
                            )
            
            # ===============================================================
            # STAGE 2: REVIVAL DETECTION (STRICT - Only explicit revivals)
            # ===============================================================
            
            print(f"\n🔍 Analyzing Event {event_node.event_number} for character revivals...")
            
            # PRE-CHECK: Does content contain ANY revival keywords?
            revival_keywords_required = [
                'revive', 'revived', 'resurrect', 'resurrected', 'resurrection',
                'brought back', 'bring back', 'brings back',
                'return from death', 'returned from dead', 'returns from death',
                'return to life', 'returned to life', 'returns to life',
                'reborn', 'rebirth', 'rise from the dead', 'rose from the dead',
                'risen from', 'rise from the ashes',
                'not dead', 'wasn\'t dead', 'was not dead', 'weren\'t dead',
                'still alive', 'survived', 'alive after all',
                'miracle', 'divine intervention', 'necromancy', 'phoenix',
                'restored to life', 'restoration', 'reviving', 'resurrecting'
            ]
            
            content_lower = content.lower()
            has_revival_context = any(keyword in content_lower for keyword in revival_keywords_required)
            
            if not has_revival_context:
                print(f"   ℹ️ No revival keywords detected - skipping revival analysis")
            else:
                print(f"   ✅ Revival keywords found - analyzing patterns...")
                
                # Comprehensive revival patterns - STRICT MATCHING ONLY
                revival_patterns_explicit = [
                    # === DIRECT REVIVAL VERBS (99% confidence) ===
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|were|is|are)\s+(?:revived|resurrected|reborn|restored\s+to\s+life)',
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|were|is|are)\s+brought\s+back\s+(?:to\s+life|from\s+(?:the\s+)?dead)',
                    
                    # === ACTIVE REVIVAL (95% confidence) ===
                    r'\b(?:revive|revives|revived|resurrect|resurrects|resurrected|bring\s+back|brings\s+back|brought\s+back)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                    
                    # === RETURN FROM DEATH (90% confidence) ===
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:returns?|returned|comes?\s+back|came\s+back)\s+(?:from\s+(?:the\s+)?dead|to\s+life)',
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:rise|rises|rose|risen)\s+from\s+(?:the\s+)?(?:dead|grave|ashes)',
                    
                    # === RESURRECTION NOUN PHRASES (85% confidence) ===
                    r'\b(?:resurrection|rebirth|revival)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\'?s\s+(?:resurrection|rebirth|revival)',
                    
                    # === FALSE DEATH REVELATION (80% confidence) ===
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:wasn\'t|was\s+not|weren\'t|were\s+not)\s+(?:actually|really|truly)?\s*dead',
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:had\s+)?survived\s+(?:the\s+)?(?:death|execution|attack|fall)',
                    r'\b(?:thought|believed|presumed|declared|pronounced)\s+dead[,\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:emerged|appeared|returned|was\s+found\s+alive|reappeared)',
                ]
                
                # STRICT EXCLUSIONS for revival (avoid false positives)
                revival_exclusion_patterns = [
                    r'will\s+(?:be\s+)?revive',
                    r'could\s+(?:be\s+)?revive',
                    r'might\s+(?:be\s+)?revive',
                    r'should\s+(?:be\s+)?revive',
                    r'cannot\s+(?:be\s+)?revive',
                    r'can\'t\s+(?:be\s+)?revive',
                    r'unable\s+to\s+revive',
                    r'failed\s+to\s+revive',
                    r'attempting\s+to\s+revive',
                    r'trying\s+to\s+revive',
                    r'hope\s+to\s+revive',
                    r'plan\s+to\s+revive',
                    r'ritual\s+to\s+revive',
                    r'spell\s+to\s+revive',
                ]
                
                detected_revivals = set()
                
                # Process each sentence for revival detection
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    
                    # FILTER: Skip if sentence contains exclusion patterns
                    if any(re.search(pattern, sentence_lower) for pattern in revival_exclusion_patterns):
                        continue
                    
                    # FILTER: Sentence must contain at least one required keyword
                    if not any(keyword in sentence_lower for keyword in revival_keywords_required):
                        continue
                    
                    # Try all revival patterns
                    for pattern in revival_patterns_explicit:
                        matches = re.finditer(pattern, sentence, re.IGNORECASE)
                        for match in matches:
                            char_name = match.group(1).strip()
                            self._process_revival_detection(
                                char_name,
                                character_manager,
                                event_node,
                                sentence,
                                detected_revivals
                            )

        # Clean up old threads
        self.clear_stale_threads(max_threads=5)
    
    def build_causal_prompt(self, next_event_number: int, character_roster: str = "") -> str:
        """
        Build a complete prompt that enforces narrative flow
        ENHANCED with smooth transitions and emotional beats
        """
        prompt = f"""You are generating Event {next_event_number} in a chronological narrative.

    CRITICAL NARRATIVE FLOW REQUIREMENTS:

    1. SMOOTH TRANSITIONS (MANDATORY):
    • Begin by explicitly referencing the previous event
    • Use transition phrases: "Following...", "In response to...", "As a result of...", "Meanwhile..."
    • Show the passage of time naturally ("Years later...", "By the next decade...")
    • Create a narrative bridge that connects cause to effect
    
    Example opening: "Following Queen Lyra's assassination, the kingdom fell into chaos..."

    2. CAUSE-AND-EFFECT LOGIC:
    • Show how previous events DIRECTLY cause this event
    • Identify the triggering action or condition
    • Explain WHY this event happened (not just WHAT happened)
    • Connect character motivations to outcomes
    
    Example: "King Theron's decree (cause) led to widespread rebellion (effect)"

    3. EMOTIONAL BEATS:
    • Include character reactions to previous events
    • Show the emotional weight of consequences
    • Balance action with reflection
    • Create moments of tension, hope, fear, or resolution
    
    Example: "The survivors mourned their losses, but hope stirred when..."

    4. CONSISTENT PACING:
    • Don't rush through major events
    • Don't over-explain minor details
    • Balance narrative density across the event
    • Create rhythm: tension → action → consequence → reflection

    5. SOFT HOOKS (End with Forward Momentum):
    • Conclude with a consequence that creates anticipation
    • Open a question or conflict for the next event
    • Don't use cliffhangers - use natural story momentum
    
    Example endings:
    • "But this peace would not last, as dark omens appeared in the east..."
    • "Meanwhile, a new power was rising in the shadows..."
    • "Yet the cost of victory would soon become clear..."

    6. PACING REQUIREMENT:
    • Maintain consistent time gaps between events
    • If previous events jumped 50+ years, continue similar scale
    • Avoid sudden 1-year jumps after decades-long gaps
    • Example: Year 1 → 53 → 112 → 187 (consistent ~50-70 year gaps)

    {self.get_causation_context(num_events=2)}

    {self.get_open_threads_prompt()}

    {character_roster}

    MANDATORY OPENING STRUCTURE:
    Start your event with ONE of these patterns:
    • "[Time marker], following [previous event], [new situation]..."
    • "In response to [previous event], [character] [action]..."
    • "As [previous event] unfolded, [consequence] emerged..."
    • "[Time marker] after [previous event], [new development]..."

    FORBIDDEN:
    - Starting with a date alone (❌ "In Year 523...")
    - Disconnected events that ignore previous context
    - Robotic listing of facts without narrative flow
    - Mentioning deceased characters without revival explanation
    - Abrupt topic changes without transitions

    Generate Event {next_event_number} now with smooth, natural narrative flow.
    """
        
        return prompt

    
    def get_chain_summary(self) -> str:
        """Get a summary of the entire event chain"""
        if not self.events:
            return "No events in chain yet."
        
        summary = f"EVENT CHAIN ({len(self.events)} events):\n\n"
        
        for event in self.events:
            summary += f"Event {event.event_number}: {event.summary}\n"
            if event.affected_characters:
                summary += f"  → Characters: {', '.join(event.affected_characters)}\n"
        
        summary += f"\nOpen threads: {len(self.open_threads)}\n"
        
        return summary
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'events': [event.to_dict() for event in self.events],
            'open_threads': self.open_threads,
            'current_tone': self.current_tone
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Create CausalEventChain from dictionary"""
        chain = CausalEventChain()
        chain.open_threads = data.get('open_threads', [])
        chain.current_tone = data.get('current_tone', 'neutral')
        
        for event_data in data.get('events', []):
            event = EventNode.from_dict(event_data)
            chain.events.append(event)
        
        return chain
    
    def export_to_json(self, filepath: str):
        """Export event chain to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def import_from_json(filepath: str):
        """Import event chain from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return CausalEventChain.from_dict(data)
