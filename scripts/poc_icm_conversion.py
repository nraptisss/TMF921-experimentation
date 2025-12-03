"""
Proof of Concept: Convert test scenarios to ICM format.

This script demonstrates Option B (Pragmatic Hybrid) by:
1. Loading scenarios from our test set
2. Generating simple JSON intents (current pipeline)
3. Converting to ICM format
4. Validating both formats
5. Saving side-by-side comparison
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tmf921.icm.converter import SimpleToICMConverter
from tmf921.icm.models import ICMIntent


def load_test_scenarios(num_scenarios=5):
    """Load first N scenarios from test set."""
    test_file = Path(__file__).parent.parent / "data" / "test.json"
    with open(test_file, 'r') as f:
        scenarios = json.load(f)
    return scenarios[:num_scenarios]


def create_simple_intent(scenario: str, index: int) -> dict:
    """
    Simulate our current pipeline output (simplified for PoC).
    
    In production, this would be:
    - LLM generation with RAG
    - TMF921 validation
    - Name correction
    """
    # This is a mock - in reality, LLM would generate this
    simple_intent = {
        "name": f"Scenario {index + 1} Intent",
        "description": scenario[:100] + "..." if len(scenario) > 100 else scenario,
        "serviceSpecCharacteristic": []
    }
    
    # Extract some characteristics (simplified pattern matching)
    if "latency" in scenario.lower() or "delay" in scenario.lower():
        # Try to extract number
        import re
        match = re.search(r'(\d+)\s*ms', scenario.lower())
        if match:
            simple_intent["serviceSpecCharacteristic"].append({
                "name": "Delay tolerance",
                "value": {"value": match.group(1), "unitOfMeasure": "ms"}
            })
    
    if "bandwidth" in scenario.lower() or "mbps" in scenario.lower() or "gbps" in scenario.lower():
        match = re.search(r'(\d+)\s*(mbps|gbps)', scenario.lower())
        if match:
            simple_intent["serviceSpecCharacteristic"].append({
                "name": "Guaranteed bandwidth",
                "value": {"value": match.group(1), "unitOfMeasure": match.group(2).upper()}
            })
    
    if "availability" in scenario.lower() or "uptime" in scenario.lower():
        match = re.search(r'([\d.]+)\s*%', scenario)
        if match:
            simple_intent["serviceSpecCharacteristic"].append({
                "name": "Availability",
                "value": {"value": match.group(1), "unitOfMeasure": "percent"}
            })
    
    # If no characteristics extracted, add a default
    if not simple_intent["serviceSpecCharacteristic"]:
        simple_intent["serviceSpecCharacteristic"].append({
            "name": "Service level",
            "value": {"value": "standard", "unitOfMeasure": ""}
        })
    
    return simple_intent


def main():
    """Run proof of concept."""
    print("=" * 80)
    print("TMF921 ICM Conversion - Proof of Concept")
    print("Option B: Pragmatic Hybrid")
    print("=" * 80)
    print()
    
    # Load scenarios
    print("Loading test scenarios...")
    scenarios = load_test_scenarios(5)
    print(f"✓ Loaded {len(scenarios)} scenarios")
    print()
    
    # Initialize converter
    converter = SimpleToICMConverter()
    
    # Process each scenario
    results = []
    
    for i, scenario in enumerate(scenarios):
        print(f"\n--- Scenario {i + 1} ---")
        print(f"Input: {scenario[:80]}...")
        print()
        
        # Step 1: Generate simple JSON (simulate current pipeline)
        print("  1. Generating simple JSON...")
        simple_intent = create_simple_intent(scenario, i)
        print(f"     ✓ Generated intent with {len(simple_intent['serviceSpecCharacteristic'])} characteristics")
        
        # Step 2: Convert to ICM
        print("  2. Converting to ICM format...")
        try:
            icm_intent = converter.convert(simple_intent)
            print(f"     ✓ Converted to ICM with {len(icm_intent['hasExpectation'])} expectations")
            
            # Step 3: Validate ICM structure
            print("  3. Validating ICM structure...")
            try:
                validated = ICMIntent(**icm_intent)
                print("     ✓ ICM structure valid")
                conversion_success = True
            except Exception as e:
                print(f"     ✗ ICM validation failed: {e}")
                conversion_success = False
        except Exception as e:
            print(f"     ✗ Conversion failed: {e}")
            icm_intent = None
            conversion_success = False
        
        # Store results
        results.append({
            "scenario": scenario,
            "simple_intent": simple_intent,
            "icm_intent": icm_intent,
            "conversion_success": conversion_success
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r["conversion_success"])
    print(f"Successful conversions: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print()
    
    # Save results
    output_dir = Path(__file__).parent.parent / "tests" / "fixtures" / "tmf921_examples" / "poc_results"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    for i, result in enumerate(results):
        # Save simple format
        simple_file = output_dir / f"scenario_{i+1}_simple.json"
        with open(simple_file, 'w') as f:
            json.dump(result["simple_intent"], f, indent=2)
        
        # Save ICM format
        if result["icm_intent"]:
            icm_file = output_dir / f"scenario_{i+1}_icm.json"
            with open(icm_file, 'w') as f:
                json.dump(result["icm_intent"], f, indent=2)
    
    print(f"✓ Results saved to: {output_dir}")
    print()
    
    # Show example comparison
    if results[0]["icm_intent"]:
        print("Example Comparison (Scenario 1):")
        print("\nSimple JSON:")
        print(json.dumps(results[0]["simple_intent"], indent=2)[:300] + "...")
        print("\nICM JSON-LD:")
        print(json.dumps(results[0]["icm_intent"], indent=2)[:300] + "...")
    
    print("\n" + "=" * 80)
    print("Proof of Concept Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
