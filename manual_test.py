# manual_test.py (UPDATED - Complete version)
"""
Manual testing script with enhanced parameter support
"""
from ai_client import HistoricalFictionGenerator
from config import Config
import json
from pathlib import Path

def print_result(result: dict):
    """Pretty print a generation result with enhanced metadata"""
    print(f"\n{'='*80}")
    print(f"GENERATION RESULT")
    print(f"{'='*80}\n")
    
    print(f"Theme: {result['theme']}")
    print(f"Custom Input: {result['custom_input']}")
    print(f"Success: {result['success']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Meets Requirements: {result['meets_requirements']}")
    print(f"Model: {result['model']}")
    print(f"Generation Time: {result['generation_time_seconds']}s")
    print(f"Tokens Used: {result['tokens_used']}")
    
    # NEW: Print enhanced parameters
    if 'parameters' in result:
        params = result['parameters']
        print(f"\nParameters Used:")
        print(f"  - Time Span: {params.get('time_span', 'N/A')}")
        print(f"  - Event Density: {params.get('event_density', 'N/A')}")
        print(f"  - Narrative Focus: {params.get('narrative_focus', 'N/A')}")
        print(f"  - Multi-Stage: {params.get('multi_stage', 'N/A')}")
    
    # NEW: Print tracked entities
    if 'entities_tracked' in result and result['entities_tracked']:
        print(f"\nEntities Tracked:")
        entities = result['entities_tracked']
        if entities.get('characters'):
            print(f"  - Characters: {', '.join(entities['characters'])}")
        if entities.get('places'):
            print(f"  - Places: {', '.join(entities['places'])}")
    
    # NEW: Print stage information
    if 'stages' in result and result['stages']:
        print(f"\nGeneration Stages:")
        for stage in result['stages']:
            print(f"  - Stage {stage['stage']}: {stage['word_count']} words")
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
    
    print(f"\n{'_'*80}")
    print("GENERATED CONTENT:")
    print(f"{'_'*80}\n")
    
    if result.get('content'):
        print(result['content'])
    else:
        print("[No content generated]")
    
    print(f"\n{'='*80}\n")


def interactive_mode():
    """Run interactive testing mode with enhanced parameters"""
    generator = HistoricalFictionGenerator()

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("HISTORICAL FICTION GENERATOR - Interactive Mode (Enhanced)")
    print("="*80)
    print(f"\nModel: {generator.model_name}")
    print(f"Target: {Config.MIN_WORDS}-{Config.MAX_WORDS} words\n")
    
    while True:
        print("\nAvailable Themes:")
        themes = Config.THEMES
        for i, theme in enumerate(themes, 1):
            print(f"  {i}. {theme}")
        print("  0. Exit")
        
        try:
            choice = input("\nSelect theme (number): ").strip()
            
            if choice == '0':
                print("Exiting...")
                break
            
            theme_idx = int(choice) - 1
            if theme_idx < 0 or theme_idx >= len(themes):
                print("Invalid selection!")
                continue
            
            theme = themes[theme_idx]
            print(f"\nSelected: {theme}")
            
            custom_input = input("Enter custom details (or press Enter for default): ").strip()
            
            print("\n--- Parameters ---")
            
            print("\nTime Span Options:")
            print("  1. Brief (50-100 years)")
            print("  2. Moderate (200-500 years)")
            print("  3. Epic (1000+ years)")
            time_choice = input("Select time span (1-3, default=2): ").strip() or "2"
            time_spans = ["brief", "moderate", "epic"]
            time_span = time_spans[int(time_choice) - 1] if time_choice in ["1", "2", "3"] else "moderate"
            
            print("\nEvent Density Options:")
            print("  1. Sparse (3-5 major events)")
            print("  2. Moderate (6-8 events)")
            print("  3. Rich (10-12 detailed events)")
            density_choice = input("Select event density (1-3, default=2): ").strip() or "2"
            densities = ["sparse", "moderate", "rich"]
            event_density = densities[int(density_choice) - 1] if density_choice in ["1", "2", "3"] else "moderate"
            
            print("\nNarrative Focus Options:")
            print("  1. Political (power, governance, wars)")
            print("  2. Cultural (traditions, art, religion)")
            print("  3. Military (conquests, battles, heroes)")
            print("  4. Economic (trade, resources, wealth)")
            print("  5. Personal (individual lives, relationships)")
            focus_choice = input("Select narrative focus (1-5, default=1): ").strip() or "1"
            focuses = ["political", "cultural", "military", "economic", "personal"]
            narrative_focus = focuses[int(focus_choice) - 1] if focus_choice in ["1", "2", "3", "4", "5"] else "political"
            
            multi_stage_choice = input("\nUse multi-stage generation? (y/n, default=y): ").strip().lower() or "y"
            use_multi_stage = multi_stage_choice == "y"
            
            print("\nGenerating...")
            result = generator.generate(
                theme=theme,
                custom_input=custom_input,
                time_span=time_span,
                event_density=event_density,
                narrative_focus=narrative_focus,
                use_multi_stage=use_multi_stage
            )
            
            print_result(result)
            
            save = input("Save this result? (y/n): ").strip().lower()
            if save == 'y':
                filename = input("Enter filename (without extension): ").strip()
                if filename:
                    # Save to output folder
                    json_path = output_dir / f"{filename}.json"
                    txt_path = output_dir / f"{filename}.txt"
                    
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"✓ Saved to {json_path}")
                    
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(result['content'])
                    print(f"✓ Saved to {txt_path}")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def quick_test():
    """Run a single quick test with enhanced parameters"""
    generator = HistoricalFictionGenerator()
    
    print("Running enhanced quick test with Fantasy Kingdom theme...")
    result = generator.generate(
        theme="Fantasy Kingdom",
        custom_input="A kingdom built inside a massive tree that reaches the clouds",
        time_span="moderate",
        event_density="moderate",
        narrative_focus="political",
        use_multi_stage=True
    )
    
    print_result(result)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_test()
    else:
        interactive_mode()
