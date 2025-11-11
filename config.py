
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
    
    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return True
