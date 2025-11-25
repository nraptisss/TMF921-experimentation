"""
Statistical testing and analysis utilities for scientific rigor.
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StatisticalTestResult:
    """Result of a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    effect_size: Optional[float] = None
    interpretation: Optional[str] = None


def mcnemar_test(
    results_a: List[bool],
    results_b: List[bool],
    alpha: float = 0.05
) -> StatisticalTestResult:
    """
    McNemar's test for paired binary classifiers.
    
    Tests if accuracy difference between two approaches is statistically significant.
    
    Args:
        results_a: List of True/False for approach A (correct/incorrect)
        results_b: List of True/False for approach B (correct/incorrect)
        alpha: Significance level (default 0.05)
        
    Returns:
        StatisticalTestResult with test details
        
    Example:
        >>> few_shot_results = [True, True, False, True, ...]
        >>> rag_results = [True, True, True, True, ...]
        >>> result = mcnemar_test(few_shot_results, rag_results)
        >>> print(f"Significant improvement: {result.significant}")
    """
    assert len(results_a) == len(results_b), "Result lists must have same length"
    
    # Create contingency table
    #       B_correct  B_wrong
    # A_correct    a       b
    # A_wrong      c       d
    
    a = sum(1 for i in range(len(results_a)) if results_a[i] and results_b[i])
    b = sum(1 for i in range(len(results_a)) if results_a[i] and not results_b[i])
    c = sum(1 for i in range(len(results_a)) if not results_a[i] and results_b[i])
    d = sum(1 for i in range(len(results_a)) if not results_a[i] and not results_b[i])
    
    # McNemar's test with continuity correction
    # Only consider discordant pairs (b and c)
    if b + c == 0:
        # No discordant pairs - methods agree completely
        return StatisticalTestResult(
            test_name="McNemar's Test",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            interpretation="Methods have identical performance"
        )
    
    # Chi-square statistic with continuity correction
    statistic = (abs(b - c) - 1) ** 2 / (b + c)
    p_value = 1 - stats.chi2.cdf(statistic, df=1)
    
    # Effect size (odds ratio)
    if c > 0:
        odds_ratio = b / c
    else:
        odds_ratio = float('inf') if b > 0 else 1.0
    
    return StatisticalTestResult(
        test_name="McNemar's Test",
        statistic=statistic,
        p_value=p_value,
        significant=p_value < alpha,
        effect_size=odds_ratio,
        interpretation=f"B is better" if c > b else f"A is better" if b > c else "Equal"
    )


def confidence_interval(
    values: List[float],
    confidence_level: float = 0.95
) -> Tuple[float, float]:
    """
    Compute confidence interval using t-distribution.
    
    Args:
        values: List of values (e.g., accuracies from different folds)
        confidence_level: Confidence level (default 0.95 for 95% CI)
        
    Returns:
        (lower_bound, upper_bound)
    """
    if len(values) < 2:
        return (values[0] if values else 0, values[0] if values else 0)
    
    mean = np.mean(values)
    std_err = stats.sem(values)
    
    ci = stats.t.interval(
        confidence_level,
        len(values) - 1,
        loc=mean,
        scale=std_err
    )
    
    return ci


def bootstrap_confidence_interval(
    results: List[bool],
    n_bootstrap: int = 1000,
    confidence_level: float = 0.95
) -> Tuple[float, float]:
    """
    Bootstrap confidence interval for binary accuracy.
    
    More robust for smaller samples (<30).
    
    Args:
        results: List of True/False (correct/incorrect)
        n_bootstrap: Number of bootstrap samples
        confidence_level: Confidence level (default 0.95)
        
    Returns:
        (lower_bound, upper_bound) in range [0, 1]
    """
    accuracies = []
    
    np.random.seed(42)  # Reproducibility
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        sample = np.random.choice(results, size=len(results), replace=True)
        accuracies.append(np.mean(sample))
    
    # Compute percentiles
    alpha = 1 - confidence_level
    lower = np.percentile(accuracies, alpha/2 * 100)
    upper = np.percentile(accuracies, (1 - alpha/2) * 100)
    
    return (lower, upper)


def paired_t_test(
    values_a: List[float],
    values_b: List[float],
    alpha: float = 0.05
) -> StatisticalTestResult:
    """
    Paired t-test for comparing two approaches on same data.
    
    Args:
        values_a: Metric values from approach A
        values_b: Metric values from approach B
        alpha: Significance level
        
    Returns:
        StatisticalTestResult
    """
    assert len(values_a) == len(values_b), "Must have same length"
    
    statistic, p_value = stats.ttest_rel(values_a, values_b)
    
    # Cohen's d effect size
    diff = np.array(values_a) - np.array(values_b)
    cohens_d = np.mean(diff) / np.std(diff, ddof=1)
    
    return StatisticalTestResult(
        test_name="Paired t-test",
        statistic=statistic,
        p_value=p_value,
        significant=p_value < alpha,
        effect_size=cohens_d,
        interpretation=interpret_cohens_d(cohens_d)
    )


def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "Negligible effect"
    elif abs_d < 0.5:
        return "Small effect"
    elif abs_d < 0.8:
        return "Medium effect"
    else:
        return "Large effect"


def compute_accuracy_with_ci(
    results: List[bool],
    confidence_level: float = 0.95,
    use_bootstrap: bool = None
) -> Dict:
    """
    Compute accuracy with confidence interval.
    
    Args:
        results: List of True/False
        confidence_level: Confidence level (default 95%)
        use_bootstrap: Force bootstrap (None = auto-detect based on sample size)
        
    Returns:
        {
            'accuracy': float (0-100),
            'ci_lower': float (0-100),
            'ci_upper': float (0-100),
            'std_error': float,
            'n': int,
            'method': str
        }
    """
    accuracy = np.mean(results)
    n = len(results)
    
    # Auto-detect: use bootstrap for small samples
    if use_bootstrap is None:
        use_bootstrap = n < 30
    
    if use_bootstrap:
        ci_lower, ci_upper = bootstrap_confidence_interval(results, confidence_level=confidence_level)
        method = "bootstrap"
        std_error = np.std([np.mean(np.random.choice(results, len(results), replace=True)) 
                           for _ in range(100)])
    else:
        ci_lower, ci_upper = confidence_interval([float(r) for r in results], confidence_level)
        method = "t-distribution"
        std_error = stats.sem([float(r) for r in results])
    
    return {
        'accuracy': accuracy * 100,
        'ci_lower': ci_lower * 100,
        'ci_upper': ci_upper * 100,
        'std_error': std_error * 100,
        'n': n,
        'method': method,
        'confidence_level': confidence_level
    }


def print_statistical_comparison(
    name_a: str,
    results_a: List[bool],
    name_b: str,
    results_b: List[bool]
):
    """
    Print comprehensive statistical comparison between two approaches.
    
    Args:
        name_a: Name of approach A
        results_a: Results from approach A
        name_b: Name of approach B
        results_b: Results from approach B
    """
    print("\n" + "="*80)
    print("STATISTICAL COMPARISON")
    print("="*80)
    
    # Accuracies with CIs
    stats_a = compute_accuracy_with_ci(results_a)
    stats_b = compute_accuracy_with_ci(results_b)
    
    print(f"\n{name_a}:")
    print(f"  Accuracy: {stats_a['accuracy']:.1f}% (95% CI: [{stats_a['ci_lower']:.1f}%, {stats_a['ci_upper']:.1f}%])")
    print(f"  ±{stats_a['std_error']:.2f}% SE, n={stats_a['n']}")
    
    print(f"\n{name_b}:")
    print(f"  Accuracy: {stats_b['accuracy']:.1f}% (95% CI: [{stats_b['ci_lower']:.1f}%, {stats_b['ci_upper']:.1f}%])")
    print(f"  ±{stats_b['std_error']:.2f}% SE, n={stats_b['n']}")
    
    # Statistical test
    mcnemar_result = mcnemar_test(results_a, results_b)
    
    print(f"\nMcNemar's Test:")
    print(f"  χ² statistic: {mcnemar_result.statistic:.3f}")
    print(f"  p-value: {mcnemar_result.p_value:.4f}")
    print(f"  Significant (α=0.05): {'YES' if mcnemar_result.significant else 'NO'}")
    
    if mcnemar_result.effect_size:
        print(f"  Odds ratio: {mcnemar_result.effect_size:.2f}")
    
    print(f"  Interpretation: {mcnemar_result.interpretation}")
    
    # Improvement
    improvement = stats_b['accuracy'] - stats_a['accuracy']
    print(f"\nImprovement: {improvement:+.1f}%")
    
    if mcnemar_result.significant:
        print("  [SIGNIFICANT] Improvement is statistically significant")
    else:
        print("  [NOT SIGNIFICANT] Improvement could be due to chance")
    
    print("\n" + "="*80)


# Example usage
if __name__ == "__main__":
    # Example: Compare few-shot vs RAG
    few_shot = [True] * 80 + [False] * 20  # 80% accuracy
    rag = [True] * 95 + [False] * 5  # 95% accuracy
    
    print_statistical_comparison(
        "Few-Shot Learning",
        few_shot,
        "RAG + Cloud",
        rag
    )
