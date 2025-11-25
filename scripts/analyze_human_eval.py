"""
Analyze human evaluation results to assess semantic correctness.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tmf921.evaluation.human_eval import HumanEvaluationSuite
import pandas as pd

# Load annotated results
annotation_file = "human_evaluation_completed.csv"

if not Path(annotation_file).exists():
    print(f"[ERROR] Annotation file not found: {annotation_file}")
    print("\nPlease complete the human evaluation first:")
    print("1. Open human_evaluation_template.csv")
    print("2. Fill in human_valid, semantic_errors, notes columns")
    print("3. Save as human_evaluation_completed.csv")
    sys.exit(1)

suite = HumanEvaluationSuite()

# Load annotations
df = suite.load_annotations(annotation_file)

# Compare automated vs human
print("\n" + "="*80)
print("SEMANTIC CORRECTNESS ANALYSIS")
print("="*80)

comparison = suite.compare_automated_vs_human(df)

# Save results
suite.save_human_eval_results(df, output_dir="results/human_evaluation")

print("\n[OK] Analysis complete! Check results/human_evaluation/")
