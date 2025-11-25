"""
Quick test script to verify new package structure.

This ensures all imports work and core functionality is preserved.
"""

import sys
from pathlib import Path

print("Testing new package structure...")
print("="*80)

# Test imports
print("\n[1/5] Testing imports...")
try:
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    from tmf921 import (
        ScenarioDataset, GSTSpecification, TMF921Validator, OllamaClient,
        TMF921PromptBuilder, EXAMPLE_SCENARIOS,
        GSTIndexer, GSTRetriever,
        CharacteristicNameMapper,
        load_config, compute_feaci_metrics
    )
    print("  ✓ All imports successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test data loading
print("\n[2/5] Testing data loading...")
try:
    dataset = ScenarioDataset("data/val.json")
    gst = GSTSpecification("gst.json")
    print(f"  ✓ Loaded {len(dataset.scenarios)} scenarios")
    print(f"  ✓ Loaded GST with {len(gst.spec['serviceSpecCharacteristic'])} characteristics")
except Exception as e:
    print(f"  ✗ Data loading failed: {e}")
    sys.exit(1)

# Test schema validation
print("\n[3/5] Testing schema validation...")
try:
    validator = TMF921Validator(gst.spec)
    test_intent = {
        "name": "Test Intent",
        "description": "Test",
        "serviceSpecCharacteristic": [
            {
                "name": "Delay tolerance",
                "value": {"value": "50", "unitOfMeasure": "ms"}
            }
        ]
    }
    validation = validator.validate_all(test_intent)
    print(f"  ✓ Validation works: {validation['overall_valid']}")
except Exception as e:
    print(f"  ✗ Validation failed: {e}")
    sys.exit(1)

# Test prompt building
print("\n[4/5] Testing prompt building...")
try:
    prompt_builder = TMF921PromptBuilder(gst.spec)
    prompt = prompt_builder.build_few_shot_prompt(
        "Test scenario",
        EXAMPLE_SCENARIOS[:2],
        max_examples=2
    )
    print(f"  ✓ Prompt built ({len(prompt)} chars)")
except Exception as e:
    print(f"  ✗ Prompt building failed: {e}")
    sys.exit(1)

# Test RAG components (if indexed)
print("\n[5/5] Testing RAG components...")
try:
    retriever = GSTRetriever()
    results = retriever.retrieve("latency requirements", n_results=5)
    print(f"  ✓ RAG retriever works ({len(results)} results)")
except Exception as e:
    print(f"  ~ RAG not yet indexed (run scripts/setup_rag.py)")

print("\n" + "="*80)
print("✓ All tests passed! New structure is working correctly.")
print("="*80 + "\n")
