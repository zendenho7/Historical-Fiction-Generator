
"""
Grammar-based prompt system with explicit variable slots
Implements replacement grammar concept from Caves of Qud
"""

class PromptGrammar:
    """Structured prompt grammar with replaceable components"""
    
    # Base grammar rules
    BASE_STRUCTURE = """You are an expert historical fiction writer specializing in creating detailed, believable chronologies.

Your task is to generate a chronological narrative with these specifications:
- Word count: {word_range}
- Time span: {time_span}
- Event density: {event_density}
- Narrative focus: {narrative_focus}
- Theme: {theme}

STRUCTURE REQUIREMENTS:
1. Present events in clear chronological order with specific dates/timeframes
2. Maintain internal consistency and logical progression
3. Create believable cause-and-effect relationships between events
4. Use rich, evocative language appropriate to the theme
5. Include specific details that make the history feel authentic

{additional_constraints}

Format your response as a narrative chronology with clear temporal markers."""

    # Theme-specific semantic fields (vocabulary/imagery)
    THEME_VOCABULARY = {
        "Fantasy Kingdom": {
            "entities": ["kings", "queens", "lords", "knights", "wizards", "dragons"],
            "events": ["coronations", "sieges", "magical discoveries", "prophecies", "royal marriages"],
            "imagery": ["castles", "ancient forests", "mystical artifacts", "enchanted weapons"]
        },
        "Future prophecy": {
            "entities": ["seers", "prophets", "chosen ones", "oracles", "interpreters"],
            "events": ["predictions", "revelations", "fulfillments", "interpretations", "divergences"],
            "imagery": ["visions", "omens", "signs", "cryptic texts", "divination tools"]
        },
        "Alien planet": {
            "entities": ["indigenous species", "colonists", "explorers", "xenobiologists"],
            "events": ["first contact", "terraforming", "evolution", "celestial events", "ecosystem shifts"],
            "imagery": ["exotic landscapes", "multiple moons", "bioluminescence", "crystalline formations"]
        },
        # Add more as needed
    }
    
    @classmethod
    def build_prompt(cls, theme, custom_input, time_span="moderate", 
                     event_density="moderate", narrative_focus="political", 
                     word_range="500-1000 words"):
        """
        Build a complete prompt with all variable slots filled
        
        This implements the grammar replacement concept:
        - Theme → affects vocabulary domain
        - Time span → affects temporal scale
        - Event density → affects number of events
        - Custom input → seeds specific entities/state
        """
        
        # Get theme-specific vocabulary
        vocab = cls.THEME_VOCABULARY.get(theme, {})
        
        # Build semantic guidance
        semantic_guidance = ""
        if vocab:
            semantic_guidance = f"""
SEMANTIC GUIDANCE for {theme}:
- Key entity types: {', '.join(vocab.get('entities', []))}
- Typical events: {', '.join(vocab.get('events', []))}
- Imagery/atmosphere: {', '.join(vocab.get('imagery', []))}
"""
        
        # Build constraints based on custom input
        additional_constraints = ""
        if custom_input:
            additional_constraints = f"""
CUSTOM SPECIFICATIONS:
The chronology must incorporate: {custom_input}

Use these details as the "initial state" - they should influence the entities, events, and narrative arc.
"""
        
        # Assemble full prompt using grammar rules
        from config import Config
        
        system_prompt = cls.BASE_STRUCTURE.format(
            word_range=word_range,
            time_span=Config.TIME_SPANS.get(time_span, time_span),
            event_density=Config.EVENT_DENSITIES.get(event_density, event_density),
            narrative_focus=Config.NARRATIVE_FOCUSES.get(narrative_focus, narrative_focus),
            theme=theme,
            additional_constraints=additional_constraints + semantic_guidance
        )
        
        return system_prompt
