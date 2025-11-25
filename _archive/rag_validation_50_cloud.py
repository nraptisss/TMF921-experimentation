"""
RAG Full Validation with Ollama Cloud (gpt-oss:20b-cloud).

Much faster than local models - expect 5-10s per scenario vs 90s.
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


def run_rag_cloud_validation():
    """Run RAG validation on 50 scenarios with cloud model."""
    
    print("\n" + "="*80)
    print("TMF921 Intent Translation - RAG + Cloud Model (50 Scenarios)")
    print("Model: gpt-oss:20b-cloud (Ollama Cloud)")
    print("="*80 + "\n")
    
    # Setup
    print("[1/7] Loading configuration and components...")
    gst = GSTSpecification("gst.json")
    validator = TMF921Validator(gst.spec)
    prompt_builder = TMF921PromptBuilder(gst.spec)
    name_mapper = CharacteristicNameMapper(gst.spec)
    retriever = GSTRetriever()  # Now uses fixed retriever with -1.0 threshold
    
    # Load validation scenarios
    with open("data/val.json", 'r') as f:
        all_scenarios = json.load(f)
    
    scenarios = all_scenarios[:50]
    
    print(f"[OK] Loaded {len(scenarios)} scenarios")
    print(f"[OK] RAG retriever initialized (fixed version)")
    
    # Initialize cloud LLM client
    print("\n[2/7] Initializing Ollama Cloud client...")
    print("Note: Make sure you're signed into Ollama Cloud (ollama signin)")
    
    client = OllamaClient(model="gpt-oss:20b-cloud")
    
    if not client._check_connection():
        print("[ERROR] Cannot connect to Ollama")
        print("Run: ollama signin")
        return
    
    print(f"[OK] Connected to cloud model: {client.model}")
    
    # Prepare results storage
    print("\n[3/7] Preparing experiment...")
    results_dir = Path("results") / "rag_cloud_validation_50"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Run translations with RAG + Cloud
    print(f"\n[4/7] Running RAG+Cloud translations on {len(scenarios)} scenarios...")
    print("-" * 80)
    print(f"Expected time: ~{len(scenarios) * 10 / 60:.0f} minutes (10s per scenario)")
    print("-" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}/{len(scenarios)}:")
        print(f"  Input: {scenario[:70]}...")
        
        # Retrieve relevant characteristics (using fixed retriever)
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
            # Generate with cloud model
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
                  f"Retrieved: {len(retrieved_chars)}, "
                  f"Corrections: {len(corrections)}, "
                  f"Time: {response['time_seconds']:.1f}s")
            
            if not validation['overall_valid'] and validation['errors']:
                print(f"    Errors: {validation['errors'][:1]}")
            
            # Save checkpoints
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
    
    # Save all results
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
            'experiment': 'rag_cloud_validation_50_scenarios',
            'model': 'gpt-oss:20b-cloud',
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
        
        print(f"\nFEACI Metrics (RAG + Cloud):")
        print(f"  Format Correctness: {metrics_summary['feaci']['format_correctness']:.1f}%")
        print(f"  Overall Accuracy:   {metrics_summary['feaci']['accuracy']:.1f}%")
        print(f"  Name Corrections:   {corrections_made}")
        print(f"  Total Time:         {total_time/60:.1f} minutes")
        print(f"  Avg Time/Scenario:  {avg_time:.1f}s")
        print(f"  Total Tokens:       {total_tokens:,}")
        
        # Save summary
        summary_file = results_dir / "metrics_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(metrics_summary, f, indent=2)
        
        print(f"\n[OK] Metrics saved to: {summary_file}")
    
    # Compare with baselines
    print(f"\n[7/7] Comparing with baselines...")
    print("-" * 80)
    
    baseline_file = Path("results/validation_50/metrics_summary.json")
    if baseline_file.exists():
        with open(baseline_file) as f:
            baseline = json.load(f)
        
        print(f"\nFew-Shot Baseline (50 scenarios, local):  {baseline['feaci']['accuracy']:.1f}% in {baseline['feaci']['inference_time_total_seconds']/60:.1f} min")
        if valid_results:
            rag_accuracy = metrics_summary['feaci']['accuracy']
            improvement = rag_accuracy - baseline['feaci']['accuracy']
            speedup = baseline['feaci']['inference_time_avg_seconds'] / avg_time
            print(f"RAG + Cloud (50 scenarios):                {rag_accuracy:.1f}% in {total_time/60:.1f} min")
            print(f"Accuracy improvement:                      {improvement:+.1f} percentage points")
            print(f"Speed improvement:                         {speedup:.1f}x faster")
    
    # Final report
    print(f"\nExperiment Complete!")
    print("=" * 80)
    
    if valid_results:
        print(f"\nResults:")
        print(f"  Valid translations: {overall_valid}/{len(valid_results)} ({overall_valid/len(valid_results)*100:.1f}%)")
        print(f"  Auto-corrections:   {corrections_made}")
        print(f"  Processing time:    {total_time/60:.1f} minutes")
        print(f"  Avg speed:          {avg_time:.1f}s per scenario")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_rag_cloud_validation()
