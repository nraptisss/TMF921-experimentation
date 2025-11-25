"""Comprehensive analysis of 50-scenario validation results."""
import json
from pathlib import Path

# Load all result sets
with open('results/quick_validation/metrics_summary.json') as f:
    zero_shot_10 = json.load(f)

with open('results/few_shot_validation/metrics_summary.json') as f:
    few_shot_10 = json.load(f)

with open('results/validation_50/metrics_summary.json') as f:
    validation_50 = json.load(f)

print("\n" + "="*80)
print("COMPREHENSIVE RESULTS ANALYSIS")
print("="*80 + "\n")

# Summary table
print("Experiment Comparison:")
print("-" * 80)
print(f"{'Experiment':<30} {'Scenarios':<12} {'Format':<10} {'Accuracy':<12} {'Time/Scenario':<15}")
print("-" * 80)

experiments = [
    ("Zero-Shot (10)", zero_shot_10),
    ("Few-Shot (10)", few_shot_10),
    ("Few-Shot (50)", validation_50)
]

for name, data in experiments:
    scenarios = data['num_scenarios']
    format_pct = data['feaci']['format_correctness']
    accuracy = data['feaci']['accuracy']
    time = data['feaci']['inference_time_avg_seconds']
    print(f"{name:<30} {scenarios:<12} {format_pct:>6.1f}%   {accuracy:>6.1f}%      {time:>6.1f}s")

print("-" * 80)

# Key findings
print("\n" + "="*80)
print("KEY FINDINGS")
print("="*80)

acc_50 = validation_50['feaci']['accuracy']
acc_10 = few_shot_10['feaci']['accuracy']
diff = acc_50 - acc_10

print(f"\n1. ACCURACY VALIDATION:")
print(f"   10-scenario test: {acc_10:.1f}%")
print(f"   50-scenario validation: {acc_50:.1f}%")
print(f"   Difference: {diff:+.1f} percentage points")

if abs(diff) < 5:
    print(f"   Status: ✅ Consistent performance across dataset sizes")
elif diff > 0:
    print(f"   Status: ✅ Better performance on larger dataset")
else:
    print(f"   Status: ⚠️  Performance decreased on larger dataset")

print(f"\n2. HYPOTHESIS H1 VALIDATION:")
print(f"   Target: >70% format correctness, >70% accuracy")
print(f"   Format: {validation_50['feaci']['format_correctness']:.1f}% {'✅' if validation_50['feaci']['format_correctness'] >= 70 else '❌'}")
print(f"   Accuracy: {acc_50:.1f}% {'✅' if acc_50 >= 70 else '❌'}")

print(f"\n3. IMPROVEMENTS ACHIEVED:")
improvement = acc_50 - zero_shot_10['feaci']['accuracy']
print(f"   Zero-shot baseline: {zero_shot_10['feaci']['accuracy']:.1f}%")
print(f"   Final accuracy: {acc_50:.1f}%")
print(f"   Total improvement: +{improvement:.1f} percentage points")

print(f"\n4. EFFICIENCY METRICS:")
total_time = validation_50['feaci']['inference_time_total_seconds']
total_tokens = validation_50['feaci']['cost_total_tokens']
print(f"   Total processing time: {total_time/60:.1f} minutes")
print(f"   Total tokens: {total_tokens:,}")
print(f"   Auto-corrections: {validation_50['num_corrections']}")

# Load full results for error analysis
with open('results/validation_50/all_results.json') as f:
    all_results = json.load(f)

valid_results = [r for r in all_results if r.get('validation')]
failed = [r for r in valid_results if not r['validation']['overall_valid']]

print(f"\n5. ERROR ANALYSIS:")
print(f"   Total processed: {len(valid_results)}")
print(f"   Successful: {len(valid_results) - len(failed)}")
print(f"   Failed: {len(failed)}")

if failed:
    # Collect all errors
    all_errors = []
    for r in failed:
        all_errors.extend(r['validation'].get('errors', []))
    
    from collections import Counter
    error_counts = Counter(all_errors)
    
    print(f"\n   Top errors:")
    for error, count in error_counts.most_common(5):
        print(f"     [{count:2}x] {error[:70]}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

if acc_50 >= 70:
    print("\n✅ RESEARCH MILESTONE ACHIEVED")
    print(f"   - {acc_50:.0f}% accuracy exceeds 70% target")
    print(f"   - Validated on 50 diverse scenarios")
    print(f"   - Ready for Phase 4: model comparison")
else:
    print(f"\n⚠️  Below 70% target: {acc_50:.1f}%")
    print(f"   - Consider RAG enhancement")
    print(f"   - Explore Chain-of-Thought reasoning")

print("\n" + "="*80 + "\n")
