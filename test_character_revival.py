"""
Test revival detection patterns
"""
import re

def test_revival_detection():
    """Test revival patterns on sample text"""
    
    # Sample texts with various revival scenarios
    test_cases = [
        "Queen Lyra was resurrected by ancient magic.",
        "Through divine intervention, King Alaric was brought back to life.",
        "The necromancer's ritual revived Prince Theron from death.",
        "Commander Elara returned from the dead, shocking the kingdom.",
        "It was revealed that Duke Marcus wasn't actually dead - he had survived.",
        "Scholar Mira rose from the ashes like a phoenix.",
        "The resurrection of Lord Vorlag was accomplished through forbidden magic.",
        "Believed to be dead, Blacksmith Gareth emerged from the ruins alive.",
        "A miracle saved Princess Anya from death at the last moment.",
        "The healing spell revived General Kael just in time.",
    ]
    
    revival_patterns = [
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:was|were|is|are)\s+(?:revived|resurrected|reborn|brought\s+back|restored\s+to\s+life)",
        r"(?:revives?|resurrects?|brings?\s+back|restores?)\s+([A-Z]\w+(?:\s+[A-Z]\w+)?)",
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:returns?|returned|comes?\s+back|came\s+back)\s+(?:from\s+the\s+dead|to\s+life)",
        r"(?:resurrection|rebirth|revival)\s+of\s+([A-Z]\w+(?:\s+[A-Z]\w+)?)",
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:wasn't|was\s+not|weren't|were\s+not)\s+(?:actually\s+)?(?:dead|killed)",
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:survived|had\s+survived)",
        r"(?:believed|thought|presumed)\s+(?:to\s+be\s+)?dead,?\s+([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:emerged|appeared|returned)",
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:rises?|rose)\s+(?:from\s+the\s+(?:dead|grave|ashes))",
        r"(?:miracle|healing\s+spell)\s+(?:saved|revived)\s+([A-Z]\w+(?:\s+[A-Z]\w+)?)",
    ]
    
    print("✨ Testing Revival Detection Patterns\n")
    
    for i, text in enumerate(test_cases, 1):
        print(f"Test {i}: {text}")
        detected = False
        
        for pattern in revival_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    char_name = match if isinstance(match, str) else match[0]
                    print(f"  ✅ DETECTED: {char_name}")
                    detected = True
        
        if not detected:
            print(f"  ❌ NOT DETECTED")
        print()

def test_invalid_revival_attempts():
    """Test that casual mentions DON'T trigger revival"""
    
    invalid_cases = [
        # These should NOT trigger revival
        ("Queen Lyra leads the troops into battle.", False),  # Casual mention, no revival
        ("The council remembers Queen Lyra's wisdom.", False),  # Past reference
        ("Queen Lyra's legacy lives on.", False),  # Legacy mention
        ("In memory of Queen Lyra.", False),  # Memorial
        ("King Alaric thinks of Queen Lyra.", False),  # Someone thinking of them
        
        # These SHOULD trigger revival
        ("Queen Lyra was resurrected by ancient magic.", True),
        ("It was revealed that Queen Lyra wasn't actually dead.", True),
        ("Through a miracle, Queen Lyra returned from the dead.", True),
    ]
    
    revival_keywords = [
        'revive', 'revived', 'resurrect', 'resurrected', 'resurrection',
        'brought back', 'return from death', 'not dead', "wasn't dead",
        'survived', 'miracle', 'divine intervention'
    ]
    
    revival_patterns = [
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:was|were|is|are)\s+(?:revived|resurrected|reborn|brought\s+back\s+(?:to\s+life|from\s+(?:the\s+)?dead))",
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+(?:wasn't|was\s+not)\s+(?:actually\s+)?dead",
        r"([A-Z]\w+(?:\s+[A-Z]\w+)?)\s+returned\s+from\s+(?:the\s+)?dead",
    ]
    
    print("\n🧪 Testing Invalid Revival Attempt Detection\n")
    
    passed = 0
    failed = 0
    
    for text, should_detect in invalid_cases:
        # Check for revival keywords
        has_keywords = any(keyword in text.lower() for keyword in revival_keywords)
        
        # Check for pattern match
        has_pattern = False
        for pattern in revival_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                has_pattern = True
                break
        
        # Both must be true for valid revival
        detected = has_keywords and has_pattern
        
        status = "✅ PASS" if detected == should_detect else "❌ FAIL"
        if detected == should_detect:
            passed += 1
        else:
            failed += 1
        
        print(f"{status}: {text}")
        print(f"         Expected: {'Revival' if should_detect else 'No Revival'}, "
              f"Got: {'Revival' if detected else 'No Revival'}")
        print()
    
    print(f"\nResults: {passed} passed, {failed} failed out of {len(invalid_cases)} tests")
    return failed == 0

if __name__ == "__main__":
    test_revival_detection()
    print("\n" + "="*60 + "\n")
    test_invalid_revival_attempts()
