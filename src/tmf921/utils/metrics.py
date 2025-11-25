"""FEACI metrics computation."""

from typing import Dict, List, Any


def compute_feaci_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute FEACI metrics from experiment results.
    
    FEACI: Format, Explainability, Accuracy, Cost, Inference time
    
    Args:
        results: List of experiment results
        
    Returns:
        Dictionary of computed metrics
    """
    valid_results = [r for r in results if r.get('validation')]
    
    if not valid_results:
        return {
            'format_correctness': 0.0,
            'accuracy': 0.0,
            'cost_avg_tokens': 0,
            'inference_time_avg_seconds': 0.0,
            'num_results': 0
        }
    
    # Format correctness
    format_valid = sum(1 for r in valid_results if r['validation']['format_valid'])
    format_correctness = format_valid / len(valid_results) * 100
    
    # Accuracy
    overall_valid = sum(1 for r in valid_results if r['validation']['overall_valid'])
    accuracy = overall_valid / len(valid_results) * 100
    
    # Cost (tokens)
    total_tokens = sum(r['metrics']['tokens'] for r in valid_results)
    avg_tokens = total_tokens / len(valid_results)
    
    # Inference time
    total_time = sum(r['metrics']['time_seconds'] for r in valid_results)
    avg_time = total_time / len(valid_results)
    
    return {
        'format_correctness': format_correctness,
        'accuracy': accuracy,
        'cost_avg_tokens': avg_tokens,
        'cost_total_tokens': total_tokens,
        'inference_time_avg_seconds': avg_time,
        'inference_time_total_seconds': total_time,
        'num_results': len(valid_results)
    }


def print_feaci_metrics(metrics: Dict[str, Any]) -> None:
    """
    Pretty print FEACI metrics.
    
    Args:
        metrics: Metrics dictionary from compute_feaci_metrics
    """
    print("\n" + "="*80)
    print("FEACI METRICS")
    print("="*80)
    
    print(f"\nFormat Correctness: {metrics['format_correctness']:.1f}%")
    print(f"Overall Accuracy:   {metrics['accuracy']:.1f}%")
    print(f"Avg Tokens:         {metrics['cost_avg_tokens']:.0f}")
    print(f"Total Tokens:       {metrics.get('cost_total_tokens', 0):,}")
    print(f"Avg Inference Time: {metrics['inference_time_avg_seconds']:.1f}s")
    print(f"Total Time:         {metrics.get('inference_time_total_seconds', 0)/60:.1f} min")
    print(f"Results Processed:  {metrics['num_results']}")
    
    print("\n" + "="*80 + "\n")
