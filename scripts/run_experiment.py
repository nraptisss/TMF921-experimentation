"""
Unified experiment runner - single entry point for all experiments.

Usage:
    python scripts/run_experiment.py --experiment few_shot --scenarios 10 --model llama3:latest
    python scripts/run_experiment.py --experiment rag_cloud --scenarios 50
    python scripts/run_experiment.py --list
"""

import argparse
import sys
from pathlib import Path

# Add parent directories to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / "src"))
sys.path.insert(0, str(parent_dir / "experiments"))

from few_shot import FewShotExperiment
from rag_cloud import RAGCloudExperiment


# Registry of available experiments
EXPERIMENTS = {
    "few_shot": {
        "class": FewShotExperiment,
        "description": "Few-shot learning with example scenarios",
        "default_model": "llama3:latest",
        "default_scenarios": 10,
    },
    "rag_cloud": {
        "class": RAGCloudExperiment,
        "description": "RAG with Ollama Cloud model for speed and accuracy",
        "default_model": "gpt-oss:20b-cloud",
        "default_scenarios": 50,
    },
}


def list_experiments():
    """List all available experiments."""
    print("\nAvailable Experiments:")
    print("=" * 80)
    
    for name, info in EXPERIMENTS.items():
        print(f"\n{name}")
        print(f"  Description: {info['description']}")
        print(f"  Default model: {info['default_model']}")
        print(f"  Default scenarios: {info['default_scenarios']}")
    
    print("\n" + "=" * 80 + "\n")


def run_experiment(experiment_name: str, model: str = None, scenarios: int = None, **kwargs):
    """
    Run specified experiment.
    
    Args:
        experiment_name: Name of experiment to run
        model: Model name (uses default if None)
        scenarios: Number of scenarios (uses default if None)
        **kwargs: Additional experiment-specific arguments
    """
    if experiment_name not in EXPERIMENTS:
        print(f"Error: Unknown experiment '{experiment_name}'")
        print(f"Available: {', '.join(EXPERIMENTS.keys())}")
        return
    
    exp_info = EXPERIMENTS[experiment_name]
    exp_class = exp_info["class"]
    
    # Use defaults if not specified
    model = model or exp_info["default_model"]
    scenarios = scenarios or exp_info["default_scenarios"]
    
    print("\n" + "=" * 80)
    print(f"TMF921 Intent Translation - {experiment_name.replace('_', ' ').title()} Experiment")
    print("=" * 80)
    print(f"\nModel: {model}")
    print(f"Scenarios: {scenarios}")
    print("")
    
    # Create and run experiment
    experiment = exp_class(
        model_name=model,
        num_scenarios=scenarios,
        **kwargs
    )
    
    experiment.setup()
    experiment.run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="TMF921 Intent Translation - Unified Experiment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run few-shot experiment with 10 scenarios
  python run_experiment.py --experiment few_shot --scenarios 10
  
  # Run RAG + Cloud with default settings (50 scenarios)
  python run_experiment.py --experiment rag_cloud
  
  # List all available experiments
  python run_experiment.py --list
        """
    )
    
    parser.add_argument(
        "--experiment", "-e",
        choices=list(EXPERIMENTS.keys()),
        help="Experiment to run"
    )
    
    parser.add_argument(
        "--model", "-m",
        help="Model name (uses experiment default if not specified)"
    )
    
    parser.add_argument(
        "--scenarios", "-n",
        type=int,
        help="Number of scenarios to process (uses experiment default if not specified)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available experiments"
    )
    
    # Few-shot specific
    parser.add_argument(
        "--examples",
        type=int,
        default=3,
        help="Number of few-shot examples (few_shot experiment only)"
    )
    
    args = parser.parse_args()
    
    # List experiments if requested
    if args.list:
        list_experiments()
        return
    
    # Require experiment name if not listing
    if not args.experiment:
        parser.error("--experiment is required (or use --list to see available experiments)")
    
    # Build kwargs for experiment-specific args
    kwargs = {}
    if args.experiment == "few_shot":
        kwargs["num_examples"] = args.examples
    
    # Run experiment
    run_experiment(
        experiment_name=args.experiment,
        model=args.model,
        scenarios=args.scenarios,
        **kwargs
    )


if __name__ == "__main__":
    main()
