"""
Few-shot validation experiment - Test with example-guided prompting.

Expected improvement: +40-50% accuracy over zero-shot baseline.
"""

import json
from pathlib import Path
from datetime import datetime

from llm_client import OllamaClient
from prompt_templates import TMF921PromptBuilder, EXAMPLE_SCENARIOS
from tmf921_schema import TMF921Validator
from name_mapper import CharacteristicNameMapper
from data_processor import GSTSpecification


def run_few_shot_validation():
    """Run few-shot validation experiment."""
    
    print("\n" + "="*80)
    print("TMF921 Intent Translation - Few-Shot Validation Experiment")
    print("="*80 + "\n")
    
    # Setup
    print("[1/7] Loading configuration and data...")
    gst = GSTSpecification("gst.json")
    validator = TMF921Validator(gst.spec)
    prompt_builder = TMF921PromptBuilder(gst.spec)
    name_mapper = CharacteristicNameMapper(gst.spec)
    
    # Load quick validation scenarios (same 10 for comparison)
    with open("data/quick_validation.json", 'r') as f:
        scenarios = json.load(f)
    
    print(f"[OK] Loaded {len(scenarios)} scenarios")
    
    # Initialize LLM client
    print("\n[2/7] Initializing Ollama client...")
    client = OllamaClient(model="llama3:latest")
    
    if not client._check_connection():
        print("[ERROR] Cannot connect to Ollama. Please ensure it's running.")
        return
    
    print(f"[OK] Connected using model: {client.model}")
    
    # Prepare results storage
    print("\n[3/7] Preparing experiment...")
    results_dir = Path("results") / "few_shot_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Run translations with few-shot prompting
    print(f"\n[4/7] Running few-shot translations on {len(scenarios)} scenarios...")
    print("-" * 80)
    print(f"Using {len(EXAMPLE_SCENARIOS)} examples for guidance")
    print("-" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}/{len(scenarios)}:")
        print(f"  Input: {scenario[:70]}...")
        
        # Build few-shot prompt
        system_prompt = prompt_builder.build_system_prompt()
        user_prompt = prompt_builder.build_few_shot_prompt(
            scenario, 
            EXAMPLE_SCENARIOS, 
            max_examples=3
        )
        
        try:
            # Generate
            response = client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2048
            )
            
            # Extract JSON
            intent_json = client.extract_json(response['response'])
            
            if not intent_json:
                print(f"  [FAIL] Could not extract JSON from response")
                results.append({
                    'scenario': scenario,
                    'generated_intent': None,
                    'error': 'Failed to extract JSON'
                })
                continue
            
            # Apply name correction
            corrected_intent, corrections = name_mapper.correct_intent(intent_json)
            
            # Validate
            validation = validator.validate_all(corrected_intent)
            
            # Store result
            result = {
                'scenario': scenario,
                'generated_intent': corrected_intent,
                'original_intent': intent_json if corrections else None,
                'name_corrections': corrections,
                'raw_response': response['response'][:500],
                'validation': validation,
                'metrics': {
                    'tokens': response['tokens'],
                    'time_seconds': response['time_seconds']
                }
            }
            results.append(result)
            
            # Print summary
            status = "[OK]" if validation['overall_valid'] else "[FAIL]"
            corrections_str = f", Corrected: {len(corrections)}" if corrections else ""
            print(f"  {status} Format: {validation['format_valid']}, "
                  f"Chars: {validation['characteristics_valid']}, "
                  f"Time: {response['time_seconds']:.1f}s{corrections_str}")
            
            if corrections:
                print(f"    Name fixes: {corrections[:2]}")
            
            if not validation['overall_valid'] and validation['errors']:
                print(f"    Errors: {validation['errors'][:1]}")
            
            # Save individual result
            result_file = results_dir / f"result_{i:02d}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
        except Exception as e:
            print(f"  [ERROR] Translation failed: {str(e)[:100]}")
            results.append({
                'scenario': scenario,
                'generated_intent': None,
                'error': str(e)
            })
    
    # Analyze results
    print(f"\n[5/7] Computing metrics...")
    print("-" * 80)
    
    valid_results = [r for r in results if r.get('validation')]
    
    if valid_results:
        format_valid_count = sum(1 for r in valid_results if r['validation']['format_valid'])
        overall_valid_count = sum(1 for r in valid_results if r['validation']['overall_valid'])
        corrections_made = sum(len(r.get('name_corrections', [])) for r in valid_results)
        
        total_time = sum(r['metrics']['time_seconds'] for r in valid_results)
        total_tokens = sum(r['metrics']['tokens'] for r in valid_results)
        avg_time = total_time / len(valid_results)
        avg_tokens = total_tokens / len(valid_results)
        
        # FEACI Metrics
        metrics_summary = {
            'experiment': 'few_shot_validation',
            'model': client.model,
            'num_scenarios': len(scenarios),
            'num_successful': len(valid_results),
            'num_corrections': corrections_made,
            'feaci': {
                'format_correctness': format_valid_count / len(valid_results) * 100,
                'accuracy': overall_valid_count / len(valid_results) * 100,
                'cost_avg_tokens': avg_tokens,
                'inference_time_avg_seconds': avg_time
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\nFEACI Metrics (Few-Shot + Name Correction):")
        print(f"  Format Correctness: {metrics_summary['feaci']['format_correctness']:.1f}%")
        print(f"  Overall Accuracy:   {metrics_summary['feaci']['accuracy']:.1f}%")
        print(f"  Name Corrections:   {corrections_made} automatic fixes")
        print(f"  Avg Tokens:         {metrics_summary['feaci']['cost_avg_tokens']:.0f}")
        print(f"  Avg Inference Time: {metrics_summary['feaci']['inference_time_avg_seconds']:.1f}s")
        
        # Save summary
        summary_file = results_dir / "metrics_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(metrics_summary, f, indent=2)
        
        print(f"\n[OK] Results saved to: {results_dir}/")
    
    # Comparison with zero-shot
    print(f"\n[6/7] Comparing with Zero-Shot Baseline...")
    print("-" * 80)
    
    # Load zero-shot results
    zero_shot_file = Path("results/quick_validation/metrics_summary.json")
    if zero_shot_file.exists():
        with open(zero_shot_file) as f:
            zero_shot = json.load(f)
        
        print(f"\nZero-Shot Baseline:")
        print(f"  Format: {zero_shot['feaci']['format_correctness']:.1f}%")
        print(f"  Accuracy: {zero_shot['feaci']['accuracy']:.1f}%")
        
        if valid_results:
            improvement = metrics_summary['feaci']['accuracy'] - zero_shot['feaci']['accuracy']
            print(f"\nFew-Shot + Corrections:")
            print(f"  Format: {metrics_summary['feaci']['format_correctness']:.1f}%")
            print(f"  Accuracy: {metrics_summary['feaci']['accuracy']:.1f}%")
            print(f"\n  Improvement: +{improvement:.1f} percentage points")
            
            if improvement >= 40:
                print(f"  Status: ✅ Target improvement achieved!")
            elif improvement >= 20:
                print(f"  Status: ⚠️  Good progress, approaching target")
            else:
                print(f"  Status: ❌ Below expected improvement")
    
    # Final report
    print(f"\n[7/7] Experiment Complete!")
    print("=" * 80)
    
    if valid_results:
        print(f"\nResults:")
        print(f"  Valid translations: {overall_valid_count}/{len(valid_results)}")
        print(f"  Auto-corrections: {corrections_made} characteristic names fixed")
        print(f"\nNext Steps:")
        if overall_valid_count >= 7:
            print(f"  ✅ Accuracy target met! Ready for full 50-scenario evaluation")
        else:
            print(f"  → Analyze remaining errors")
            print(f"  → Consider RAG enhancement for complex scenarios")
            print(f"  → Test Chain-of-Thought reasoning")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_few_shot_validation()
