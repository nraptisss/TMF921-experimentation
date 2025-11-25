"""
RAG Validation - Test RAG enhancement on previously failed scenarios.

Goal: Improve accuracy from 80% to 90%+ by providing relevant characteristics.
"""

import json
from pathlib import Path
from datetime import datetime

from llm_client import OllamaClient
from prompt_templates import TMF921PromptBuilder
from tmf921_schema import TMF921Validator
from name_mapper import CharacteristicNameMapper
from rag_retriever import GSTRetriever
from data_processor import GSTSpecification


def run_rag_validation():
    """Run RAG validation on quick validation set."""
    
    print("\n" + "="*80)
    print("TMF921 Intent Translation - RAG Validation Experiment")
    print("="*80 + "\n")
    
    # Setup
    print("[1/7] Loading configuration and components...")
    gst = GSTSpecification("gst.json")
    validator = TMF921Validator(gst.spec)
    prompt_builder = TMF921PromptBuilder(gst.spec)
    name_mapper = CharacteristicNameMapper(gst.spec)
    retriever = GSTRetriever()
    
    # Load quick validation scenarios
    with open("data/quick_validation.json", 'r') as f:
        scenarios = json.load(f)
    
    print(f"[OK] Loaded {len(scenarios)} scenarios")
    print(f"[OK] RAG retriever initialized")
    
    # Initialize LLM client
    print("\n[2/7] Initializing Ollama client...")
    client = OllamaClient(model="llama3:latest")
    
    if not client._check_connection():
        print("[ERROR] Cannot connect to Ollama")
        return
    
    print(f"[OK] Connected using model: {client.model}")
    
    # Prepare results storage
    print("\n[3/7] Preparing experiment...")
    results_dir = Path("results") / "rag_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Run translations with RAG
    print(f"\n[4/7] Running RAG-enhanced translations on {len(scenarios)} scenarios...")
    print("-" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}/{len(scenarios)}:")
        print(f"  Input: {scenario[:70]}...")
        
        # Retrieve relevant characteristics
        retrieved_chars = retriever.retrieve_for_scenario(scenario, n_results=8)
        print(f"  Retrieved: {len(retrieved_chars)} characteristics")
        
        # Build RAG prompt
        system_prompt = prompt_builder.build_system_prompt()
        user_prompt = prompt_builder.build_rag_prompt(
            scenario,
            retrieved_chars,
            include_examples=True
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
            
            # Apply name correction (as backup)
            corrected_intent, corrections = name_mapper.correct_intent(intent_json)
            
            # Validate
            validation = validator.validate_all(corrected_intent)
            
            # Store result
            result = {
                'scenario': scenario,
                'generated_intent': corrected_intent,
                'retrieved_characteristics': [c['name'] for c in retrieved_chars],
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
            
            if not validation['overall_valid'] and validation['errors']:
                print(f"    Errors: {validation['errors'][:1]}")
            
            # Save individual result
            result_file = results_dir / f"result_{i:02d}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            results.append({
                'scenario': scenario,
                'generated_intent': None,
                'error': str(e)
            })
    
    # Compute metrics
    print(f"\n[5/7] Computing metrics...")
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
            'experiment': 'rag_validation_10_scenarios',
            'model': client.model,
            'num_scenarios': len(scenarios),
            'num_successful': len(valid_results),
            'num_corrections': corrections_made,
            'feaci': {
                'format_correctness': format_valid / len(valid_results) * 100,
                'accuracy': overall_valid / len(valid_results) * 100,
                'cost_avg_tokens': avg_tokens,
                'inference_time_avg_seconds': avg_time
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\nFEACI Metrics (RAG):")
        print(f"  Format Correctness: {metrics_summary['feaci']['format_correctness']:.1f}%")
        print(f"  Overall Accuracy:   {metrics_summary['feaci']['accuracy']:.1f}%")
        print(f"  Name Corrections:   {corrections_made}")
        print(f"  Avg Tokens:         {metrics_summary['feaci']['cost_avg_tokens']:.0f}")
        print(f"  Avg Inference Time: {metrics_summary['feaci']['inference_time_avg_seconds']:.1f}s")
        
        # Save summary
        summary_file = results_dir / "metrics_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(metrics_summary, f, indent=2)
        
        print(f"\n[OK] Results saved to: {results_dir}/")
    
    # Compare with baselines
    print(f"\n[6/7] Comparing with baselines...")
    print("-" * 80)
    
    # Load baseline results
    few_shot_file = Path("results/few_shot_validation/metrics_summary.json")
    if few_shot_file.exists():
        with open(few_shot_file) as f:
            few_shot = json.load(f)
        
        print(f"\nFew-Shot Baseline (10 scenarios): {few_shot['feaci']['accuracy']:.1f}%")
        if valid_results:
            rag_accuracy = metrics_summary['feaci']['accuracy']
            improvement = rag_accuracy - few_shot['feaci']['accuracy']
            print(f"RAG Enhanced:                     {rag_accuracy:.1f}%")
            print(f"Improvement:                      {improvement:+.1f} percentage points")
            
            if improvement >= 10:
                print(f"\n  Status: ✅ Significant improvement achieved!")
            elif improvement >= 5:
                print(f"\n  Status: ⚠️  Moderate improvement")
            else:
                print(f"\n  Status: ❌ Limited improvement - RAG may not be helping")
    
    # Final report
    print(f"\n[7/7] Experiment Complete!")
    print("=" * 80)
    
    if valid_results:
        print(f"\nResults:")
        print(f"  Valid translations: {overall_valid}/{len(valid_results)}")
        print(f"  Auto-corrections: {corrections_made}")
        
        if overall_valid >= 9:
            print(f"\n  Status: ✅ Ready for full 50-scenario RAG validation!")
        else:
            print(f"\n  Status: → Analyze retrieval quality and adjust")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_rag_validation()
