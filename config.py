
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-1.5-flash')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1500))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
    MIN_WORDS = 500
    MAX_WORDS = 1000

    THEMES = [
        "Fantasy Kingdom",
        "Future prophecy",
        "Survivors of an apocalyptic event",
        "Imaginary creature",
        "Imaginary world event or holiday",
        "Cultural myth or legend",
        "Lineage of a family",
        "Reimagined Singapore",
        "Alien planet",
        "Interesting object (work of art, enchanted artifact, spaceship)"
    ]
    
    # NEW: Parameter-driven content variation
    TIME_SPANS = {
        "brief": "spanning 50-100 years",
        "moderate": "spanning 200-500 years",
        "epic": "spanning 1000+ years"
    }
    
    EVENT_DENSITIES = {
        "sparse": "3-5 major events",
        "moderate": "6-8 significant events",
        "rich": "10-12 detailed events"
    }
    
    NARRATIVE_FOCUSES = {
        "political": "political power, governance, wars, alliances",
        "cultural": "cultural evolution, traditions, art, religion",
        "military": "conquests, battles, strategies, heroes",
        "economic": "trade, resources, wealth, technology",
        "personal": "individual lives, relationships, personal journeys"
    }

    # === PERSONA SYSTEM ===
    PERSONA_PRESETS = {
        "Smooth Storyteller": {
            "description": "Balanced pacing with smooth transitions and emotional depth",
            "temperature": 0.7,
            "instructions": """
            NARRATIVE PERSONA: Smooth Storyteller
            
            Your writing style emphasizes:
            • Smooth transitions between events (use phrases like "Following this...", "In response...", "As a result...")
            • Emotional beats that show character reactions and consequences
            • Consistent pacing - don't rush major events or dwell too long on minor ones
            • Clear cause-and-effect logic that makes the story flow naturally
            • Soft hooks between scenes that create anticipation without cliffhangers
            
            Avoid: Abrupt jumps, disconnected events, robotic listing of facts
            """
        },
        
        "Epic Chronicler": {
            "description": "Grand, sweeping narratives with dramatic moments",
            "temperature": 0.8,
            "instructions": """
            NARRATIVE PERSONA: Epic Chronicler
            
            Your writing style emphasizes:
            • Dramatic tension and high-stakes moments
            • Sweeping, grand-scale events that shape entire civilizations
            • Powerful imagery and evocative language
            • Strong emotional highs and lows
            • Epic scope with lasting consequences
            
            Maintain: Gravitas, weight, significance in every event
            """
        },
        
        "Intimate Historian": {
            "description": "Personal focus on characters and human stories",
            "temperature": 0.6,
            "instructions": """
            NARRATIVE PERSONA: Intimate Historian
            
            Your writing style emphasizes:
            • Character-driven storytelling with deep emotional resonance
            • Personal relationships and their evolution over time
            • Human motivations and internal conflicts
            • Detailed character actions and reactions
            • Intimate moments that reveal character depth
            
            Focus on: The human element, personal stakes, emotional truth
            """
        },
        
        "Analytical Archivist": {
            "description": "Precise, logical progression with clear causality",
            "temperature": 0.5,
            "instructions": """
            NARRATIVE PERSONA: Analytical Archivist
            
            Your writing style emphasizes:
            • Logical progression of events with explicit cause-and-effect
            • Precise details and factual consistency
            • Clear documentation of changes over time
            • Systematic analysis of patterns and trends
            • Objective tone with minimal emotional embellishment
            
            Prioritize: Accuracy, clarity, logical consistency
            """
        }
    }

    DEFAULT_PERSONA = "Smooth Storyteller"
    
    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return True
