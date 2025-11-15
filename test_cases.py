# test_cases.py (UPDATED - Enhanced test cases)
"""
Test cases with parameter variation for comprehensive testing
Demonstrates all course concepts in action
"""

TEST_CASES = [
    # Fantasy Kingdom - Testing different time spans
    {
        "theme": "Fantasy Kingdom",
        "custom_input": "A kingdom built on floating islands connected by magical bridges, ruled by dragon riders",
        "time_span": "epic",
        "event_density": "rich",
        "narrative_focus": "political",
        "use_multi_stage": True
    },
    {
        "theme": "Fantasy Kingdom",
        "custom_input": "An underground dwarven kingdom that discovered a sentient crystal",
        "time_span": "brief",
        "event_density": "sparse",
        "narrative_focus": "cultural",
        "use_multi_stage": True
    },
    {
        "theme": "Fantasy Kingdom",
        "custom_input": "",  # Minimal input test
        "time_span": "moderate",
        "event_density": "moderate",
        "narrative_focus": "military",
        "use_multi_stage": False  # Test single-stage
    },
    
    # Future prophecy - Testing narrative focuses
    {
        "theme": "Future prophecy",
        "custom_input": "A prophecy foretelling the rise of an AI that will either save or destroy humanity",
        "time_span": "moderate",
        "event_density": "moderate",
        "narrative_focus": "personal",
        "use_multi_stage": True
    },
    {
        "theme": "Future prophecy",
        "custom_input": "Ancient prediction about the return of magic to a science-dominated world in 2087",
        "time_span": "brief",
        "event_density": "rich",
        "narrative_focus": "cultural",
        "use_multi_stage": True
    },
    
    # Apocalyptic survivors - Testing event densities
    {
        "theme": "Survivors of an apocalyptic event",
        "custom_input": "Survivors of a global fungal outbreak that turned humans into plant-hybrid beings",
        "time_span": "moderate",
        "event_density": "rich",
        "narrative_focus": "political",
        "use_multi_stage": True
    },
    {
        "theme": "Survivors of an apocalyptic event",
        "custom_input": "After the sun's radiation doubled, humanity must live underground",
        "time_span": "epic",
        "event_density": "sparse",
        "narrative_focus": "economic",
        "use_multi_stage": True
    },
    
    # Imaginary creature
    {
        "theme": "Imaginary creature",
        "custom_input": "Cloud whales that swim through the atmosphere and feed on lightning",
        "time_span": "epic",
        "event_density": "moderate",
        "narrative_focus": "cultural",
        "use_multi_stage": True
    },
    {
        "theme": "Imaginary creature",
        "custom_input": "Shadow cats that can phase between dimensions",
        "time_span": "moderate",
        "event_density": "rich",
        "narrative_focus": "personal",
        "use_multi_stage": True
    },
    
    # World event/holiday
    {
        "theme": "Imaginary world event or holiday",
        "custom_input": "The Festival of Fallen Stars, celebrating when asteroids brought magic to Earth",
        "time_span": "epic",
        "event_density": "moderate",
        "narrative_focus": "cultural",
        "use_multi_stage": True
    },
    {
        "theme": "Imaginary world event or holiday",
        "custom_input": "Convergence Day, when parallel dimensions overlap for 24 hours every decade",
        "time_span": "moderate",
        "event_density": "rich",
        "narrative_focus": "political",
        "use_multi_stage": True
    },
    
    # Cultural myth
    {
        "theme": "Cultural myth or legend",
        "custom_input": "The legend of the Mirror City, a perfect civilization that exists in reflections",
        "time_span": "epic",
        "event_density": "moderate",
        "narrative_focus": "cultural",
        "use_multi_stage": True
    },
    {
        "theme": "Cultural myth or legend",
        "custom_input": "The myth of the First Programmer, who coded reality itself",
        "time_span": "moderate",
        "event_density": "sparse",
        "narrative_focus": "personal",
        "use_multi_stage": True
    },
    
    # Family lineage
    {
        "theme": "Lineage of a family",
        "custom_input": "The Chen family, guardians of a portal between worlds for ten generations",
        "time_span": "epic",
        "event_density": "rich",
        "narrative_focus": "personal",
        "use_multi_stage": True
    },
    {
        "theme": "Lineage of a family",
        "custom_input": "A family cursed with prophetic dreams from medieval times to present",
        "time_span": "epic",
        "event_density": "moderate",
        "narrative_focus": "cultural",
        "use_multi_stage": True
    },
    
    # Reimagined Singapore
    {
        "theme": "Reimagined Singapore",
        "custom_input": "Singapore became the world's first fully underwater city after sea levels rose",
        "time_span": "moderate",
        "event_density": "rich",
        "narrative_focus": "economic",
        "use_multi_stage": True
    },
    {
        "theme": "Reimagined Singapore",
        "custom_input": "Singapore as a sovereign kingdom of spice traders in the 1400s",
        "time_span": "epic",
        "event_density": "moderate",
        "narrative_focus": "political",
        "use_multi_stage": True
    },
    
    # Alien planet
    {
        "theme": "Alien planet",
        "custom_input": "A tidally-locked planet where civilization exists in the twilight zone",
        "time_span": "epic",
        "event_density": "rich",
        "narrative_focus": "political",
        "use_multi_stage": True
    },
    {
        "theme": "Alien planet",
        "custom_input": "A gas giant moon with crystalline forests and silicon-based life",
        "time_span": "moderate",
        "event_density": "moderate",
        "narrative_focus": "cultural",
        "use_multi_stage": True
    },
    
    # Interesting object
    {
        "theme": "Interesting object (work of art, enchanted artifact, spaceship)",
        "custom_input": "An ancient violin that plays the memories of everyone who has ever owned it",
        "time_span": "epic",
        "event_density": "rich",
        "narrative_focus": "personal",
        "use_multi_stage": True
    },
    {
        "theme": "Interesting object (work of art, enchanted artifact, spaceship)",
        "custom_input": "The generation ship Prometheus, from construction to arrival",
        "time_span": "epic",
        "event_density": "moderate",
        "narrative_focus": "military",
        "use_multi_stage": True
    },
]

# Quick test cases for rapid validation
QUICK_TEST_CASES = [
    {
        "theme": "Fantasy Kingdom",
        "custom_input": "A small kingdom with a magical library",
        "time_span": "brief",
        "event_density": "sparse",
        "narrative_focus": "cultural",
        "use_multi_stage": False
    },
    {
        "theme": "Imaginary creature",
        "custom_input": "A creature that feeds on dreams",
        "time_span": "moderate",
        "event_density": "moderate",
        "narrative_focus": "personal",
        "use_multi_stage": True
    },
    {
        "theme": "Reimagined Singapore",
        "custom_input": "Singapore in a steampunk alternate history",
        "time_span": "moderate",
        "event_density": "rich",
        "narrative_focus": "economic",
        "use_multi_stage": True
    },
]

# Edge case tests
EDGE_CASE_TESTS = [
    {
        'theme': 'Fantasy Kingdom',
        'custom_input': 'Focus on character deaths and succession',
        'time_span': 'epic',
        'event_density': 'rich',
        'narrative_focus': 'personal',
        'use_multi_stage': True,
        'num_characters': 10  # Test maximum
    },
    {
        'theme': 'Alien Planet',
        'custom_input': 'Multiple character deaths and revivals',
        'time_span': 'moderate',
        'event_density': 'moderate',
        'narrative_focus': 'political',
        'use_multi_stage': True,
        'num_characters': 3  # Test minimum
    }
]