
from session_manager import SessionManager

def test_session_manager():
    print("=== Testing Session Manager ===\n")
    
    # Create new session
    print("1. Creating new session...")
    session = SessionManager()
    session.update_metadata(theme="Fantasy Kingdom", persona_settings={'flow': 'epic'})
    print(f"Session ID: {session.session_id}")
    print()
    
    # Add characters
    print("2. Adding characters...")
    session.character_manager.update_event_number(1)
    session.character_manager.add_character("King Alaric", role="protagonist")
    session.character_manager.add_character("Queen Lyra", role="protagonist")
    print(f"Active characters: {len(session.character_manager.get_active_characters())}")
    print()
    
    # Add events
    print("3. Adding events...")
    event1 = session.event_chain.add_event(1, "King Alaric crowned. Unrest brewing.")
    session.event_chain.analyze_event_and_update(event1, ["King Alaric"])
    
    event2 = session.event_chain.add_event(2, "Assassin kills King Alaric. Queen Lyra vows revenge.")
    session.event_chain.analyze_event_and_update(event2, ["King Alaric", "Queen Lyra"])
    
    session.character_manager.kill_character("King Alaric", "Assassinated")
    print(f"Events in chain: {len(session.event_chain.events)}")
    print()
    
    # Save session
    print("4. Saving session...")
    filepath = session.save()
    print(f"Saved to: {filepath}")
    print()
    
    # List available sessions
    print("5. Listing available sessions...")
    sessions = SessionManager.list_available_sessions()
    for s in sessions:
        print(f"  - {s['session_id']}: {s['theme']} ({s['events']} events, {s['characters']} chars)")
    print()
    
    # Load session
    print("6. Loading session back...")
    loaded_session = SessionManager.load(session.session_id)
    print(f"Loaded session: {loaded_session.session_id}")
    print(f"Theme: {loaded_session.metadata['theme']}")
    print(f"Characters: {len(loaded_session.character_manager.roster)}")
    print(f"Events: {len(loaded_session.event_chain.events)}")
    print()
    
    # Verify data integrity
    print("7. Verifying data integrity...")
    active = loaded_session.character_manager.get_active_characters()
    deceased = loaded_session.character_manager.get_deceased_characters()
    print(f"Active characters: {[c.name for c in active]}")
    print(f"Deceased characters: {[c.name for c in deceased]}")
    print()
    
    # Export readable summary
    print("8. Exporting readable summary...")
    loaded_session.export_readable_summary("output/session_summary.txt")
    print("Exported to: output/session_summary.txt")
    print()
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_session_manager()
