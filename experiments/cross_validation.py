"""
Cross-validation experiment for rigorous evaluation.

Implements k-fold cross-validation to assess model performance variance.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from sklearn.model_selection import KFold
import json
from datetime import datetime

from tmf921.core import ScenarioDataset
from tmf921.utils import compute_feaci_metrics


class CrossValidationExperiment:
    """
    K-fold cross-validation for rigorous evaluation.
    
    Usage:
        cv = CrossValidationExperiment(
            experiment_class=RAGCloudExperiment,
            model_name="gpt-oss:20b-cloud",
            n_folds=5,
            scenarios_per_fold=20
        )
        cv.run()
    """
    
    def __init__(
        self,
        experiment_class,
        model_name: str,
        n_folds: int = 5,
        scenarios_per_fold: int = None,
        **experiment_kwargs
    ):
        """
        Initialize cross-validation experiment.
        
        Args:
            experiment_class: BaseExperiment subclass (FewShotExperiment, RAGCloudExperiment)
            model_name: Name of model to use
            n_folds: Number of folds (default 5)
            scenarios_per_fold: Limit scenarios per fold (None = use all)
            **experiment_kwargs: Additional kwargs for experiment
        """
        self.experiment_class = experiment_class
        self.model_name = model_name
        self.n_folds = n_folds
        self.scenarios_per_fold = scenarios_per_fold
        self.experiment_kwargs = experiment_kwargs
        self.fold_results = []
        
    def run(self):
        """Run k-fold cross-validation."""
        
        # Load validation scenarios
        dataset = ScenarioDataset("data/val.json")
        scenarios = dataset.scenarios
        
        print("\n" + "="*80)
        print(f"{self.n_folds}-FOLD CROSS-VALIDATION")
        print("="*80)
        print(f"\nTotal scenarios: {len(scenarios)}")
        print(f"Scenarios per fold: ~{len(scenarios)//self.n_folds}")
        print(f"Model: {self.model_name}")
        print("")
        
        # K-fold split
        kf = KFold(n_splits=self.n_folds, shuffle=True, random_state=42)
        
        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(scenarios), 1):
            print(f"\n{'='*80}")
            print(f"FOLD {fold_idx}/{self.n_folds}")
            print(f"{'='*80}")
            
            # Get fold scenarios
            fold_scenarios = [scenarios[i] for i in val_idx]
            
            # Limit if specified
            if self.scenarios_per_fold:
                fold_scenarios = fold_scenarios[:self.scenarios_per_fold]
            
            print(f"Evaluating on {len(fold_scenarios)} scenarios...")
            
            # Create and run experiment for this fold
            exp = self.experiment_class(
                model_name=self.model_name,
                num_scenarios=len(fold_scenarios),
                **self.experiment_kwargs
            )
            
            exp.setup()
            exp.scenarios = fold_scenarios
            exp.experiment_name = f"{exp.experiment_name}_fold{fold_idx}"
            exp.run()
            
            # Store fold results
            fold_metrics = compute_feaci_metrics(exp.results)
            
            self.fold_results.append({
                'fold': fold_idx,
                'num_scenarios': len(fold_scenarios),
                'results': exp.results,
                'metrics': fold_metrics
            })
            
            print(f"\nFold {fold_idx} Accuracy: {fold_metrics['accuracy']:.1f}%")
        
        # Aggregate and report
        self.aggregate_and_report()
    
    def aggregate_and_report(self):
        """Compute statistics across folds and save results."""
        
        # Extract metrics
        accuracies = [fold['metrics']['accuracy'] for fold in self.fold_results]
        times = [fold['metrics']['inference_time_avg_seconds'] for fold in self.fold_results]
        
        # Compute statistics
        mean_acc = np.mean(accuracies)
        std_acc = np.std(accuracies, ddof=1)  # Sample std
        
        mean_time = np.mean(times)
        std_time = np.std(times, ddof=1)
        
        # Print results
        print("\n" + "="*80)
        print("CROSS-VALIDATION RESULTS")
        print("="*80)
        
        print(f"\nAccuracy: {mean_acc:.1f}% ± {std_acc:.1f}%")
        print(f"Inference Time: {mean_time:.1f}s ± {std_time:.1f}s")
        
        print(f"\nPer-fold accuracies:")
        for fold in self.fold_results:
            acc = fold['metrics']['accuracy']
            print(f"  Fold {fold['fold']}: {acc:.1f}%")
        
        # Coefficient of variation
        cv = (std_acc / mean_acc) * 100 if mean_acc > 0 else 0
        print(f"\nCoefficient of Variation: {cv:.1f}%")
        
        if cv < 5:
            print("  [EXCELLENT] Very consistent performance")
        elif cv < 10:
            print("  [GOOD] Reasonably consistent")
        else:
            print("  [WARNING] High variance across folds")
        
        # Save summary
        summary = {
            'n_folds': self.n_folds,
            'model': self.model_name,
            'mean_accuracy': float(mean_acc),
            'std_accuracy': float(std_acc),
            'mean_time': float(mean_time),
            'std_time': float(std_time),
            'fold_accuracies': accuracies,
            'fold_times': times,
            'coefficient_of_variation': float(cv),
            'timestamp': datetime.now().isoformat()
        }
        
        output_dir = Path("results") / "cross_validation"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "cv_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n[OK] Results saved to: {output_dir}/")
        print("\n" + "="*80 + "\n")
        
        return summary


if __name__ == "__main__":
    # Example usage
    from rag_cloud import RAGCloudExperiment
    
    cv = CrossValidationExperiment(
        experiment_class=RAGCloudExperiment,
        model_name="llama3:8b",  # Use local model instead of cloud
        n_folds=5,
        scenarios_per_fold=10  # 10 scenarios per fold for quick test
    )
    
    cv.run()
