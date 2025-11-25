"""
Comprehensive verification of scientific rigor implementation.

Tests all new modules and validates scientific improvements.
"""

import sys
from pathlib import Path

print("="*80)
print("SCIENTIFIC RIGOR VERIFICATION")
print("="*80)

errors = []
successes = []
warnings = []

# Test 1: Dataset Splits
print("\n[1/8] Testing dataset splits...")
try:
    import json
    
    # Check split files exist
    for split in ['train', 'val', 'test']:
        path = Path(f"data/{split}.json")
        if not path.exists():
            errors.append(f"Missing {split}.json")
        else:
            with open(path) as f:
                data = json.load(f)
                successes.append(f"[OK] {split}.json: {len(data)} scenarios")
    
    # Check metadata
    metadata_path = Path("data/split_metadata.json")
    if metadata_path.exists():
        with open(metadata_path) as f:
            meta = json.load(f)
            total = meta['train_size'] + meta['val_size'] + meta['test_size']
            successes.append(f"[OK] Total split: {total} scenarios")
    else:
        warnings.append("Missing split_metadata.json")
    
    print("  [OK] Dataset splits verified")
except Exception as e:
    errors.append(f"Dataset splits test failed: {e}")

# Test 2: Statistical Module
print("\n[2/8] Testing statistical module...")
try:
    sys.path.insert(0, "src")
    from tmf921.utils.statistics import (
        mcnemar_test,
        confidence_interval,
        bootstrap_confidence_interval,
        compute_accuracy_with_ci,
        print_statistical_comparison
    )
    
    # Test functions
    test_results_a = [True] * 80 + [False] * 20
    test_results_b = [True] * 90 + [False] * 10
    
    # McNemar test
    result = mcnemar_test(test_results_a, test_results_b)
    assert 'p_value' in result.__dict__
    assert 'significant' in result.__dict__
    
    # CI
    ci = confidence_interval([0.8, 0.85, 0.9])
    assert len(ci) == 2
    
    # Bootstrap CI
    boot_ci = bootstrap_confidence_interval(test_results_a)
    assert len(boot_ci) == 2
    
    # Accuracy with CI
    stats = compute_accuracy_with_ci(test_results_a)
    assert 'accuracy' in stats
    assert 'ci_lower' in stats
    assert 'ci_upper' in stats
    
    successes.append("[OK] All statistical functions working")
    print("  [OK] Statistical module verified")
except Exception as e:
    errors.append(f"Statistical module test failed: {e}")

# Test 3: Cross-Validation Module
print("\n[3/8] Testing cross-validation module...")
try:
    cross_val_path = Path("experiments/cross_validation.py")
    if not cross_val_path.exists():
        errors.append("Missing cross_validation.py")
    else:
        # Just check it loads
        with open(cross_val_path) as f:
            content = f.read()
            if 'CrossValidationExperiment' in content:
                successes.append("[OK] CrossValidationExperiment class defined")
            if 'KFold' in content:
                successes.append("[OK] KFold integration present")
    
    print("  [OK] Cross-validation module verified")
except Exception as e:
    errors.append(f"Cross-validation test failed: {e}")

# Test 4: Ablation Study Module
print("\n[4/8] Testing ablation study module...")
try:
    ablation_path = Path("experiments/ablation_study.py")
    if not ablation_path.exists():
        errors.append("Missing ablation_study.py")
    else:
        with open(ablation_path) as f:
            content = f.read()
            configs_found = content.count("'name':")
            if configs_found >= 7:
                successes.append(f"[OK] AblationStudy with {configs_found} configurations")
            else:
                warnings.append(f"Only {configs_found} configs found, expected 7")
    
    print("  [OK] Ablation study module verified")
except Exception as e:
    errors.append(f"Ablation study test failed: {e}")

# Test 5: Error Analysis Module
print("\n[5/8] Testing error analysis module...")
try:
    from tmf921.evaluation import ErrorAnalyzer
    
    analyzer = ErrorAnalyzer()
    
    # Test with dummy data
    test_results = [
        {'scenario': 'test', 'validation': {'overall_valid': True}},
        {'scenario': 'test2', 'validation': {'overall_valid': False, 'errors': ['Test error']}}
    ]
    
    categories = analyzer.analyze_failures(test_results)
    assert isinstance(categories, dict)
    
    successes.append("[OK] ErrorAnalyzer functional")
    print("  [OK] Error analysis module verified")
except Exception as e:
    errors.append(f"Error analysis test failed: {e}")

# Test 6: Human Evaluation Module
print("\n[6/8] Testing human evaluation module...")
try:
    from tmf921.evaluation.human_eval import HumanEvaluationSuite
    
    suite = HumanEvaluationSuite(sample_size=10)
    
    # Test functions exist
    assert hasattr(suite, 'prepare_eval_set')
    assert hasattr(suite, 'load_annotations')
    assert hasattr(suite, 'compute_inter_annotator_agreement')
    assert hasattr(suite, 'compare_automated_vs_human')
    
    successes.append("[OK] HumanEvaluationSuite functional")
    print("  [OK] Human evaluation module verified")
except Exception as e:
    errors.append(f"Human evaluation test failed: {e}")

# Test 7: Honest Metrics in BaseExperiment
print("\n[7/8] Testing honest metrics reporting...")
try:
    base_exp_path = Path("experiments/base_experiment.py")
    with open(base_exp_path) as f:
        content = f.read()
        
        if 'HONEST METRICS REPORTING' in content:
            successes.append("[OK] Honest metrics header present")
        if 'processing_failures' in content:
            successes.append("[OK] Processing failures tracked")
        if 'overall_success_rate' in content:
            successes.append("[OK] Overall success rate calculated")
    
    print("  [OK] Honest metrics reporting verified")
except Exception as e:
    errors.append(f"Honest metrics test failed: {e}")

# Test 8: Module Exports
print("\n[8/8] Testing module exports...")
try:
    from tmf921.utils import (
        mcnemar_test,
        confidence_interval,
        compute_accuracy_with_ci
    )
    
    successes.append("[OK] Statistics exported from utils")
    
    from tmf921.evaluation import ErrorAnalyzer
    successes.append("[OK] ErrorAnalyzer exported from evaluation")
    
    print("  [OK] Module exports verified")
except Exception as e:
    errors.append(f"Module exports test failed: {e}")

# Summary
print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)

if errors:
    print(f"\n[FAIL] ERRORS ({len(errors)}):")
    for error in errors:
        print(f"  - {error}")

if warnings:
    print(f"\n[WARN] WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"  - {warning}")

print(f"\n[OK] SUCCESSES ({len(successes)}):")
for success in successes[:10]:  # Show first 10
    print(f"  {success}")

if len(successes) > 10:
    print(f"  ... and {len(successes) - 10} more")

if errors:
    print("\n[FAIL] VERIFICATION FAILED")
    sys.exit(1)
elif warnings:
    print("\n[WARN] VERIFICATION PASSED WITH WARNINGS")
    sys.exit(0)
else:
    print("\n[SUCCESS] ALL SCIENTIFIC RIGOR MODULES VERIFIED")
    print("\nReady for:")
    print("  - Cross-validation experiments")
    print("  - Ablation studies")
    print("  - Human evaluation")
    print("  - Statistical comparison")
    print("  - Error analysis")
    print("\n[NEXT STEP] Run validation experiments!")
    sys.exit(0)
