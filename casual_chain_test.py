
from causal_chain import CausalEventChain, EventNode

def test_causal_chain():
    print("=== Testing Causal Event Chain ===\n")
    
    # Create chain
    chain = CausalEventChain()
    
    # Event 1
    print("1. Adding Event 1...")
    event1_content = """
    In the year 1205, King Alaric ascended to the throne of Eldoria. 
    His coronation was met with celebration, but rumors of conspiracy 
    began to spread among the nobility. This unrest would soon threaten 
    the stability of the realm.
    """
    event1 = chain.add_event(1, event1_content.strip())
    chain.analyze_event_and_update(event1, ["King Alaric"])
    
    print(f"Event 1 Summary: {event1.summary}")
    print(f"Open threads: {chain.open_threads}")
    print()
    
    # Event 2
    print("2. Adding Event 2...")
    event2_content = """
    Three years later, the conspiracy reached its climax. An assassin 
    known only as The Shadow struck during a royal feast, killing King Alaric. 
    Queen Lyra, his widow, vowed revenge. The kingdom fell into chaos 
    as nobles scrambled for power.
    """
    event2 = chain.add_event(2, event2_content.strip())
    chain.analyze_event_and_update(event2, ["King Alaric", "The Shadow", "Queen Lyra"])
    
    print(f"Event 2 Summary: {event2.summary}")
    print(f"Characters involved: {event2.affected_characters}")
    print(f"Open threads: {chain.open_threads}")
    print()
    
    # Get context for Event 3
    print("3. Getting causation context for Event 3...")
    context = chain.get_causation_context(num_events=2)
    print(context)
    
    # Build causal prompt
    print("4. Building causal prompt for Event 3...")
    roster_example = """
CHARACTER ROSTER:
ACTIVE: Queen Lyra (protagonist), The Shadow (antagonist)
DECEASED: King Alaric (died in Event 2)
"""
    prompt = chain.build_causal_prompt(3, roster_example)
    print(prompt[:500] + "...\n")
    
    # Chain summary
    print("5. Full chain summary:")
    print(chain.get_chain_summary())

if __name__ == "__main__":
    test_causal_chain()

