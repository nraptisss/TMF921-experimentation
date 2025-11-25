"""
Quick validation experiment - Run zero-shot TMF921 translation on 10 scenarios.

This is the first experiment to validate the entire pipeline works.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import our modules
from llm_client import OllamaClient, load_llm_client
from prompt_templates import TMF921PromptBuilder
from tmf921_schema import TMF921Validator
from data_processor import ScenarioDataset, GSTSpecification


def run_quick_validation():
    """Run quick validation experiment."""
    
    print("\n" + "="*80)
    print("TMF921 Intent Translation - Quick Validation Experiment")
    print("="*80 + "\n")
    
    # Setup
    print("[1/6] Loading configuration and data...")
    gst = GSTSpecification("gst.json")
    validator = TMF921Validator(gst.spec)
    prompt_builder = TMF921PromptBuilder(gst.spec)
    
    # Load quick validation scenarios
    with open("data/quick_validation.json", 'r') as f:
        scenarios = json.load(f)
    
    print(f"[OK] Loaded {len(scenarios)} scenarios for quick validation")
    
    #Initialize LLM client
    print("\n[2/6] Initializing Ollama client...")
    try:
        # Try llama3:latest (4.7GB) - should fit in 9GB RAM
        client = OllamaClient(model="llama3:latest")
        
        if not client._check_connection():
            print("\n" + "!"*80)
            print("ERROR: Cannot connect to Ollama")
            print("!"*80)
            print("\nPlease follow these steps:")
            print("  1. Install Ollama from: https://ollama.com/download")
            print("  2. Start Ollama: 'ollama serve'")
            print("  3. Pull the model: 'ollama pull phi3:mini'")
            print("  4. Re-run this script\n")
            return
        
        print(f"[OK] Connected to Ollama using model: {client.model}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize LLM client: {e}")
        print("\nPlease ensure Ollama is installed and running.")
        return
    
    # Prepare results storage
    print("\n[3/6] Preparing experiment...")
    results_dir = Path("results") / "quick_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
   
    
    results = []
    
    # Run translations
    print(f"\n[4/6] Running zero-shot translations on {len(scenarios)} scenarios...")
    print("-" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}/{len(scenarios)}:")
        print(f"  Input: {scenario[:70]}...")
        
        # Build prompt
        system_prompt = prompt_builder.build_system_prompt()
        user_prompt = prompt_builder.build_zero_shot_prompt(scenario, include_examples_list=True)
        
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
            
            # Validate
            validation = validator.validate_all(intent_json) if intent_json else {
                'format_valid': False,
                'overall_valid': False,
                'errors': ['Failed to extract valid JSON from response']
            }
            
            # Store result
            result = {
                'scenario': scenario,
                'generated_intent': intent_json,
                'raw_response': response['response'][:500],  # Truncate for storage
                'validation': validation,
                'metrics': {
                    'tokens': response['tokens'],
                    'time_seconds': response['time_seconds']
                }
            }
            results.append(result)
            
            # Print summary
            status = "[OK]" if validation['overall_valid'] else "[FAIL]"
            print(f"  {status} Format: {validation['format_valid']}, "
                  f"Chars: {validation['characteristics_valid']}, "
                  f"Time: {response['time_seconds']:.2f}s")
            
            if not validation['overall_valid']:
                print(f"  Errors: {validation['errors'][:2]}")
            
            # Save individual result
            result_file = results_dir / f"result_{i:02d}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
        except Exception as e:
            print(f"  [ERROR] Translation failed: {e}")
            results.append({
                'scenario': scenario,
                'generated_intent': None,
                'error': str(e)
            })
    
    # Analyze results
    print(f"\n[5/6] Computing metrics...")
    print("-" * 80)
    
    valid_results = [r for r in results if r.get('validation')]
    
    if valid_results:
        format_valid_count = sum(1 for r in valid_results if r['validation']['format_valid'])
        overall_valid_count = sum(1 for r in valid_results if r['validation']['overall_valid'])
        
        total_time = sum(r['metrics']['time_seconds'] for r in valid_results)
        total_tokens = sum(r['metrics']['tokens'] for r in valid_results)
        avg_time = total_time / len(valid_results)
        avg_tokens = total_tokens / len(valid_results)
        
        # FEACI Metrics (Format, Explainability, Accuracy, Cost, Inference time)
        metrics_summary = {
            'experiment': 'quick_validation_zero_shot',
            'model': client.model,
            'num_scenarios': len(scenarios),
            'num_successful': len(valid_results),
            'feaci': {
                'format_correctness': format_valid_count / len(valid_results) * 100,
                'accuracy': overall_valid_count / len(valid_results) * 100,
                'cost_avg_tokens': avg_tokens,
                'inference_time_avg_seconds': avg_time
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\nFEACI Metrics:")
        print(f"  Format Correctness: {metrics_summary['feaci']['format_correctness']:.1f}%")
        print(f"  Overall Accuracy:   {metrics_summary['feaci']['accuracy']:.1f}%")
        print(f"  Avg Tokens:         {metrics_summary['feaci']['cost_avg_tokens']:.0f}")
        print(f"  Avg Inference Time: {metrics_summary['feaci']['inference_time_avg_seconds']:.2f}s")
        
        # Save summary
        summary_file = results_dir / "metrics_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(metrics_summary, f, indent=2)
        
        print(f"\n[OK] Results saved to: {results_dir}/")
    
    # Final report
    print(f"\n[6/6] Experiment Complete!")
    print("=" * 80)
    
    if valid_results:
        print(f"\nSuccess Rate: {len(valid_results)}/{len(scenarios)} scenarios translated")
        print(f"Format Correctness: {format_valid_count}/{len(valid_results)} valid")
        print(f"Overall Valid: {overall_valid_count}/{len(valid_results)}")
        
        print(f"\nNext Steps:")
        print(f"  1. Review results in: {results_dir}/")
        print(f"  2. Examine failed cases to improve prompts")
        print(f"  3. Run full experiments on 50+ scenarios")
        print(f"  4. Try few-shot and CoT prompting")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_quick_validation()
