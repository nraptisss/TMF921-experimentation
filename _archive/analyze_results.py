"""Analyze quick validation results."""
import json
from pathlib import Path
from collections import Counter

results_dir = Path("results/quick_validation")
results = [json.load(open(f)) for f in sorted(results_dir.glob("result_*.json"))]

print("\n" + "="*80)
print("QUICK VALIDATION RESULTS ANALYSIS")
print("="*80 + "\n")

# Overall stats
valid = [r for r in results if r.get('validation')]
print(f"Total scenarios: {len(results)}")
print(f"Successful generations: {len(valid)}")

if valid:
    format_valid = sum(1 for r in valid if r['validation']['format_valid'])
    char_valid = sum(1 for r in valid if r['validation']['characteristics_valid'])
    overall_valid = sum(1 for r in valid if r['validation']['overall_valid'])
    
    print(f"\nFEACI Metrics:")
    print(f"  Format Correctness:  {format_valid}/{len(valid)} ({format_valid/len(valid)*100:.1f}%)")
    print(f"  Characteristics Valid: {char_valid}/{len(valid)} ({char_valid/len(valid)*100:.1f}%)")
    print(f"  Overall Valid:       {overall_valid}/{len(valid)} ({overall_valid/len(valid)*100:.1f}%)")
    
    avg_time = sum(r['metrics']['time_seconds'] for r in valid) / len(valid)
    avg_tokens = sum(r['metrics']['tokens'] for r in valid) / len(valid)
    
    print(f"\n  Avg Inference Time:  {avg_time:.1f}s")
    print(f"  Avg Tokens:          {avg_tokens:.0f}")
    
    # Error analysis
    print(f"\n" + "-"*80)
    print("ERROR ANALYSIS")
    print("-"*80)
    
    all_errors = []
    for r in valid:
        all_errors.extend(r['validation'].get('errors', []))
    
    if all_errors:
        error_counts = Counter(all_errors)
        print(f"\nMost common errors:")
        for error, count in error_counts.most_common(5):
            print(f"  [{count}x] {error}")
    
    # Success examples
    print(f"\n" + "-"*80)
    print("SUCCESSFUL TRANSLATIONS")
    print("-"*80)
    
    successes = [r for r in valid if r['validation']['overall_valid']]
    print(f"\n{len(successes)} fully valid translations:")
    for i, r in enumerate(successes[:3], 1):
        scenario = r['scenario'][:60]
        print(f"\n{i}. {scenario}...")
        intent = r['generated_intent']
        print(f"  Name: {intent['name']}")
        print(f"  Characteristics: {len(intent['serviceSpecCharacteristic'])}")
        for char in intent['serviceSpecCharacteristic'][:2]:
            print(f"    - {char['name']}: {char['value']['value']} {char['value'].get('unitOfMeasure', '')}")
    
    # Failure examples
    failures = [r for r in valid if not r['validation']['overall_valid']]
    if failures:
        print(f"\n" + "-"*80)
        print("FAILED TRANSLATIONS")
        print("-"*80)
        print(f"\n{len(failures)} translations with errors:")
        for i, r in enumerate(failures[:2], 1):
            scenario = r['scenario'][:60]
            print(f"\n{i}. {scenario}...")
            print(f"  Errors: {r['validation']['errors']}")

print("\n" + "="*80 + "\n")
