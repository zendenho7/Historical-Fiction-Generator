# test_runner.py (UPDATED - Enhanced reporting)
"""
Test runner with enhanced parameter tracking and reporting
"""
import json
import csv
from datetime import datetime
from pathlib import Path
from ai_client import HistoricalFictionGenerator
from test_cases import TEST_CASES, QUICK_TEST_CASES
from config import Config

class TestRunner:
    """Enhanced test runner with parameter tracking"""
    
    def __init__(self, output_dir: str = "test_results"):
        """Initialize test runner with output directory"""
        self.generator = HistoricalFictionGenerator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def run_tests(self, test_cases: list = None, test_name: str = "test") -> dict:
        """Run test suite with enhanced tracking"""
        if test_cases is None:
            test_cases = TEST_CASES
        
        print(f"\n{'='*60}")
        print(f"Running Test Suite: {test_name}")
        print(f"Total Test Cases: {len(test_cases)}")
        print(f"Model: {self.generator.model_name}")
        print(f"{'='*60}\n")
        
        # Run generation
        results = self.generator.batch_generate(test_cases)
        
        # Generate reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary = self._generate_summary(results)
        
        # Save results
        self._save_json_report(results, f"{test_name}_{timestamp}.json")
        self._save_csv_report(results, f"{test_name}_{timestamp}.csv")
        self._save_detailed_report(results, f"{test_name}_{timestamp}_detailed.txt")
        
        # Print summary
        self._print_summary(summary)
        
        return summary
    
    def _generate_summary(self, results: list) -> dict:
        """Generate summary statistics with parameter breakdown"""
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        meets_requirements = sum(1 for r in results if r['meets_requirements'])
        
        word_counts = [r['word_count'] for r in results if r['success']]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        
        generation_times = [r['generation_time_seconds'] for r in results]
        avg_time = sum(generation_times) / len(generation_times) if generation_times else 0
        
        # NEW: Parameter usage statistics
        multi_stage_count = sum(1 for r in results if r.get('parameters', {}).get('multi_stage'))
        
        # Count parameter distributions
        time_spans = {}
        event_densities = {}
        narrative_focuses = {}
        
        for r in results:
            params = r.get('parameters', {})
            ts = params.get('time_span', 'unknown')
            ed = params.get('event_density', 'unknown')
            nf = params.get('narrative_focus', 'unknown')
            
            time_spans[ts] = time_spans.get(ts, 0) + 1
            event_densities[ed] = event_densities.get(ed, 0) + 1
            narrative_focuses[nf] = narrative_focuses.get(nf, 0) + 1
        
        total_tokens = 0
        for r in results:
            if r['success']:
                tokens = r.get('tokens_used', 0)
                if isinstance(tokens, (int, float)) and tokens != 0:
                    total_tokens += tokens
        
        tokens_display = total_tokens if total_tokens > 0 else "N/A (Gemini doesn't report tokens)"
        
        return {
            "total_tests": total,
            "successful": successful,
            "failed": total - successful,
            "meets_word_requirements": meets_requirements,
            "compliance_rate": f"{(meets_requirements/total*100):.1f}%" if total > 0 else "0%",
            "avg_word_count": round(avg_words, 1),
            "avg_generation_time": round(avg_time, 2),
            "total_tokens_used": tokens_display,
            "multi_stage_used": multi_stage_count,
            "parameter_distribution": {
                "time_spans": time_spans,
                "event_densities": event_densities,
                "narrative_focuses": narrative_focuses
            }
        }
    
    def _save_json_report(self, results: list, filename: str):
        """Save results as JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON report saved: {filepath}")
    
    def _save_csv_report(self, results: list, filename: str):
        """Save results as CSV with enhanced fields"""
        filepath = self.output_dir / filename
        
        fieldnames = [
            'timestamp', 'theme', 'success', 'word_count', 'meets_requirements',
            'model', 'generation_time_seconds', 'tokens_used', 'custom_input', 'error',
            'time_span', 'event_density', 'narrative_focus', 'multi_stage',
            'entities_found'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                params = result.get('parameters', {})
                entities = result.get('entities_tracked', {})
                all_entities = []
                for ent_type, ent_list in entities.items():
                    all_entities.extend(ent_list)
                
                row = {
                    'timestamp': result.get('timestamp', ''),
                    'theme': result.get('theme', ''),
                    'success': result.get('success', False),
                    'word_count': result.get('word_count', 0),
                    'meets_requirements': result.get('meets_requirements', False),
                    'model': result.get('model', ''),
                    'generation_time_seconds': result.get('generation_time_seconds', 0),
                    'tokens_used': result.get('tokens_used', ''),
                    'custom_input': result.get('custom_input', ''),
                    'error': result.get('error', ''),
                    'time_span': params.get('time_span', ''),
                    'event_density': params.get('event_density', ''),
                    'narrative_focus': params.get('narrative_focus', ''),
                    'multi_stage': params.get('multi_stage', False),
                    'entities_found': ', '.join(all_entities[:5]) if all_entities else ''
                }
                writer.writerow(row)
        
        print(f"✓ CSV report saved: {filepath}")
    
    def _save_detailed_report(self, results: list, filename: str):
        """Save detailed text report with enhanced metadata"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("DETAILED TEST RESULTS (ENHANCED)\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"TEST CASE #{i}\n")
                f.write(f"{'='*80}\n\n")
                
                f.write(f"Theme: {result['theme']}\n")
                f.write(f"Custom Input: {result['custom_input']}\n")
                f.write(f"Success: {result['success']}\n")
                f.write(f"Word Count: {result['word_count']}\n")
                f.write(f"Meets Requirements (500-1000 words): {result['meets_requirements']}\n")
                f.write(f"Model: {result['model']}\n")
                f.write(f"Generation Time: {result['generation_time_seconds']}s\n")
                f.write(f"Tokens Used: {result.get('tokens_used', 'N/A')}\n")
                f.write(f"Timestamp: {result['timestamp']}\n")
                
                # NEW: Write enhanced parameters
                if 'parameters' in result:
                    params = result['parameters']
                    f.write(f"\nGeneration Parameters:\n")
                    f.write(f"  - Time Span: {params.get('time_span', 'N/A')}\n")
                    f.write(f"  - Event Density: {params.get('event_density', 'N/A')}\n")
                    f.write(f"  - Narrative Focus: {params.get('narrative_focus', 'N/A')}\n")
                    f.write(f"  - Multi-Stage: {params.get('multi_stage', 'N/A')}\n")
                
                # NEW: Write tracked entities
                if 'entities_tracked' in result and result['entities_tracked']:
                    f.write(f"\nTracked Entities:\n")
                    entities = result['entities_tracked']
                    if entities.get('characters'):
                        f.write(f"  - Characters: {', '.join(entities['characters'])}\n")
                    if entities.get('places'):
                        f.write(f"  - Places: {', '.join(entities['places'])}\n")
                    if entities.get('items'):
                        f.write(f"  - Items: {', '.join(entities['items'])}\n")
                    if entities.get('factions'):
                        f.write(f"  - Factions: {', '.join(entities['factions'])}\n")
                
                # NEW: Write stage information
                if 'stages' in result and result['stages']:
                    f.write(f"\nGeneration Stages:\n")
                    for stage in result['stages']:
                        f.write(f"  - Stage {stage['stage']}: {stage['word_count']} words")
                        if 'entities_found' in stage:
                            f.write(f" (Found {len(stage['entities_found'])} entities)")
                        f.write("\n")
                
                if result.get('error'):
                    f.write(f"\nError: {result['error']}\n")
                
                f.write(f"\n{'_'*80}\n")
                f.write("GENERATED CONTENT:\n")
                f.write(f"{'_'*80}\n\n")
                
                if result.get('content'):
                    f.write(result['content'])
                else:
                    f.write("[No content generated]")
                
                f.write("\n\n")
        
        print(f"✓ Detailed report saved: {filepath}")
    
    def _print_summary(self, summary: dict):
        """Print enhanced summary to console"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY (ENHANCED)")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Meets Word Requirements: {summary['meets_word_requirements']}")
        print(f"Compliance Rate: {summary['compliance_rate']}")
        print(f"Average Word Count: {summary['avg_word_count']}")
        print(f"Average Generation Time: {summary['avg_generation_time']}s")
        print(f"Total Tokens Used: {summary['total_tokens_used']}")
        print(f"Multi-Stage Generations: {summary['multi_stage_used']}")
        
        # NEW: Print parameter distribution
        print(f"\nParameter Distribution:")
        param_dist = summary['parameter_distribution']
        
        print(f"  Time Spans:")
        for span, count in param_dist['time_spans'].items():
            print(f"    - {span}: {count}")
        
        print(f"  Event Densities:")
        for density, count in param_dist['event_densities'].items():
            print(f"    - {density}: {count}")
        
        print(f"  Narrative Focuses:")
        for focus, count in param_dist['narrative_focuses'].items():
            print(f"    - {focus}: {count}")
        
        print(f"{'='*60}\n")


def main():
    """Main test execution function"""
    import sys
    
    runner = TestRunner()
    
    # Determine which test suite to run
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        print("Running QUICK test suite (enhanced parameters)...")
        runner.run_tests(QUICK_TEST_CASES, "quick_test")
    else:
        print("Running FULL test suite (enhanced parameters)...")
        print("(Use --quick flag for faster testing with fewer cases)")
        runner.run_tests(TEST_CASES, "full_test")


if __name__ == "__main__":
    main()