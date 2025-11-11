"""
Prompt engineering templates for different themes
Each template is optimized for chronological narrative generation
"""

class PromptTemplates:
    """Collection of prompt templates for historical fiction generation"""
    
    # Base system prompt for all themes
    SYSTEM_BASE = """You are an expert historical fiction writer specializing in creating detailed, believable chronologies.

Your task is to generate a chronological narrative that:
1. Contains between 500-1000 words
2. Presents events in clear chronological order with specific dates/timeframes
3. Maintains internal consistency and logical progression
4. Uses rich, evocative language appropriate to the theme
5. Creates believable cause-and-effect relationships between events
6. Includes specific details that make the history feel authentic

Format your response as a narrative chronology with clear temporal markers (dates, years, eras, etc.).
Do not include meta-commentary or explanations outside the narrative itself."""

    # Theme-specific templates
    TEMPLATES = {
        "Fantasy Kingdom": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of a fantasy kingdom.

Theme: Fantasy Kingdom
Custom Details: {custom_input}

The chronology should include:
- Founding/origin events
- Major rulers or dynasties
- Significant wars, alliances, or political changes
- Cultural or magical developments
- Rise and/or fall of power
- Key artifacts, prophecies, or legendary figures

Create a rich, believable history spanning multiple generations or centuries."""
        },
        
        "Future prophecy": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological account of a prophecy and its fulfillment in the future.

Theme: Future Prophecy
Custom Details: {custom_input}

The chronology should include:
- Discovery or utterance of the original prophecy
- Initial interpretations and reactions
- Key events that seem to align with prophetic elements
- Misinterpretations or false fulfillments
- The actual fulfillment (or subversion) of the prophecy
- Aftermath and legacy

Create a narrative that spans from prophecy to fulfillment with compelling temporal progression."""
        },
        
        "Survivors of an apocalyptic event": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of survivors following an apocalyptic event.

Theme: Apocalyptic Survivors
Custom Details: {custom_input}

The chronology should include:
- The apocalyptic event itself (briefly)
- Immediate survival period and challenges
- Formation of communities or factions
- Technological/social adaptations
- Conflicts and alliances between survivor groups
- Long-term rebuilding or evolution of society
- Rediscovery or loss of pre-apocalyptic knowledge

Create a compelling narrative of survival and adaptation over time."""
        },
        
        "Imaginary creature": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of an imaginary creature.

Theme: Imaginary Creature
Custom Details: {custom_input}

The chronology should include:
- First recorded sightings or ancient origins
- Evolution or changes over time
- Relationships with other species (especially humans/intelligent beings)
- Habitats and migrations
- Role in ecosystems or civilizations
- Mythological or cultural significance
- Current status and future prospects

Create a natural history that feels scientifically or mythologically grounded."""
        },
        
        "Imaginary world event or holiday": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of an imaginary world event or holiday.

Theme: Imaginary World Event/Holiday
Custom Details: {custom_input}

The chronology should include:
- Originating event or reason for the celebration
- Early forms and traditions
- Evolution of customs and practices over time
- Significant changes or controversies
- Cultural or political significance
- Modern celebrations or observances
- Variations across different regions or cultures

Create a rich cultural history that spans generations."""
        },
        
        "Cultural myth or legend": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological account of a cultural myth or legend's evolution.

Theme: Cultural Myth or Legend
Custom Details: {custom_input}

The chronology should include:
- Origins (historical events or ancient storytelling)
- Earliest recorded versions
- Evolution and variations across time periods
- Cultural or religious significance
- Influence on art, literature, or society
- Modern interpretations or adaptations
- Archaeological or historical evidence (real or imagined)

Create a narrative that traces the myth from origin to modern understanding."""
        },
        
        "Lineage of a family": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of a family lineage.

Theme: Family Lineage
Custom Details: {custom_input}

The chronology should include:
- Founding ancestor or earliest known generation
- Key figures in each generation and their achievements
- Family traditions, values, or secrets
- Marriages, alliances, and inheritance
- Conflicts, scandals, or tragedies
- Changes in fortune, status, or location
- Legacy and modern descendants

Create a multi-generational saga with interconnected character arcs."""
        },
        
        "Reimagined Singapore": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of a reimagined Singapore.

Theme: Reimagined Singapore
Custom Details: {custom_input}

The chronology should include:
- Point of divergence from real history
- Alternative developments in governance, culture, or technology
- Key historical figures (real or imagined) and their roles
- Economic, social, or environmental changes
- Relationships with neighboring countries
- Cultural evolution and identity
- Present-day state of this alternate Singapore

Create an alternate history that feels grounded in Singapore's real geography and culture."""
        },
        
        "Alien planet": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of an alien planet.

Theme: Alien Planet
Custom Details: {custom_input}

The chronology should include:
- Planetary formation and early conditions
- Evolution of life (if applicable)
- Development of civilizations or dominant species
- Major geological, climatic, or cosmic events
- Technological or cultural evolution
- First contact with other worlds (if applicable)
- Current state and future trajectory

Create a planetary history that spans geological and civilizational timescales."""
        },
        
        "Interesting object (work of art, enchanted artifact, spaceship)": {
            "system": SYSTEM_BASE,
            "user_template": """Generate a detailed chronological history of an interesting object.

Theme: Interesting Object
Custom Details: {custom_input}

The chronology should include:
- Creation or discovery of the object
- Original purpose and creator
- Ownership history and notable owners
- Significant events involving the object
- Changes to the object over time
- Cultural or historical significance
- Current location and condition
- Legends or mysteries surrounding it

Create a biography of the object that spans its entire existence."""
        }
    }
    
    @staticmethod
    def get_prompt(theme: str, custom_input: str = "") -> tuple:
        """
        Get system and user prompts for a specific theme
        
        Args:
            theme: The theme name
            custom_input: Custom user input to incorporate
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        if theme not in PromptTemplates.TEMPLATES:
            raise ValueError(f"Unknown theme: {theme}. Available themes: {list(PromptTemplates.TEMPLATES.keys())}")
        
        template = PromptTemplates.TEMPLATES[theme]
        system_prompt = template["system"]
        user_prompt = template["user_template"].format(custom_input=custom_input if custom_input else "Generate a creative and original chronology.")
        
        return system_prompt, user_prompt
    
    @staticmethod
    def list_themes() -> list:
        """Get list of all available themes"""
        return list(PromptTemplates.TEMPLATES.keys())
