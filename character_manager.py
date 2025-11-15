
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Set


class CharacterState:
    """Represents the state of a single character"""
    
    def __init__(self, name: str, role: str = "supporting", event_introduced: int = 1):
        self.name = name
        self.status = "alive"  # "alive", "dead", "missing", "unknown"
        self.role = role  # "protagonist", "antagonist", "supporting"
        self.first_appearance = event_introduced
        self.last_mentioned = event_introduced
        self.death_event = None
        self.revival_event = None
        self.relationships = {}  # {character_name: relationship_type}
        self.notable_actions = []  # List of important things they did
    
    def kill(self, event_num: int, cause: str = ""):
        """Mark character as dead"""
        self.status = "dead"
        self.death_event = event_num
        if cause:
            self.notable_actions.append(f"Died: {cause} (Event {event_num})")
    
    def revive(self, event_num: int, reason: str):
        """Revive character (only with in-universe explanation)"""
        self.status = "alive"
        self.revival_event = event_num
        self.notable_actions.append(f"Revived: {reason} (Event {event_num})")
    
    def update_mention(self, event_num: int):
        """Update last mentioned event"""
        self.last_mentioned = event_num
    
    def add_action(self, action: str, event_num: int):
        """Record a notable action"""
        self.notable_actions.append(f"{action} (Event {event_num})")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'status': self.status,
            'role': self.role,
            'first_appearance': self.first_appearance,
            'last_mentioned': self.last_mentioned,
            'death_event': self.death_event,
            'revival_event': self.revival_event,
            'relationships': self.relationships,
            'notable_actions': self.notable_actions
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Create CharacterState from dictionary"""
        char = CharacterState(data['name'], data.get('role', 'supporting'), data.get('first_appearance', 1))
        char.status = data.get('status', 'alive')
        char.last_mentioned = data.get('last_mentioned', 1)
        char.death_event = data.get('death_event')
        char.revival_event = data.get('revival_event')
        char.relationships = data.get('relationships', {})
        char.notable_actions = data.get('notable_actions', [])
        return char


class CharacterManager:
    """Manages character roster with lifecycle tracking"""
    
    def __init__(self):
        self.roster: Dict[str, CharacterState] = {}  # {name: CharacterState}
        self.current_event_num = 0
        self.name_variations = {}  # Handle "King Alaric" vs "Alaric"

    def determine_character_role(self, char_name: str, text: str) -> str:
        """
        Intelligently determine character role from context in text.
        
        Returns: 'main', 'supporting', or 'minor'
        """
        import re
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        char_lower = char_name.lower()
        
        # Count mentions
        mention_count = len(re.findall(r'\b' + re.escape(char_lower) + r'\b', text_lower))
        
        # Keywords that suggest importance
        importance_keywords = [
            # Leadership/Authority
            r'\b(king|queen|emperor|empress|lord|lady|prince|princess|ruler|sovereign|monarch)\b',
            r'\b(leader|commander|general|captain|chief)\b',
            
            # Actions/Agency
            r'\b(declared|commanded|ordered|decreed|proclaimed|conquered|defeated|ruled)\b',
            r'\b(led|founded|established|created|destroyed|killed|assassinated)\b',
            
            # Possessives (showing ownership/agency)
            rf'\b{re.escape(char_lower)}\'s\b',
            rf'\b{re.escape(char_lower)} (army|forces|kingdom|empire|followers|allies)\b',
        ]
        
        # Score based on importance indicators
        importance_score = 0
        
        for pattern in importance_keywords:
            # Check if pattern appears near character name (within 50 chars)
            for match in re.finditer(pattern, text_lower):
                char_matches = list(re.finditer(r'\b' + re.escape(char_lower) + r'\b', text_lower))
                for char_match in char_matches:
                    distance = abs(match.start() - char_match.start())
                    if distance < 50:  # Character mentioned within 50 chars of keyword
                        importance_score += 1
                        break
        
        # Decision logic
        if mention_count >= 5 or importance_score >= 3:
            return "main"
        elif mention_count >= 2 or importance_score >= 1:
            return "supporting"
        else:
            return "minor"
    
    def add_character(self, name: str, role: str = "supporting", event_num: int = None) -> CharacterState:
        """Add a new character to the roster"""
        if event_num is None:
            event_num = self.current_event_num
        
        # Normalize name
        normalized_name = self._normalize_name(name)
        
        # Check if already exists
        if normalized_name in self.roster:
            return self.roster[normalized_name]
        
        # Create new character
        char = CharacterState(name, role, event_num)
        self.roster[normalized_name] = char
        
        # Track name variations (e.g., "King Alaric" and "Alaric")
        self.name_variations[normalized_name] = [name]
        
        return char
    
    def get_character(self, name: str) -> Optional[CharacterState]:
        """Get character by name (handles variations)"""
        normalized = self._normalize_name(name)
        return self.roster.get(normalized)
    
    def kill_character(self, name: str, cause: str = "") -> bool:
        """Mark character as dead"""
        char = self.get_character(name)
        if char:
            char.kill(self.current_event_num, cause)
            return True
        return False
    
    def revive_character(self, name: str, reason: str) -> bool:
        """Revive a dead character (requires in-universe reason)"""
        char = self.get_character(name)
        if char and char.status == "dead":
            char.revive(self.current_event_num, reason)
            return True
        return False
    
    def get_active_characters(self) -> List[CharacterState]:
        """Get all alive characters"""
        return [char for char in self.roster.values() if char.status == "alive"]
    
    def get_deceased_characters(self) -> List[CharacterState]:
        """Get all dead characters"""
        return [char for char in self.roster.values() if char.status == "dead"]
    
    def is_character_alive(self, name: str) -> bool:
        """Check if character is alive"""
        char = self.get_character(name)
        return char is not None and char.status == "alive"
    
    def update_event_number(self, event_num: int):
        """Update current event number"""
        self.current_event_num = event_num
    
    def extract_characters_from_text(self, text: str) -> List[str]:

        # Expanded exclude list
        exclude_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'year', 'years', 'event', 'events',
            'age', 'era', 'period', 'century', 'centuries', 'ae'
        }
        
        # Event/location indicators to exclude
        non_character_indicators = {
            'kingdom', 'city', 'town', 'village', 'forest', 'mountain', 'river',
            'valley', 'plain', 'desert', 'ocean', 'sea', 'lake', 'island',
            'castle', 'fortress', 'temple', 'woods', 'peak', 'peaks', 'creek', 'hills',
            'battle', 'war', 'treaty', 'pact', 'alliance', 'rebellion', 'revolt',
            'fire', 'plague', 'rot', 'disease', 'catastrophe', 'disaster',
            'throne', 'crown', 'order', 'codex', 'blade', 'sword', 'weapon',
            'founding', 'expansion', 'turmoil', 'rebirth', 'collapse',
            'age of', 'era of', 'year', 'dragon throne', 'chronicle'
        }
        
        # Character title indicators (these suggest it's a person)
        character_titles = {
            'king', 'queen', 'prince', 'princess', 'lord', 'lady', 'sir',
            'emperor', 'empress', 'duke', 'duchess', 'count', 'countess',
            'baron', 'baroness', 'knight', 'general', 'captain', 'commander'
        }
        
        # Find capitalized words (potential names)
        sentences = re.split(r'[.!?]+', text)
        potential_names = set()
        
        for sentence in sentences:
            words = sentence.strip().split()
            
            i = 0
            while i < len(words):
                # Skip first word of sentence
                if i == 0:
                    i += 1
                    continue
                
                word = words[i]
                clean_word = word.strip('.,;:!?"\'()[]{}*')
                
                # Must be capitalized and not in exclude list
                if not clean_word or not clean_word[0].isupper():
                    i += 1
                    continue
                
                if clean_word.lower() in exclude_words:
                    i += 1
                    continue
                
                # Check for multi-word names (up to 3 words)
                name_parts = [clean_word]
                j = i + 1
                
                # Look ahead for title + name pattern (e.g., "King Theron")
                has_title = clean_word.lower() in character_titles
                
                while j < len(words) and j < i + 3:
                    next_word = words[j].strip('.,;:!?"\'()[]{}*')
                    
                    if not next_word or not next_word[0].isupper():
                        break
                    
                    if next_word.lower() in exclude_words:
                        break
                    
                    name_parts.append(next_word)
                    j += 1
                
                full_name = ' '.join(name_parts)
                full_name_lower = full_name.lower()
                
                # Filter out non-characters
                is_non_character = False
                
                # Check if contains non-character indicators
                for indicator in non_character_indicators:
                    if indicator in full_name_lower:
                        is_non_character = True
                        break
                
                # Check if it's just a title without a name
                if len(name_parts) == 1 and name_parts[0].lower() in character_titles:
                    is_non_character = True
                
                # Check for date markers (e.g., "AE:**")
                if ':' in full_name or '*' in full_name or ')' in full_name:
                    is_non_character = True
                
                # Must be 2-4 words if it includes a title
                if has_title and len(name_parts) < 2:
                    is_non_character = True
                
                # Add if valid
                if not is_non_character and len(full_name) >= 3:
                    # Only add names with titles OR 2-word names
                    if has_title or len(name_parts) >= 2:
                        potential_names.add(full_name)
                
                i = j if j > i + 1 else i + 1
        
        return list(potential_names)[:20]  # Limit to 20 characters
    
    def validate_character_usage(self, text: str) -> tuple[bool, List[str]]:
        """
        Validate that no dead characters appear in the text
        Returns: (is_valid, list_of_violations)
        """
        deceased = self.get_deceased_characters()
        violations = []
        
        for char in deceased:
            # Check all name variations
            for name_var in self.name_variations.get(self._normalize_name(char.name), [char.name]):
                if name_var in text:
                    violations.append(f"{char.name} (died in Event {char.death_event})")
        
        return len(violations) == 0, violations
    
    def get_roster_summary(self) -> str:
        """Get formatted summary of character roster for AI prompt"""
        active = self.get_active_characters()
        deceased = self.get_deceased_characters()

        # Return empty if NO characters at all (both lists empty)
        if not active and not deceased:
            return ""
        
        summary = "CHARACTER ROSTER:\n\n"
        
        if active:
            summary += "ACTIVE CHARACTERS (alive, can appear in story):\n"
            for char in active:
                summary += f"  • {char.name} ({char.role})"
                if char.notable_actions:
                    summary += f" - Last action: {char.notable_actions[-1]}"
                summary += "\n"
        else:
            summary += "ACTIVE CHARACTERS: None yet\n"
        
        summary += "\n"
        
        if deceased:
            summary += "DECEASED CHARACTERS (cannot appear unless revived in-universe):\n"
            for char in deceased:
                summary += f"  • {char.name} - {char.notable_actions[-1] if char.notable_actions else 'Deceased'}\n"
        else:
            summary += "DECEASED CHARACTERS: None\n"
        
        return summary
    
    def _normalize_name(self, name: str) -> str:
        """Normalize character name for consistent lookup"""
        # Remove titles
        titles = ['king', 'queen', 'lord', 'lady', 'sir', 'prince', 'princess', 'emperor', 'empress']
        words = name.lower().split()
        normalized_words = [w for w in words if w not in titles]
        return ' '.join(normalized_words) if normalized_words else name.lower()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'roster': {name: char.to_dict() for name, char in self.roster.items()},
            'current_event_num': self.current_event_num,
            'name_variations': self.name_variations
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Create CharacterManager from dictionary"""
        manager = CharacterManager()
        manager.current_event_num = data.get('current_event_num', 0)
        manager.name_variations = data.get('name_variations', {})
        
        for name, char_data in data.get('roster', {}).items():
            manager.roster[name] = CharacterState.from_dict(char_data)
        
        return manager
    
    def export_to_json(self, filepath: str):
        """Export character roster to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def import_from_json(filepath: str):
        """Import character roster from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return CharacterManager.from_dict(data)
