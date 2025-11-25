"""Compare zero-shot vs few-shot results."""
import json

# Load results
with open('results/quick_validation/metrics_summary.json') as f:
    zero_shot = json.load(f)

with open('results/few_shot_validation/metrics_summary.json') as f:
    few_shot = json.load(f)

print("\n" + "="*80)
print("ZERO-SHOT VS FEW-SHOT COMPARISON")
print("="*80 + "\n")

print("FEACI Metrics:")
print("-" * 80)
print(f"{'Metric':<30} {'Zero-Shot':<15} {'Few-Shot':<15} {'Delta':<15}")
print("-" * 80)

format_zs = zero_shot['feaci']['format_correctness']
format_fs = few_shot['feaci']['format_correctness']
print(f"{'Format Correctness':<30} {format_zs:>6.1f}%{'':<8} {format_fs:>6.1f}%{'':<8} {format_fs-format_zs:>+6.1f}pp")

acc_zs = zero_shot['feaci']['accuracy']
acc_fs = few_shot['feaci']['accuracy']
print(f"{'Overall Accuracy':<30} {acc_zs:>6.1f}%{'':<8} {acc_fs:>6.1f}%{'':<8} {acc_fs-acc_zs:>+6.1f}pp")

tokens_zs = zero_shot['feaci']['cost_avg_tokens']
tokens_fs = few_shot['feaci']['cost_avg_tokens']
print(f"{'Avg Tokens':<30} {tokens_zs:>7.0f}{'':<8} {tokens_fs:>7.0f}{'':<8} {tokens_fs-tokens_zs:>+7.0f}")

time_zs = zero_shot['feaci']['inference_time_avg_seconds']
time_fs = few_shot['feaci']['inference_time_avg_seconds']
speedup = time_zs / time_fs
print(f"{'Avg Inference Time':<30} {time_zs:>6.1f}s{'':<8} {time_fs:>6.1f}s{'':<8} {speedup:>6.2f}x faster")

print("-" * 80)
print(f"\nName Corrections: {few_shot['num_corrections']} automatic fixes applied")

print("\n" + "="*80)
print("KEY IMPROVEMENTS")
print("="*80)
print(f"\n✅ Accuracy: {acc_zs:.0f}% → {acc_fs:.0f}% (+{acc_fs-acc_zs:.0f} percentage points)")
print(f"✅ Speed: {time_zs:.1f}s → {time_fs:.1f}s ({speedup:.1f}x faster inference)")
print(f"✅ Auto-corrections: {few_shot['num_corrections']} characteristic names fixed")

if acc_fs >= 70:
    print(f"\n🎯 TARGET ACHIEVED: {acc_fs:.0f}% accuracy exceeds 70% target (H1)")
else:
    print(f"\n⚠️  Below 70% target: {acc_fs:.0f}% vs 70% goal")

print("\n" + "="*80 + "\n")
