"""
Full 50-scenario validation experiment.

Tests the few-shot + name correction approach on validation set.
"""

import json
from pathlib import Path
from datetime import datetime
import random

from llm_client import OllamaClient
from prompt_templates import TMF921PromptBuilder, EXAMPLE_SCENARIOS
from tmf921_schema import TMF921Validator
from name_mapper import CharacteristicNameMapper
from data_processor import GSTSpecification


def run_full_validation():
    """Run validation on 50 scenarios."""
    
    print("\n" + "="*80)
    print("TMF921 Intent Translation - Full 50-Scenario Validation")
    print("="*80 + "\n")
    
    # Setup
    print("[1/7] Loading configuration and data...")
    gst = GSTSpecification("gst.json")
    validator = TMF921Validator(gst.spec)
    prompt_builder = TMF921PromptBuilder(gst.spec)
    name_mapper = CharacteristicNameMapper(gst.spec)
    
    # Load validation set
    with open("data/val.json", 'r') as f:
        all_scenarios = json.load(f)
    
    # Use first 50 scenarios
    scenarios = all_scenarios[:50]
    
    print(f"[OK] Loaded {len(scenarios)} scenarios from validation set")
    
    # Initialize LLM client
    print("\n[2/7] Initializing Ollama client...")
    client = OllamaClient(model="llama3:latest")
    
    if not client._check_connection():
        print("[ERROR] Cannot connect to Ollama")
        return
    
    print(f"[OK] Connected using model: {client.model}")
    
    # Prepare results storage
    print("\n[3/7] Preparing experiment...")
    results_dir = Path("results") / "validation_50"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Run translations
    print(f"\n[4/7] Running few-shot translations on {len(scenarios)} scenarios...")
    print("-" * 80)
    print(f"Estimated time: ~{len(scenarios) * 30 / 60:.0f} minutes")
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
                print(f"  [FAIL] Could not extract JSON")
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
                'name_corrections': corrections,
                'validation': validation,
                'metrics': {
                    'tokens': response['tokens'],
                    'time_seconds': response['time_seconds']
                }
            }
            results.append(result)
            
            # Print summary
            status = "[OK]" if validation['overall_valid'] else "[FAIL]"
            print(f"  {status} Valid: {validation['overall_valid']}, "
                  f"Corrections: {len(corrections)}, "
                  f"Time: {response['time_seconds']:.1f}s")
            
            # Save every 10 results
            if i % 10 == 0:
                checkpoint_file = results_dir / f"checkpoint_{i}.json"
                with open(checkpoint_file, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"  [CHECKPOINT] Saved {i} results")
            
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            results.append({
                'scenario': scenario,
                'generated_intent': None,
                'error': str(e)
            })
    
    # Save final results
    print(f"\n[5/7] Saving results...")
    final_file = results_dir / "all_results.json"
    with open(final_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[OK] Saved to {final_file}")
    
    # Compute metrics
    print(f"\n[6/7] Computing metrics...")
    print("-" * 80)
    
    valid_results = [r for r in results if r.get('validation')]
    
    if valid_results:
        format_valid = sum(1 for r in valid_results if r['validation']['format_valid'])
        overall_valid = sum(1 for r in valid_results if r['validation']['overall_valid'])
        corrections_made = sum(len(r.get('name_corrections', [])) for r in valid_results)
        
        total_time = sum(r['metrics']['time_seconds'] for r in valid_results)
        total_tokens = sum(r['metrics']['tokens'] for r in valid_results)
        avg_time = total_time / len(valid_results)
        avg_tokens = total_tokens / len(valid_results)
        
        # FEACI Metrics
        metrics_summary = {
            'experiment': 'validation_50_scenarios',
            'model': client.model,
            'num_scenarios': len(scenarios),
            'num_successful': len(valid_results),
            'num_corrections': corrections_made,
            'feaci': {
                'format_correctness': format_valid / len(valid_results) * 100,
                'accuracy': overall_valid / len(valid_results) * 100,
                'cost_avg_tokens': avg_tokens,
                'cost_total_tokens': total_tokens,
                'inference_time_avg_seconds': avg_time,
                'inference_time_total_seconds': total_time
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\nFEACI Metrics (50 Scenarios):")
        print(f"  Format Correctness: {metrics_summary['feaci']['format_correctness']:.1f}%")
        print(f"  Overall Accuracy:   {metrics_summary['feaci']['accuracy']:.1f}%")
        print(f"  Name Corrections:   {corrections_made}")
        print(f"  Total Time:         {total_time/60:.1f} minutes")
        print(f"  Total Tokens:       {total_tokens:,}")
        print(f"  Avg Time/Scenario:  {avg_time:.1f}s")
        
        # Save summary
        summary_file = results_dir / "metrics_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(metrics_summary, f, indent=2)
        
        print(f"\n[OK] Metrics saved to: {summary_file}")
    
    # Final report
    print(f"\n[7/7] Validation Complete!")
    print("=" * 80)
    
    if valid_results:
        print(f"\nResults Summary:")
        print(f"  Valid translations: {overall_valid}/{len(valid_results)} ({overall_valid/len(valid_results)*100:.1f}%)")
        print(f"  Auto-corrections:   {corrections_made} names fixed")
        print(f"  Processing time:    {total_time/60:.1f} minutes")
        
        if overall_valid / len(valid_results) >= 0.70:
            print(f"\n  Status: ✅ Achieved 70%+ accuracy target!")
        else:
            print(f"\n  Status: ⚠️  Below 70% target")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_full_validation()
