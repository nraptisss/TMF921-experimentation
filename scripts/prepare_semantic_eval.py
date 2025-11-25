"""
Run semantic evaluation using human evaluation framework.

This will prepare a sample of results for human review to validate
that intents are not just schema-valid but also semantically correct.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
from tmf921.evaluation.human_eval import HumanEvaluationSuite

print("="*80)
print("SEMANTIC EVALUATION SETUP")
print("="*80)

# Load results from validation experiment
results_file = Path("results/rag_cloud_86_scenarios/all_results.json")

if not results_file.exists():
    print(f"\n[ERROR] Results file not found: {results_file}")
    print("Run validation experiment first!")
    sys.exit(1)

with open(results_file) as f:
    results = json.load(f)

print(f"\n[OK] Loaded {len(results)} results from validation experiment")

# Create human evaluation suite
suite = HumanEvaluationSuite(sample_size=50)  # Sample 50 for review

# Prepare evaluation template
print("\nPreparing evaluation template...")
df = suite.prepare_eval_set(results, output_file="human_evaluation_template.csv")

print("\n" + "="*80)
print("NEXT STEPS FOR SEMANTIC EVALUATION")
print("="*80)

print("""
1. REVIEW THE TEMPLATE
   - Open: human_evaluation_template.csv
   - 50 samples stratified (40 successes, 10 failures)

2. HUMAN ANNOTATION
   For each row, evaluate:
   - Does the generated intent match the original scenario?
   - Are the values semantically correct?
   - Are the characteristics appropriate?
   
   Fill in these columns:
   - human_valid: True/False (is it semantically correct?)
   - semantic_errors: Describe any issues
   - notes: Additional observations

3. ANALYSIS
   After annotation, run:
   python scripts/analyze_human_eval.py

This will compute:
   - Agreement rate (automated vs human)
   - Precision/Recall of automated validation
   - Inter-annotator reliability (if multiple annotators)
   - False positive/negative analysis

IMPORTANT:
   Schema-valid ≠ Semantically correct!
   This evaluation validates MEANING, not just FORMAT.
""")

print("\n[OK] Template ready: human_evaluation_template.csv")
print("\n" + "="*80)
