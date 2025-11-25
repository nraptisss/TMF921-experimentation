"""
Comprehensive error analysis and categorization.

Analyzes failure modes systematically to identify patterns and improvement opportunities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
from typing import Dict, List
from collections import Counter, defaultdict
import pandas as pd


class ErrorAnalyzer:
    """
    Systematic error analysis and categorization.
    """
    
    def __init__(self):
        self.error_categories = defaultdict(list)
        
    def analyze_failures(self, results: List[Dict]) -> Dict:
        """
        Categorize and analyze all failures.
        
        Args:
            results: List of experiment results
            
        Returns:
            Dictionary of error categories with examples
        """
        failures = [r for r in results if not r.get('validation', {}).get('overall_valid', False)]
        
        print("\n" + "="*80)
        print("ERROR ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Results: {len(results)}")
        print(f"Failures: {len(failures)} ({len(failures)/len(results)*100:.1f}%)")
        print(f"Successes: {len(results) - len(failures)} ({(len(results)-len(failures))/len(results)*100:.1f}%)")
        
        if not failures:
            print("\n[SUCCESS] No failures to analyze!")
            return {}
        
        # Categorize errors
        for failure in failures:
            self._categorize_failure(failure)
        
        # Report by category
        print("\n" + "-"*80)
        print("ERROR CATEGORIES")
        print("-"*80)
        
        total_failures = len(failures)
        
        for category, items in sorted(self.error_categories.items(), key=lambda x: -len(x[1])):
            pct = len(items) / total_failures * 100
            print(f"\n{category.replace('_', ' ').title()}: {len(items)} ({pct:.1f}%)")
            
            # Show example
            if items:
                example = items[0]
                print(f"  Example scenario: {example['scenario'][:70]}...")
                if 'error' in example:
                    print(f"  Error: {example['error'][:100]}")
        
        return dict(self.error_categories)
    
    def _categorize_failure(self, failure: Dict):
        """Categorize a single failure."""
        
        # JSON extraction failure
        if not failure.get('generated_intent'):
            self.error_categories['json_extraction_failure'].append(failure)
            return
        
        validation = failure.get('validation', {})
        errors = validation.get('errors', [])
        
        # Categorize based on validation errors
        for error in errors:
            error_lower = error.lower()
            
            if 'not in gst' in error_lower or 'unknown characteristic' in error_lower:
                self.error_categories['wrong_characteristic_name'].append(failure)
            elif 'value' in error_lower and 'missing' in error_lower:
                self.error_categories['missing_value'].append(failure)
            elif 'unit' in error_lower:
                self.error_categories['wrong_unit'].append(failure)
            elif 'type' in error_lower:
                self.error_categories['wrong_value_type'].append(failure)
            elif 'required' in error_lower:
                self.error_categories['missing_required_field'].append(failure)
            else:
                self.error_categories['other_schema_violation'].append(failure)
    
    def analyze_scenario_difficulty(self, results: List[Dict]) -> pd.DataFrame:
        """
        Correlate errors with scenario characteristics.
        
        Args:
            results: List of experiment results
            
        Returns:
            DataFrame with difficulty analysis
        """
        print("\n" + "="*80)
        print("SCENARIO DIFFICULTY ANALYSIS")
        print("="*80)
        
        data = []
        for result in results:
            scenario = result['scenario']
            success = result.get('validation', {}).get('overall_valid', False)
            
            # Extract features
            features = {
                'scenario': scenario[:50] + "..." if len(scenario) > 50 else scenario,
                'length': len(scenario),
                'word_count': len(scenario.split()),
                'num_commas': scenario.count(','),
                'has_latency': 'latency' in scenario.lower() or 'delay' in scenario.lower(),
                'has_bandwidth': 'mbps' in scenario.lower() or 'gbps' in scenario.lower() or 'bandwidth' in scenario.lower(),
                'has_reliability': 'reliability' in scenario.lower() or 'uptime' in scenario.lower() or '%' in scenario,
                'has_coverage': 'coverage' in scenario.lower() or 'area' in scenario.lower(),
                'success': success
            }
            
            data.append(features)
        
        df = pd.DataFrame(data)
        
        # Analysis: Success rate by length bins
        print("\nSuccess Rate by Scenario Length:")
        length_bins = pd.cut(df['length'], bins=5)
        length_analysis = df.groupby(length_bins)['success'].agg(['mean', 'count'])
        length_analysis['mean'] = length_analysis['mean'] * 100
        print(length_analysis.to_string())
        
        # Analysis: Success rate by word count
        print("\nSuccess Rate by Word Count:")
        word_bins = pd.cut(df['word_count'], bins=4)
        word_analysis = df.groupby(word_bins)['success'].agg(['mean', 'count'])
        word_analysis['mean'] = word_analysis['mean'] * 100
        print(word_analysis.to_string())
        
        # Analysis: Success rate by requirement type
        print("\nSuccess Rate by Requirement Type:")
        for req_type in ['has_latency', 'has_bandwidth', 'has_reliability', 'has_coverage']:
            if req_type in df.columns:
                type_analysis = df.groupby(req_type)['success'].agg(['mean', 'count'])
                type_analysis['mean'] = type_analysis['mean'] * 100
                print(f"\n{req_type.replace('has_', '').title()}:")
                print(type_analysis.to_string())
        
        return df
    
    def identify_hard_scenarios(self, results: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """
        Identify consistently difficult scenarios.
        
        Args:
            results: Results from multiple runs
            threshold: Success rate threshold for "hard" scenarios
            
        Returns:
            List of hard scenarios
        """
        # Group by scenario
        scenario_results = defaultdict(list)
        
        for result in results:
            scenario = result['scenario']
            success = result.get('validation', {}).get('overall_valid', False)
            scenario_results[scenario].append(success)
        
        # Find hard scenarios
        hard_scenarios = []
        
        for scenario, successes in scenario_results.items():
            success_rate = sum(successes) / len(successes)
            
            if success_rate < threshold:
                hard_scenarios.append({
                    'scenario': scenario,
                    'success_rate': success_rate,
                    'num_attempts': len(successes)
                })
        
        # Sort by success rate
        hard_scenarios.sort(key=lambda x: x['success_rate'])
        
        print("\n" + "="*80)
        print(f"HARD SCENARIOS (Success Rate < {threshold*100:.0f}%)")
        print("="*80)
        
        print(f"\nFound {len(hard_scenarios)} hard scenarios")
        
        if hard_scenarios:
            print("\nTop 5 Hardest:")
            for i, hs in enumerate(hard_scenarios[:5], 1):
                print(f"\n{i}. Success Rate: {hs['success_rate']*100:.0f}%")
                print(f"   Scenario: {hs['scenario'][:80]}...")
        
        return hard_scenarios
    
    def save_analysis(self, results: List[Dict], output_dir: str = "results/error_analysis"):
        """Save comprehensive error analysis."""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Error categories
        error_cats = self.analyze_failures(results)
        
        with open(output_path / "error_categories.json", 'w') as f:
            json.dump({k: len(v) for k, v in error_cats.items()}, f, indent=2)
        
        # Difficulty analysis
        df = self.analyze_scenario_difficulty(results)
        df.to_csv(output_path / "scenario_analysis.csv", index=False)
        
        # Hard scenarios
        hard = self.identify_hard_scenarios(results)
        
        with open(output_path / "hard_scenarios.json", 'w') as f:
            json.dump(hard, f, indent=2)
        
        print(f"\n[OK] Error analysis saved to: {output_path}/")


if __name__ == "__main__":
    # Example: Load and analyze results
    import json
    
    # Load results from a previous experiment
    try:
        with open("results/rag_cloud_50_scenarios/all_results.json") as f:
            results = json.load(f)
        
        analyzer = ErrorAnalyzer()
        analyzer.save_analysis(results)
    except FileNotFoundError:
        print("No results found. Run an experiment first.")
