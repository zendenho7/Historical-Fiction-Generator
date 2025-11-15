"""
Test character lifecycle and consistency
"""
from ai_client import HistoricalFictionGenerator
from session_manager import SessionManager

def test_character_death_consistency():
    """Test that dead characters don't reappear"""
    generator = HistoricalFictionGenerator()
    session = SessionManager()
    
    # Generate first event
    result1 = generator.generate(
        theme='Fantasy Kingdom',
        custom_input='King Aldric dies in a battle',
        session_manager=session,
        num_characters=5
    )
    
    # Manually mark character as dead
    session.character_manager.kill_character('King Aldric', 'Died in battle')
    
    # Generate second event
    result2 = generator.generate(
        theme='Fantasy Kingdom', 
        custom_input='Continue the story',
        session_manager=session,
        num_characters=5
    )
    
    # Validate
    is_valid, violations = session.character_manager.validate_character_usage(
        result2['content']
    )
    
    assert is_valid, f"Dead character appeared: {violations}"
    print("✅ Character lifecycle test passed!")

if __name__ == "__main__":
    test_character_death_consistency()
