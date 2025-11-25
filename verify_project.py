"""
Comprehensive project verification script.

Tests all components to ensure everything works correctly.
"""

import sys
from pathlib import Path
import json

print("="*80)
print("TMF921 PROJECT VERIFICATION")
print("="*80)

errors = []
warnings = []
successes = []

# Test 1: Package Structure
print("\n[1/10] Testing package structure...")
try:
    required_dirs = [
        "src/tmf921",
        "src/tmf921/core",
        "src/tmf921/prompting",
        "src/tmf921/rag",
        "src/tmf921/post_processing",
        "src/tmf921/utils",
        "experiments",
        "scripts",
        "docs",
        "data",
        "_archive"
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            errors.append(f"Missing directory: {dir_path}")
        else:
            successes.append(f"[OK] Directory exists: {dir_path}")
    
    print(f"  Checked {len(required_dirs)} directories")
except Exception as e:
    errors.append(f"Package structure test failed: {e}")

# Test 2: Core Imports
print("\n[2/10] Testing core imports...")
try:
    sys.path.insert(0, "src")
    
    from tmf921 import (
        ScenarioDataset, GSTSpecification, TMF921Validator, OllamaClient,
        TMF921PromptBuilder, EXAMPLE_SCENARIOS,
        GSTIndexer, GSTRetriever,
        CharacteristicNameMapper,
        load_config, compute_feaci_metrics
    )
    
    successes.append("[OK] All core imports successful")
    print("  [OK] All imports working")
except Exception as e:
    errors.append(f"Import failed: {e}")
    print(f"  [FAIL] Import error: {e}")

# Test 3: Data Loading
print("\n[3/10] Testing data loading...")
try:
    gst = GSTSpecification("gst.json")
    if len(gst.characteristics) != 87:
        errors.append(f"GST has {len(gst.characteristics)} characteristics, expected 87")
    else:
        successes.append(f"[OK] GST loaded correctly (87 characteristics)")
    
    dataset = ScenarioDataset("data/val.json")
    if len(dataset.scenarios) == 0:
        errors.append("No scenarios loaded")
    else:
        successes.append(f"[OK] Loaded {len(dataset.scenarios)} scenarios")
    
    print(f"  [OK] Data loaded successfully")
except Exception as e:
    errors.append(f"Data loading failed: {e}")
    print(f"  [FAIL] Error: {e}")

# Test 4: Schema Validation
print("\n[4/10] Testing schema validation...")
try:
    validator = TMF921Validator(gst.spec)
    
    # Test valid intent
    test_intent = {
        "name": "Test Intent",
        "description": "Test description",
        "serviceSpecCharacteristic": [
            {
                "name": "Delay tolerance",
                "value": {"value": "100", "unitOfMeasure": "ms"}
            }
        ]
    }
    
    validation = validator.validate_all(test_intent)
    if not validation['overall_valid']:
        errors.append(f"Valid intent marked invalid: {validation['errors']}")
    else:
        successes.append("[OK] Validation working correctly")
    
    print("  [OK] Validator functional")
except Exception as e:
    errors.append(f"Validation test failed: {e}")
    print(f"  [FAIL] Error: {e}")

# Test 5: Prompt Building
print("\n[5/10] Testing prompt building...")
try:
    prompt_builder = TMF921PromptBuilder(gst.spec)
    
    # Test zero-shot
    zero_shot = prompt_builder.build_zero_shot_prompt("Test scenario")
    if len(zero_shot) == 0:
        errors.append("Zero-shot prompt is empty")
    else:
        successes.append(f"[OK] Zero-shot prompt built ({len(zero_shot)} chars)")
    
    # Test few-shot
    few_shot = prompt_builder.build_few_shot_prompt(
        "Test scenario",
        EXAMPLE_SCENARIOS[:2],
        max_examples=2
    )
    if len(few_shot) == 0:
        errors.append("Few-shot prompt is empty")
    else:
        successes.append(f"[OK] Few-shot prompt built ({len(few_shot)} chars)")
    
    print("  [OK] Prompt builder functional")
except Exception as e:
    errors.append(f"Prompt building failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 6: Name Mapper
print("\n[6/10] Testing name mapper...")
try:
    mapper = CharacteristicNameMapper(gst.spec)
    
    # Test correction
    corrected = mapper.correct_name("E2E latency")
    if corrected != "Delay tolerance":
        warnings.append(f"Name mapping unexpected: E2E latency -> {corrected}")
    else:
        successes.append("[OK] Name mapping working")
    
    print("  [OK] Name mapper functional")
except Exception as e:
    errors.append(f"Name mapper test failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 7: Configuration
print("\n[7/10] Testing configuration...")
try:
    config = load_config("config.yaml")
    
    if 'models' not in config:
        errors.append("Config missing 'models' section")
    if 'experiments' not in config:
        errors.append("Config missing 'experiments' section")
    
    # Check cloud model exists
    models = config.get('models', {}).get('ollama', {}).get('models', [])
    cloud_models = [m for m in models if m.get('name') == 'gpt-oss:20b-cloud']
    
    if not cloud_models:
        warnings.append("Cloud model not in config")
    else:
        successes.append("[OK] Cloud model configured")
    
    print("  [OK] Configuration valid")
except Exception as e:
    errors.append(f"Config test failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 8: Documentation
print("\n[8/10] Testing documentation...")
try:
    required_docs = [
        "README.md",
        "docs/API.md",
        "docs/ARCHITECTURE.md",
        "docs/TUTORIAL.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "LICENSE"
    ]
    
    for doc in required_docs:
        if not Path(doc).exists():
            errors.append(f"Missing documentation: {doc}")
        else:
            successes.append(f"[OK] Doc exists: {doc}")
    
    print(f"  [OK] All {len(required_docs)} docs present")
except Exception as e:
    errors.append(f"Documentation test failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 9: GitHub Readiness
print("\n[9/10] Testing GitHub readiness...")
try:
    github_files = [".gitignore", "LICENSE", "setup.py", "requirements.txt"]
    
    for gfile in github_files:
        if not Path(gfile).exists():
            errors.append(f"Missing GitHub file: {gfile}")
        else:
            successes.append(f"[OK] GitHub file: {gfile}")
    
    print("  [OK] GitHub files present")
except Exception as e:
    errors.append(f"GitHub readiness test failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 10: Results Preservation
print("\n[10/10] Testing results preservation...")
try:
    results_dir = Path("results")
    
    key_experiments = [
        "validation_50",
        "rag_cloud_50_scenarios"
    ]
    
    for exp in key_experiments:
        exp_dir = results_dir / exp
        if not exp_dir.exists():
            warnings.append(f"Results missing: {exp}")
        else:
            metrics_file = exp_dir / "metrics_summary.json"
            if metrics_file.exists():
                with open(metrics_file) as f:
                    metrics = json.load(f)
                    accuracy = metrics.get('feaci', {}).get('accuracy', 0)
                    successes.append(f"[OK] {exp}: {accuracy:.0f}% accuracy")
            else:
                warnings.append(f"Missing metrics: {exp}")
    
    print("  [OK] Results preserved")
except Exception as e:
    errors.append(f"Results test failed: {e}")
    print(f"  ✗ Error: {e}")

# Summary
print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)

if errors:
    print(f"\n❌ ERRORS ({len(errors)}):")
    for error in errors:
        print(f"  - {error}")

if warnings:
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"  - {warning}")

print(f"\n[OK] SUCCESSES ({len(successes)})")

if errors:
    print("\n[FAIL] VERIFICATION FAILED")
    sys.exit(1)
elif warnings:
    print("\n[WARN] VERIFICATION PASSED WITH WARNINGS")
    sys.exit(0)
else:
    print("\n[SUCCESS] VERIFICATION PASSED - ALL TESTS SUCCESSFUL")
    sys.exit(0)
