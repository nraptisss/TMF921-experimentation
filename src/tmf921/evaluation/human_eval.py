"""
Human evaluation protocol for semantic correctness validation.

Schema-valid ≠ semantically correct. This module provides tools
for human evaluation to validate semantic accuracy.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
from sklearn.metrics import cohen_kappa_score


class HumanEvaluationSuite:
    """
    Human evaluation protocol for semantic correctness.
    
    Workflow:
    1. prepare_eval_set() - Sample results stratified
    2. Export to CSV for human annotation
    3. load_annotations() - Load completed annotations
    4. compute_agreement() - Inter-annotator reliability
    5. compare_automated_vs_human() - Automated validation accuracy
    """
    
    def __init__(self, sample_size: int = 100):
        """
        Initialize human evaluation suite.
        
        Args:
            sample_size: Number of scenarios to evaluate (default 100)
        """
        self.sample_size = sample_size
        self.annotations = []
    
    def prepare_eval_set(
        self,
        results: List[Dict],
        output_file: str = "human_evaluation_template.csv"
    ) -> pd.DataFrame:
        """
        Prepare evaluation set with stratified sampling.
        
        Args:
            results: Experiment results
            output_file: CSV file to save template
            
        Returns:
            DataFrame with evaluation template
        """
        import random
        random.seed(42)
        
        # Stratified sampling: include successes and failures
        successes = [r for r in results if r.get('validation', {}).get('overall_valid', False)]
        failures = [r for r in results if not r.get('validation', {}).get('overall_valid', False)]
        
        # Sample 80 successes, 20 failures (or proportional if fewer available)
        n_success = min(int(self.sample_size * 0.8), len(successes))
        n_failure = min(self.sample_size - n_success, len(failures))
        
        sample = (
            random.sample(successes, n_success) +
            random.sample(failures, n_failure)
        )
        
        # Create evaluation template
        eval_data = []
        for i, result in enumerate(sample):
            eval_data.append({
                'id': i,
                'scenario': result['scenario'],
                'generated_intent_json': json.dumps(result.get('generated_intent', {}), indent=2),
                'automated_valid': result.get('validation', {}).get('overall_valid', False),
                'automated_errors': '; '.join(result.get('validation', {}).get('errors', [])),
                # Fields for human annotators to fill:
                'human_valid': None,
                'semantic_errors': None,
                'notes': None
            })
        
        # Save to CSV
        df = pd.DataFrame(eval_data)
        df.to_csv(output_file, index=False)
        
        print(f"\n[OK] Created human evaluation template: {output_file}")
        print(f"     Samples: {len(eval_data)} (Success: {n_success}, Failure: {n_failure})")
        print(f"\n     Instructions for annotators:")
        print(f"     1. Review scenario and generated intent")
        print(f"     2. Mark 'human_valid' as True/False")
        print(f"     3. Note any semantic errors in 'semantic_errors'")
        print(f"     4. Add any observations in 'notes'")
        
        return df
    
    def load_annotations(self, annotation_file: str) -> pd.DataFrame:
        """
        Load completed annotations from CSV.
        
        Args:
            annotation_file: Path to completed CSV
            
        Returns:
            DataFrame with annotations
        """
        df = pd.read_csv(annotation_file)
        
        # Validate required columns
        required = ['id', 'scenario', 'automated_valid', 'human_valid']
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Convert human_valid to boolean
        df['human_valid'] = df['human_valid'].astype(bool)
        
        print(f"\n[OK] Loaded {len(df)} annotations from {annotation_file}")
        
        return df
    
    def compute_inter_annotator_agreement(
        self,
        annotations_a: List[bool],
        annotations_b: List[bool]
    ) -> Dict:
        """
        Compute Cohen's Kappa for inter-annotator agreement.
        
        Args:
            annotations_a: Annotator A's judgments
            annotations_b: Annotator B's judgments
            
        Returns:
            Dictionary with kappa score and interpretation
        """
        kappa = cohen_kappa_score(annotations_a, annotations_b)
        
        # Interpretation per Landis & Koch
        if kappa < 0:
            interpretation = "Poor (Less than chance)"
        elif kappa < 0.20:
            interpretation = "Slight"
        elif kappa < 0.40:
            interpretation = "Fair"
        elif kappa < 0.60:
            interpretation = "Moderate"
        elif kappa < 0.80:
            interpretation = "Substantial"
        else:
            interpretation = "Almost Perfect"
        
        print(f"\n" + "="*80)
        print("INTER-ANNOTATOR AGREEMENT")
        print("="*80)
        print(f"\nCohen's Kappa: {kappa:.3f}")
        print(f"Interpretation: {interpretation}")
        print(f"Sample size: {len(annotations_a)}")
        
        return {
            'kappa': kappa,
            'interpretation': interpretation,
            'n': len(annotations_a)
        }
    
    def compare_automated_vs_human(
        self,
        df: pd.DataFrame
    ) -> Dict:
        """
        Compare automated validation vs human judgment.
        
        Args:
            df: DataFrame with both automated_valid and human_valid columns
            
        Returns:
            Dictionary with comparison metrics
        """
        automated = df['automated_valid'].astype(bool).tolist()
        human = df['human_valid'].astype(bool).tolist()
        
        # Agreement metrics
        agreement = sum(1 for i in range(len(human)) if human[i] == automated[i])
        agreement_rate = agreement / len(human)
        
        # Confusion matrix
        true_positive = sum(1 for i in range(len(human)) if automated[i] and human[i])
        false_positive = sum(1 for i in range(len(human)) if automated[i] and not human[i])
        false_negative = sum(1 for i in range(len(human)) if not automated[i] and human[i])
        true_negative = sum(1 for i in range(len(human)) if not automated[i] and not human[i])
        
        # Metrics
        precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
        recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Cohen's Kappa
        kappa = cohen_kappa_score(human, automated)
        
        print("\n" + "="*80)
        print("AUTOMATED vs HUMAN VALIDATION")
        print("="*80)
        
        print(f"\nAgreement Rate: {agreement_rate*100:.1f}%")
        print(f"Cohen's Kappa: {kappa:.3f}")
        
        print(f"\nConfusion Matrix:")
        print(f"  True Positives:  {true_positive} (Automated=Valid, Human=Valid)")
        print(f"  False Positives: {false_positive} (Automated=Valid, Human=Invalid)")  
        print(f"  False Negatives: {false_negative} (Automated=Invalid, Human=Valid)")
        print(f"  True Negatives:  {true_negative} (Automated=Invalid, Human=Invalid)")
        
        print(f"\nAutomated Validation Performance:")
        print(f"  Precision: {precision*100:.1f}% (When automated says valid, how often is it really valid?)")
        print(f"  Recall: {recall*100:.1f}% (Of truly valid intents, how many did automated catch?)")
        print(f"  F1 Score: {f1*100:.1f}%")
        
        if false_positive > 0:
            print(f"\n[WARNING] {false_positive} false positives - automated marked valid but human says invalid")
        
        if false_negative > 0:
            print(f"\n[WARNING] {false_negative} false negatives - automated marked invalid but human says valid")
        
        return {
            'agreement_rate': agreement_rate,
            'kappa': kappa,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': {
                'true_positive': true_positive,
                'false_positive': false_positive,
                'false_negative': false_negative,
                'true_negative': true_negative
            }
        }
    
    def save_human_eval_results(
        self,
        df: pd.DataFrame,
        output_dir: str = "results/human_evaluation"
    ):
        """Save human evaluation results and analysis."""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save annotated data
        df.to_csv(output_path / "human_annotations.csv", index=False)
        
        # Comparison analysis
        comparison = self.compare_automated_vs_human(df)
        
        with open(output_path / "automated_vs_human.json", 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"\n[OK] Human evaluation results saved to: {output_path}/")


# Example usage
if __name__ == "__main__":
    # Step 1: Prepare evaluation set
    import json
    
    # Load experiment results
    with open("results/rag_cloud_50_scenarios/all_results.json") as f:
        results = json.load(f)
    
    suite = HumanEvaluationSuite(sample_size=100)
    
    # Create template for annotators
    suite.prepare_eval_set(results, output_file="human_evaluation_template.csv")
    
    print("\n[NEXT STEP] Send human_evaluation_template.csv to 3 annotators")
    print("            After completion, use load_annotations() to analyze")
