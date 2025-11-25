"""
Analyze and compare experiment results.

Usage:
    python analyze_results.py --experiment rag_cloud_50_scenarios
    python analyze_results.py --compare few_shot_10 rag_cloud_50
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any


def load_metrics(experiment_name: str) -> Dict[str, Any]:
    """Load metrics from experiment results."""
    metrics_file = Path("results") / experiment_name / "metrics_summary.json"
    
    if not metrics_file.exists():
        raise FileNotFoundError(f"Metrics not found: {metrics_file}")
    
    with open(metrics_file) as f:
        return json.load(f)


def print_experiment_results(experiment_name: str):
    """Print detailed results for single experiment."""
    metrics = load_metrics(experiment_name)
    
    print("\n" + "="*80)
    print(f"Experiment: {experiment_name}")
    print("="*80)
    
    print(f"\nModel: {metrics['model']}")
    print(f"Scenarios: {metrics['num_scenarios']}")
    print(f"Successful: {metrics['num_successful']}")
    print(f"Corrections: {metrics['num_corrections']}")
    
    feaci = metrics['feaci']
    print(f"\nFEACI Metrics:")
    print(f"  Format Correctness: {feaci['format_correctness']:.1f}%")
    print(f"  Accuracy:           {feaci['accuracy']:.1f}%")
    print(f"  Avg Tokens:         {feaci['cost_avg_tokens']:.0f}")
    print(f"  Total Tokens:       {feaci.get('cost_total_tokens', 0):,}")
    print(f"  Avg Time:           {feaci['inference_time_avg_seconds']:.1f}s")
    print(f"  Total Time:         {feaci.get('inference_time_total_seconds', 0)/60:.1f} min")
    
    print("\n" + "="*80 + "\n")


def compare_experiments(experiment_names: List[str]):
    """Compare multiple experiments."""
    experiments = []
    for name in experiment_names:
        try:
            metrics = load_metrics(name)
            experiments.append((name, metrics))
        except FileNotFoundError as e:
            print(f"Warning: {e}")
    
    if not experiments:
        print("No experiments to compare")
        return
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPARISON")
    print("="*80 + "\n")
    
    # Print comparison table
    print(f"{'Experiment':<30} {'Model':<20} {'Accuracy':<12} {'Time/Scenario':<15}")
    print("-" * 80)
    
    for name, metrics in experiments:
        feaci = metrics['feaci']
        model = metrics['model']
        accuracy = feaci['accuracy']
        avg_time = feaci['inference_time_avg_seconds']
        
        print(f"{name:<30} {model:<20} {accuracy:>6.1f}%      {avg_time:>6.1f}s")
    
    print("\n" + "="*80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze experiment results")
    
    parser.add_argument(
        "--experiment", "-e",
        help="Single experiment to analyze"
    )
    
    parser.add_argument(
        "--compare", "-c",
        nargs="+",
        help="Multiple experiments to compare"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available results"
    )
    
    args = parser.parse_args()
    
    # List results
    if args.list:
        results_dir = Path("results")
        if results_dir.exists():
            experiments = [d.name for d in results_dir.iterdir() if d.is_dir()]
            print("\nAvailable results:")
            for exp in sorted(experiments):
                print(f"  - {exp}")
            print()
        return
    
    # Analyze single experiment
    if args.experiment:
        print_experiment_results(args.experiment)
        return
    
    # Compare experiments
    if args.compare:
        compare_experiments(args.compare)
        return
    
    # Default: show usage
    parser.print_help()


if __name__ == "__main__":
    main()
