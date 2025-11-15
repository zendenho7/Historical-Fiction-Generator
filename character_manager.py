
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
        Intelligently determine character role from context.
        
        ENHANCED with:
        - Mention count threshold
        - Action verb proximity
        - Title presence
        - Possessive usage
        """
        import re
        
        text_lower = text.lower()
        char_lower = char_name.lower()
        
        # Count mentions (case-insensitive word boundary)
        mention_pattern = r'\b' + re.escape(char_lower) + r'\b'
        mention_count = len(re.findall(mention_pattern, text_lower))
        
        # Check for title usage (e.g., "Queen Lyra", "King Aldric")
        has_title = any(title in char_name.lower() for title in [
            'king', 'queen', 'emperor', 'empress', 'prince', 'princess',
            'lord', 'lady', 'sir', 'dame', 'general', 'commander'
        ])
        
        # Check for possessive usage (indicates importance)
        has_possessive = f"{char_lower}'s" in text_lower
        
        # High-importance action verbs (indicates MAIN character)
        main_actions = [
            r'\b(ruled|reigned|conquered|founded|established|created)\b',
            r'\b(declared|proclaimed|decreed|ordered|commanded)\b',
            r'\b(killed|assassinated|defeated|destroyed)\b',
            r'\b(led|guided|united|liberated|saved)\b',
        ]
        
        # Medium-importance action verbs (indicates SUPPORTING character)
        supporting_actions = [
            r'\b(fought|defended|attacked|battled|served)\b',
            r'\b(discovered|found|uncovered|revealed)\b',
            r'\b(married|allied|betrayed|fled|escaped)\b',
            r'\b(built|constructed|forged|crafted)\b',
        ]
        
        # Count actions near character name
        main_action_count = 0
        supporting_action_count = 0
        
        # Search for character name followed by action within 50 characters
        for pattern in main_actions:
            for char_match in re.finditer(mention_pattern, text_lower):
                char_pos = char_match.start()
                # Look 50 chars before and after
                context = text_lower[max(0, char_pos-50):min(len(text_lower), char_pos+50)]
                if re.search(pattern, context):
                    main_action_count += 1
        
        for pattern in supporting_actions:
            for char_match in re.finditer(mention_pattern, text_lower):
                char_pos = char_match.start()
                context = text_lower[max(0, char_pos-50):min(len(text_lower), char_pos+50)]
                if re.search(pattern, context):
                    supporting_action_count += 1
        
        # === CLASSIFICATION LOGIC ===
        
        # MAIN character criteria:
        # - 5+ mentions OR 3+ main actions OR has title + possessive
        if (mention_count >= 5 or 
            main_action_count >= 3 or 
            (has_title and has_possessive) or
            (has_title and mention_count >= 3)):
            return "main"
        
        # SUPPORTING character criteria:
        # - 2-4 mentions OR 1+ main actions OR 2+ supporting actions
        elif (mention_count >= 2 or 
            main_action_count >= 1 or 
            supporting_action_count >= 2 or
            has_possessive):
            return "supporting"
        
        # MINOR character (mentioned but not important)
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
    
    def extract_characters_from_text(self, text: str, max_characters: int = None) -> List[str]:
        """
        Enhanced character extraction with better filtering
        
        IMPROVEMENTS:
        1. Excludes geographic locations (countries, cities, regions)
        2. Excludes species/scientific names
        3. Requires character titles or contextual verbs
        4. Prioritizes entities with human actions
        """
        
        # === EXPANDED EXCLUSION LISTS ===
        
        # Common words to always exclude
        exclude_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'year', 'years', 'event', 'events',
            'age', 'era', 'period', 'century', 'centuries', 'ae'
        }
        
        geographic_indicators = {
            # Regions/Landforms
            'peninsula', 'island', 'continent', 'region', 'territory', 'land',
            'kingdom', 'empire', 'nation', 'country', 'state', 'province',
            'city', 'town', 'village', 'settlement', 'outpost',
            
            # Natural features (ADD THESE - fixes "Elder Tree" issue)
            'forest', 'jungle', 'woods', 'wilderness', 'grove',
            'tree', 'trees',  # CRITICAL FIX
            'mountain', 'mountains', 'peak', 'peaks', 'hills', 'highlands',
            'river', 'creek', 'stream', 'lake', 'sea', 'ocean', 'bay', 'gulf',
            'valley', 'plain', 'plains', 'desert', 'wasteland', 'tundra',
            'coast', 'shore', 'beach', 'cliff', 'canyon', 'gorge',
            
            # Structures (buildings/fortifications)
            'castle', 'fortress', 'fort', 'citadel', 'stronghold',
            'temple', 'cathedral', 'shrine', 'monastery', 'abbey',
            'palace', 'manor', 'estate', 'tower', 'keep',
            'gate', 'gates', 'wall', 'walls', 'bridge',
            'galleries', 'gallery', 'citadel',  # ADD for your story context
            
            # Specific well-known places
            'arabia', 'arabian', 'saudi', 'africa', 'asia', 'europe',
            'america', 'antarctica', 'australia', 'pacific', 'atlantic',
            'mediterranean', 'sahara', 'gobi', 'arctic', 'antarctic',
            'arboria', 'arboreal', 'gloomwood', 'silverwood'  # Your world-specific places
        }

        # Scientific/species indicators (biology terms)
        scientific_indicators = {
            'gryllus', 'arenarius', 'sapiens', 'domesticus',  # Latin binomials
            'species', 'genus', 'family', 'order', 'class',
            'insect', 'cricket', 'beetle', 'spider', 'ant',
            'mammal', 'reptile', 'bird', 'fish', 'amphibian'
        }
        
        # Abstract concepts/events (not people)
        abstract_concepts = {
            'hope', 'faith', 'courage', 'wisdom', 'justice', 'freedom',
            'peace', 'war', 'battle', 'conflict', 'alliance', 'treaty',
            'rebellion', 'revolution', 'uprising', 'coup',
            'founding', 'establishment', 'creation', 'destruction',
            'expansion', 'contraction', 'growth', 'decline',
            'sands', 'shifting', 'eternal', 'ancient', 'sacred'
        }

         # Group/Faction indicators (prevents "Dragon Riders" extraction)
        
        group_indicators = {
            # Military groups
            'riders', 'guards', 'guardians', 'warriors', 'soldiers', 'knights',
            'army', 'armies', 'legion', 'legions', 'force', 'forces',
            'militia', 'mercenaries', 'troops', 'battalion',
            
            # Political groups
            'council', 'senate', 'parliament', 'assembly',
            'faction', 'party', 'alliance', 'coalition',
            
            # Social groups
            'people', 'folk', 'clan', 'tribe', 'family',
            'order', 'guild', 'brotherhood', 'sisterhood',
            'society', 'organization', 'group',
            
            # Specific to your world
            'elders', 'arborians'
        } 

        # Event/Phenomenon indicators (prevents "Great Burning" extraction)
        event_indicators = {
            # Historical events
            'war', 'wars', 'battle', 'battles', 'siege', 'sieges',
            'conflict', 'conflicts', 'rebellion', 'revolution', 'uprising',
            'invasion', 'incursion', 'raid', 'assault',
            
            # Natural/magical events
            'burning', 'fire', 'flood', 'storm', 'earthquake', 'disaster',
            'germination', 'sprouting', 'blooming',
            'era', 'age', 'epoch', 'period',
            
            # Ceremonies/milestones
            'founding', 'discovery', 'coronation', 'reign',
            'binding', 'sealing', 'banishment',
            'rebirth', 'renaissance', 'awakening'
        }

        # Character titles (these MUST accompany a name to be valid)
        character_titles = {
            'king', 'queen', 'emperor', 'empress', 'sultan', 'caliph',
            'prince', 'princess', 'duke', 'duchess', 'lord', 'lady',
            'count', 'countess', 'baron', 'baroness',
            'sir', 'dame', 'knight',
            'general', 'commander', 'captain', 'admiral', 'colonel',
            'chief', 'chieftain', 'elder', 'shaman', 'priest', 'bishop',
            'prophet', 'sage', 'wizard', 'mage', 'sorcerer',
            'master', 'mistress', 'doctor', 'professor'
        }
        
        # Human action verbs (verbs that indicate a PERSON acting)
        human_action_verbs = {
            # Leadership actions
            'ruled', 'reigned', 'governed', 'commanded', 'led', 'directed',
            'declared', 'decreed', 'proclaimed', 'announced', 'ordered',
            
            # Physical actions
            'killed', 'murdered', 'assassinated', 'executed', 'slew', 'defeated',
            'conquered', 'invaded', 'attacked', 'defended', 'fought', 'battled',
            'fled', 'escaped', 'retreated', 'advanced', 'marched',
            
            # Social actions
            'married', 'wed', 'divorced', 'betrothed', 'courted',
            'befriended', 'betrayed', 'allied', 'conspired', 'plotted',
            
            # Mental actions
            'decided', 'chose', 'planned', 'schemed', 'thought', 'believed',
            'knew', 'learned', 'discovered', 'realized', 'understood',
            
            # Speech actions
            'said', 'spoke', 'declared', 'whispered', 'shouted', 'claimed',
            'argued', 'debated', 'negotiated', 'promised', 'vowed'
        }
        
        # === EXTRACTION LOGIC ===
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        potential_characters = {}  # {name: score}
        
        for sentence in sentences:
            words = sentence.strip().split()
            
            i = 0
            while i < len(words):
                # Skip first word of sentence (often capitalized for grammar)
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
                
                # === BUILD MULTI-WORD NAME ===
                name_parts = [clean_word]
                j = i + 1
                
                # Check if first word is a title
                has_title = clean_word.lower() in character_titles
                
                # Look ahead for additional capitalized words
                while j < len(words) and j < i + 4:  # Max 4 words
                    next_word = words[j].strip('.,;:!?"\'()[]{}*')
                    
                    if not next_word or not next_word[0].isupper():
                        break
                    
                    if next_word.lower() in exclude_words:
                        break
                    
                    name_parts.append(next_word)
                    j += 1
                
                full_name = ' '.join(name_parts)
                full_name_lower = full_name.lower()
                
                # === FILTERING LOGIC ===
                
                # 1. REJECT: Geographic terms
                if any(geo in full_name_lower for geo in geographic_indicators):
                    i = j if j > i + 1 else i + 1
                    continue

                # 2. REJECT: Scientific terms
                if any(sci in full_name_lower for sci in scientific_indicators):
                    i = j if j > i + 1 else i + 1
                    continue

                # 3. REJECT: Abstract concepts
                if any(concept in full_name_lower for concept in abstract_concepts):
                    i = j if j > i + 1 else i + 1
                    continue

                # 4. REJECT: Group/Faction names (NEW FIX)
                if any(group in full_name_lower.split() for group in group_indicators):
                    i = j if j > i + 1 else i + 1
                    continue

                # 5. REJECT: Event names (NEW FIX)
                # Check if entity contains event-related words
                entity_words = set(full_name_lower.split())
                if entity_words & event_indicators:  # Intersection check
                    i = j if j > i + 1 else i + 1
                    continue

                # 6. REJECT: Compound place names (e.g., "Elder Tree", "Sunstone Citadel")
                # Pattern: [Adjective] + [Geographic term]
                if len(name_parts) == 2:
                    last_word = name_parts[-1].lower()
                    if last_word in geographic_indicators:
                        i = j if j > i + 1 else i + 1
                        continue

                # 7. REJECT: Just a title without a name
                if len(name_parts) == 1 and name_parts[0].lower() in character_titles:
                    i = j if j > i + 1 else i + 1
                    continue

                # 8. REJECT: Date markers (e.g., "AE", "Year")
                if ':' in full_name or '*' in full_name or ')' in full_name:
                    i = j if j > i + 1 else i + 1
                    continue

                # 9. REJECT: Possessive forms only (e.g., "Elder Tree's")
                if full_name.endswith("'s") and len(name_parts) == 1:
                    i = j if j > i + 1 else i + 1
                    continue
                
                # === SCORING SYSTEM (to prioritize likely characters) ===
                score = 0
                
                # +3 points: Has a character title
                if has_title:
                    score += 3
                
                # +2 points: Multiple words (e.g., "King Aldric" vs "Arabia")
                if len(name_parts) >= 2:
                    score += 2
                
                # +2 points: Appears near human action verbs
                sentence_lower = sentence.lower()
                for verb in human_action_verbs:
                    if verb in sentence_lower:
                        # Check proximity (within 30 characters)
                        name_pos = sentence_lower.find(full_name_lower)
                        verb_pos = sentence_lower.find(verb)
                        if name_pos >= 0 and verb_pos >= 0:
                            distance = abs(name_pos - verb_pos)
                            if distance < 30:
                                score += 2
                                break
                
                # +1 point: Has possessive form ("'s")
                if f"{full_name_lower}'s" in sentence_lower:
                    score += 1
                
                # +1 point: Mentioned multiple times in text
                mention_count = text.lower().count(full_name_lower)
                if mention_count >= 2:
                    score += 1
                if mention_count >= 4:
                    score += 1
                
                # === ACCEPT if score >= 3 ===
                if score >= 3 and len(full_name) >= 3:
                    if full_name not in potential_characters:
                        potential_characters[full_name] = score
                    else:
                        potential_characters[full_name] += score
                
                i = j if j > i + 1 else i + 1
        
        # === SORT BY SCORE AND RETURN ===
        sorted_characters = sorted(
            potential_characters.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        character_names = [name for name, score in sorted_characters]
        
        # Apply max_characters limit
        if max_characters and len(character_names) > max_characters:
            character_names = character_names[:max_characters]
        
        # Limit to 20 if no max specified
        return character_names[:20] if not max_characters else character_names
    
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
    
    def calculate_entity_consistency(self, text: str) -> tuple:
        """
        Calculate entity consistency score for quality metrics
        
        Returns:
            (score: float, details: dict) where score is 0.0-1.0
        """
        import re
        
        # Extract all capitalized entities mentioned in text
        mentioned_entities = set()
        for match in re.finditer(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text):
            entity = match.group()
            # Filter out common non-entity words
            if entity.lower() not in {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'from'}:
                mentioned_entities.add(entity)
        
        # Get tracked characters
        tracked_chars = set(self.roster.keys())
        
        # Calculate matches
        correct_matches = mentioned_entities & tracked_chars
        false_negatives = tracked_chars - mentioned_entities  # Tracked but not mentioned
        false_positives = mentioned_entities - tracked_chars  # Mentioned but not tracked
        
        # Score calculation
        if len(tracked_chars) == 0:
            consistency_score = 0.0
        else:
            # Ratio of tracked characters that appear in text
            coverage = len(correct_matches) / len(tracked_chars)
            
            # Penalty for false positives (untracked entities)
            if len(mentioned_entities) > 0:
                precision = len(correct_matches) / len(mentioned_entities)
            else:
                precision = 1.0
            
            # Combined score (F1-like metric)
            if coverage + precision > 0:
                consistency_score = 2 * (coverage * precision) / (coverage + precision)
            else:
                consistency_score = 0.0
        
        details = {
            'tracked_count': len(tracked_chars),
            'mentioned_count': len(mentioned_entities),
            'correct_matches': len(correct_matches),
            'false_negatives': list(false_negatives),  # Should be mentioned but aren't
            'false_positives': list(false_positives)[:10],  # Mentioned but not tracked (limit to 10)
            'consistency_score': consistency_score
        }
        
        return consistency_score, details

    def get_consistency_report(self, text: str) -> str:
        """
        Generate human-readable consistency report
        """
        score, details = self.calculate_entity_consistency(text)
        
        report = f"Entity Consistency: {score:.1%}\n"
        report += f"Tracked characters: {details['tracked_count']}\n"
        report += f"Mentioned in text: {details['mentioned_count']}\n"
        report += f"Correctly matched: {details['correct_matches']}\n"
        
        if details['false_negatives']:
            report += f"\n⚠️ Tracked characters not mentioned:\n"
            for char in details['false_negatives']:
                report += f"  - {char}\n"
        
        if details['false_positives']:
            report += f"\n⚠️ Untracked entities mentioned (may need tracking):\n"
            for entity in details['false_positives'][:5]:  # Show top 5
                report += f"  - {entity}\n"
        
        return report

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
