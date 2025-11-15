
from character_manager import CharacterManager

def test_character_manager():
    print("=== Testing Character Manager ===\n")
    
    # Create manager
    manager = CharacterManager()
    manager.update_event_number(1)
    
    # Add characters
    print("1. Adding characters...")
    manager.add_character("King Alaric", role="protagonist", event_num=1)
    manager.add_character("Queen Lyra", role="protagonist", event_num=1)
    manager.add_character("The Assassin", role="antagonist", event_num=2)
    
    print("Active characters:", [c.name for c in manager.get_active_characters()])
    print()
    
    # Kill a character
    print("2. Event 3: Assassin kills King Alaric...")
    manager.update_event_number(3)
    manager.kill_character("King Alaric", cause="Assassinated by The Assassin")
    
    print("Active characters:", [c.name for c in manager.get_active_characters()])
    print("Deceased:", [c.name for c in manager.get_deceased_characters()])
    print()
    
    # Test validation
    print("3. Testing validation...")
    test_text_valid = "Queen Lyra mourned the loss of her husband."
    test_text_invalid = "King Alaric attended the ceremony."
    
    valid, violations = manager.validate_character_usage(test_text_valid)
    print(f"Valid text: {valid}")
    
    valid, violations = manager.validate_character_usage(test_text_invalid)
    print(f"Invalid text (mentions dead character): {valid}")
    if violations:
        print(f"Violations: {violations}")
    print()
    
    # Get roster summary
    print("4. Roster Summary for AI:")
    print(manager.get_roster_summary())

if __name__ == "__main__":
    test_character_manager()

