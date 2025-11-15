"""
Grammar-based prompt system with explicit variable slots
Implements replacement grammar concept from Caves of Qud
"""

class PromptGrammar:
    """Structured prompt grammar with replaceable components"""
    
    BASE_STRUCTURE = """You are an expert historical fiction writer specializing in creating detailed, believable chronologies.

CRITICAL WORD COUNT REQUIREMENT:
- You MUST generate between {min_words} and {max_words} words
- Count your words carefully as you write
- If you approach {max_words} words, conclude your chronology IMMEDIATELY
- DO NOT exceed {max_words} words under ANY circumstances
- Target approximately {target_words} words for optimal results

THEME & PARAMETERS:
- Theme: {theme}
- Time span: {time_span}
- Event density: {event_density}
- Narrative focus: {narrative_focus}

{character_requirements}

{semantic_guidance}

{custom_specifications}

{character_roster}

{causal_context}

STRUCTURE REQUIREMENTS:
1. Present events in clear chronological order with specific dates/timeframes
2. Maintain internal consistency and logical progression
3. Create believable cause-and-effect relationships between events
4. Use rich, evocative language appropriate to the theme
5. Include specific details that make the history feel authentic

FORMAT GUIDELINES:
- Start with a compelling title
- Use clear temporal markers (years, dates, eras)
- Write in narrative prose, not bullet points
- Show how earlier events influence later ones
- Create a coherent, engaging historical narrative

WORD COUNT REMINDER: Write exactly {min_words}-{max_words} words. Stop at {max_words} words maximum.

Format your response as a narrative chronology with clear temporal markers.
"""

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
        "Survivors of an apocalyptic event": {
            "entities": ["survivors", "raiders", "scavengers", "leaders", "mutants"],
            "events": ["collapse", "migration", "resource wars", "rebuilding", "discoveries"],
            "imagery": ["ruins", "wasteland", "bunkers", "contaminated zones", "salvaged tech"]
        },
        "Imaginary creature": {
            "entities": ["the creature", "observers", "hunters", "researchers", "witnesses"],
            "events": ["first sighting", "encounters", "migrations", "conflicts", "revelations"],
            "imagery": ["habitats", "tracks", "behaviors", "adaptations", "mysteries"]
        },
        "Imaginary world event or holiday": {
            "entities": ["participants", "organizers", "celebrants", "traditionalists", "innovators"],
            "events": ["founding", "celebrations", "traditions", "changes", "controversies"],
            "imagery": ["ceremonies", "symbols", "rituals", "decorations", "customs"]
        },
        "Cultural myth or legend": {
            "entities": ["heroes", "deities", "monsters", "sages", "mortals"],
            "events": ["creation", "quests", "battles", "transformations", "lessons"],
            "imagery": ["sacred places", "artifacts", "symbols", "trials", "mysteries"]
        },
        "Lineage of a family": {
            "entities": ["ancestors", "descendants", "patriarchs", "matriarchs", "heirs"],
            "events": ["births", "marriages", "conflicts", "achievements", "tragedies"],
            "imagery": ["family estates", "heirlooms", "traditions", "legacies", "bloodlines"]
        },
        "Reimagined Singapore": {
            "entities": ["citizens", "leaders", "immigrants", "innovators", "communities"],
            "events": ["founding", "development", "crises", "transformations", "milestones"],
            "imagery": ["landmarks", "districts", "cultures", "technologies", "institutions"]
        },
        "Alien planet": {
            "entities": ["indigenous species", "colonists", "explorers", "xenobiologists"],
            "events": ["first contact", "terraforming", "evolution", "celestial events", "ecosystem shifts"],
            "imagery": ["exotic landscapes", "multiple moons", "bioluminescence", "crystalline formations"]
        },
        "Interesting object (work of art, enchanted artifact, spaceship)": {
            "entities": ["creators", "owners", "seekers", "scholars", "thieves"],
            "events": ["creation", "discovery", "ownership changes", "uses", "mysteries"],
            "imagery": ["craftsmanship", "powers", "history", "legends", "transformations"]
        }
    }

    @classmethod
    def build_prompt(cls, theme, custom_input="", time_span="moderate", 
                    event_density="moderate", narrative_focus="political", 
                    word_range="500-1000 words", 
                    character_roster_summary="", causal_context="", num_characters=5):
        """
        Build a complete prompt with all variable slots filled
        NOW INCLUDES: Character roster and causal event context
        """
        from config import Config
        
        # Calculate word count targets based on time_span
        word_targets = {
            'brief': (500, 700),
            'moderate': (650, 900),
            'epic': (800, 1000)
        }
        
        min_words, max_words = word_targets.get(time_span, (650, 900))
        target_words = (min_words + max_words) // 2
        
        # Get theme-specific vocabulary
        vocab = cls.THEME_VOCABULARY.get(theme, {})
        
        # === BUILD SECTIONS ===
        
        # 1. Semantic Guidance (theme-specific vocabulary)
        semantic_guidance = ""
        if vocab:
            semantic_guidance = f"""SEMANTIC GUIDANCE for {theme}:
- Key entity types: {', '.join(vocab.get('entities', []))}
- Typical events: {', '.join(vocab.get('events', []))}
- Imagery/atmosphere: {', '.join(vocab.get('imagery', []))}

Use these elements naturally in your chronology to maintain thematic consistency."""
        
        # 2. Custom Specifications (user input)
        custom_specifications = ""
        if custom_input:
            custom_specifications = f"""CUSTOM SPECIFICATIONS:
The chronology must incorporate: {custom_input}

Use these details as the initial state - they should influence the entities, events, and narrative arc."""
        
        # 3. Character Requirements (only for first generation)
        character_requirements = ""
        if not character_roster_summary:  # First event - need to introduce characters
            character_requirements = f"""CHARACTER GENERATION REQUIREMENT:
- You MUST introduce exactly {num_characters} distinct main characters in this chronology
- Give each character a unique name, role, and personality
- Make sure all {num_characters} characters play meaningful roles in the story
- Characters should have clear motivations and relationships
- Distribute character focus appropriately across the timeline

Character distribution:
  • {max(1, num_characters // 3)} primary protagonist(s) - central to the story
  • {max(1, num_characters // 2)} supporting character(s) - important roles
  • {max(1, num_characters - (num_characters // 3) - (num_characters // 2))} minor character(s) - smaller but memorable roles"""
        
        # 4. Character Roster (existing characters - subsequent events)
        character_roster = ""
        if character_roster_summary:
            character_roster = f"""{character_roster_summary}

CRITICAL CHARACTER RULES:
- Only use ACTIVE characters in your narrative
- NEVER mention DECEASED characters unless reviving them with in-universe explanation
- Maintain consistency with established character states and actions
- Reference their previous actions and relationships"""
        
        # 5. Causal Context (previous events)
        formatted_causal_context = ""
        if causal_context:
            formatted_causal_context = f"""{causal_context}

CRITICAL CAUSALITY RULES:
- This event MUST be a direct consequence of previous events
- Reference specific characters and events from above context
- Show clear cause-and-effect relationships
- Address at least one open plot thread
- End with a consequence or hook that leads to the next event"""
        
        # === ASSEMBLE FULL PROMPT ===
        system_prompt = cls.BASE_STRUCTURE.format(
            min_words=min_words,
            max_words=max_words,
            target_words=target_words,
            time_span=Config.TIME_SPANS.get(time_span, time_span),
            event_density=Config.EVENT_DENSITIES.get(event_density, event_density),
            narrative_focus=Config.NARRATIVE_FOCUSES.get(narrative_focus, narrative_focus),
            theme=theme,
            character_requirements=character_requirements,
            semantic_guidance=semantic_guidance,
            custom_specifications=custom_specifications,
            character_roster=character_roster,
            causal_context=formatted_causal_context
        )
        
        return system_prompt
