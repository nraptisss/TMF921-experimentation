"""
Run final test set evaluation.

⚠️ WARNING: This is a ONE-TIME evaluation on the held-out test set.
This should only be run once for final publication numbers.
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "experiments"))

from tmf921.core import ScenarioDataset
from rag_cloud import RAGCloudExperiment

def main():
    print("\n" + "="*80)
    print("⚠️  FINAL TEST SET EVALUATION - ONE-TIME USE ONLY")
    print("="*80)
    print("\nThis evaluation uses the held-out test set (87 scenarios)")
    print("that has NEVER been used during development or validation.")
    print("\nModel: llama3:8b (local)")
    print("Approach: RAG + Name Correction")
    print("\n" + "="*80 + "\n")
    
    # Create experiment with test set name
    experiment = RAGCloudExperiment(
        model_name="llama3:8b",
        num_scenarios=87
    )
    
    # Override experiment name for test set
    experiment.experiment_name = "final_test_set_87_scenarios"
    
    # Setup
    experiment.setup()
    
    # Load test set scenarios (override validation scenarios)
    test_dataset = ScenarioDataset("data/test.json")
    experiment.scenarios = test_dataset.scenarios  # All 87 test scenarios
    
    print(f"\n✓ Loaded {len(experiment.scenarios)} test scenarios")
    print("\nStarting evaluation...")
    print("This will take approximately 3-4 minutes...\n")
    
    # Run without calling setup again
    print(f"\n[4/4] Running {experiment.experiment_name} on {len(experiment.scenarios)} scenarios...")
    print("=" * 80)
    
    for i, scenario in enumerate(experiment.scenarios, 1):
        result = experiment.process_scenario(scenario, i)
        experiment.results.append(result)
        
        # Save checkpoint every 10 scenarios
        if i % 10 == 0:
            experiment.save_checkpoint(i)
    
    # Compute and save final metrics
    experiment.compute_and_save_metrics()
    
    print(f"\n[SUCCESS] Experiment complete!")
    print("=" * 80 + "\n")
    
    print("\n" + "="*80)
    print("✓ FINAL TEST SET EVALUATION COMPLETE")
    print("="*80)
    print(f"\nResults saved to: {experiment.results_dir}/")
    print("\n⚠️  Remember: This test set should NOT be used again.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
