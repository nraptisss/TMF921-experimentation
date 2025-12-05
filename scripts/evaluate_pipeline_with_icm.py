"""
Comprehensive Pipeline Evaluation with ICM Export

Runs full evaluation on validation set with ICM export enabled.
Measures:
- Intent generation accuracy
- ICM conversion success
- Performance metrics
- Format validation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "experiments"))

from rag_cloud import RAGCloudExperiment


def main():
    """Run comprehensive evaluation."""
    print("=" * 80)
    print("COMPREHENSIVE PIPELINE EVALUATION")
    print("ICM Export: ENABLED")
    print("=" * 80)
    print()
    
    # Create experiment with ICM export enabled
    exp = RAGCloudExperiment(
        model_name="llama3:8b",
        num_scenarios=86,  # Full validation set
        export_icm=True    # Enable ICM export
    )
    
    print("Configuration:")
    print(f"  Model: {exp.model_name}")
    print(f"  Scenarios: {exp.num_scenarios}")
    print(f"  ICM Export: {exp.export_icm}")
    print(f"  Results Dir: {exp.results_dir}")
    print()
    
    # Run experiment
    exp.setup()
    exp.run()
    
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    print()
    print("Check results in:")
    print(f"  - {exp.results_dir}/")
    print()


if __name__ == "__main__":
    main()
