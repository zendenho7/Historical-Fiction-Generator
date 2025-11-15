
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
        
        # 🆕 NEW: Extract deaths and update CharacterManager
        if character_manager:
            death_patterns = [
                r"(\w+(?:\s+\w+)?)\s+(?:was\s+)?(?:killed|died|perished|murdered|slain|assassinated|falls\s+to)",
                r"(?:death|demise|execution)\s+of\s+(\w+(?:\s+\w+)?)",
                r"(\w+(?:\s+\w+)?)\s+(?:death|demise)",
            ]
            
            for pattern in death_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    char_name = match if isinstance(match, str) else match[0]
                    char_name = char_name.strip()
                    
                    # Check if this is a known character
                    normalized_name = character_manager._normalize_name(char_name)
                    if normalized_name in character_manager.roster:
                        char = character_manager.roster[normalized_name]
                        if char.status == "alive":
                            character_manager.kill_character(
                                char.name,
                                cause=f"Died in Event {event_node.event_number}"
                            )
                            print(f"⚰️ Marked {char.name} as deceased in Event {event_node.event_number}")
            
            # Track character mentions
            for char_name, char_state in character_manager.roster.items():
                if char_state.name.lower() in content.lower():
                    event_node.add_affected_character(char_state.name)
                    char_state.update_mention(event_node.event_number)
        
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
