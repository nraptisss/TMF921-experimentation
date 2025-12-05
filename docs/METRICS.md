# Evaluation Metrics Documentation

> **Complete guide to all metrics used in TMF921 Intent Translation evaluation**

---

## Overview

This project uses a multi-layered metrics framework to honestly and comprehensively evaluate intent translation performance.

### Metrics Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          HONEST COUNTS                                  │
│  Total Scenarios → Processing Success → Validation Success → Overall   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FEACI METRICS                                  │
│  Format • Explainability • Accuracy • Cost • Inference Time            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STATISTICAL MEASURES                                │
│  Cross-Validation • Confidence Intervals • Effect Sizes                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Honest Counts

**Philosophy**: Report what actually happens, not just best-case scenarios.

### Metrics Breakdown

| Metric | Formula | Description |
|--------|---------|-------------|
| **Total Scenarios** | N | Input count |
| **Processing Failures** | Failed JSON extraction | LLM output not parseable |
| **Processing Success Rate** | (N - Failures) / N | % of valid JSON outputs |
| **Valid Intents** | Pass all validation | Schema + characteristic valid |
| **Validation Success Rate** | Valid / Processed | % of parsed that validate |
| **Overall Success Rate** | Valid / N | True end-to-end success |

### Example (v2.2.0 Run)

```
Total Scenarios:        86
Processing Failures:     1 (1.2%)
Successfully Processed: 85 (98.8%)
Valid Intents:          81 (95.3% of processed)

**Overall Success Rate: 81/86 = 94.2%**
```

### Why "Honest Counts" Matter

Traditional reporting often shows only `Valid / Processed`, hiding extraction failures. Our approach:

```
              Traditional                      Honest
              ───────────                      ──────
              "95.3% accuracy"                 "94.2% overall"
                                               ├─ 98.8% processing
                                               └─ 95.3% validation
```

---

## FEACI Metrics

### Definition

**F**ormat · **E**xplainability · **A**ccuracy · **C**ost · **I**nference time

| Metric | Target | Description |
|--------|--------|-------------|
| **Format Correctness** | 100% | Valid TMF921 JSON structure |
| **Accuracy** | >90% | Valid + correct characteristics |
| **Cost (Tokens)** | <2000 avg | Token usage per scenario |
| **Inference Time** | <5s | LLM generation time |

### Computation

```python
from tmf921.utils import compute_feaci_metrics

results = [...]  # Experiment results
feaci = compute_feaci_metrics(results)

# Returns:
{
    'format_correctness': 100.0,      # % valid JSON format
    'accuracy': 95.3,                 # % overall valid
    'cost_avg_tokens': 1530,          # Tokens per scenario
    'cost_total_tokens': 130022,      # Total tokens
    'inference_time_avg_seconds': 2.1,# Avg time
    'inference_time_total_seconds': 180.2,
    'num_results': 85
}
```

### Current Results (v2.2.0)

| Metric | Value | Status |
|--------|-------|--------|
| Format Correctness | 100.0% | ✅ Excellent |
| Accuracy | 95.3% | ✅ Excellent |
| Avg Tokens | 1,530 | ✅ Good |
| Avg Time | 2.1s | ✅ Fast |

---

## Validation Layers

### Three-Stage Validation

```
Raw LLM Output
      │
      ▼
┌─────────────────────────────────────┐
│  Stage 1: FORMAT VALIDATION         │
│  - Has 'name' field?                │
│  - Has 'description' field?         │
│  - Has 'serviceSpecCharacteristic'? │
│  - Is it a valid list?              │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│  Stage 2: CHARACTERISTIC VALIDATION │
│  - Does each char have 'name'?      │
│  - Does each char have 'value'?     │
│  - Is name in GST specification?    │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│  Stage 3: PLAUSIBILITY CHECKING     │
│  - Latency: 0.1ms - 10,000ms?       │
│  - Bandwidth: reasonable range?     │
│  - Availability: 0-100%?            │
└─────────────────────────────────────┘
      │
      ▼
   VALIDATED
```

### Validation Result Structure

```python
{
    'format_valid': True,           # Stage 1 passed
    'characteristics_valid': True,  # Stage 2 passed
    'plausibility_valid': True,     # Stage 3 passed
    'errors': [],                   # Hard failures
    'warnings': [],                 # Soft issues
    'overall_valid': True           # AND of all stages
}
```

---

## Cross-Validation Metrics

### K-Fold Cross-Validation

We use **5-fold cross-validation** to assess model stability.

```
Dataset: 86 validation scenarios
         ┌──────────────────────────────────────────────┐
Fold 1:  │████████████████████ TEST │ TRAIN TRAIN TRAIN│
Fold 2:  │TRAIN │████████████████████ TEST │TRAIN TRAIN│
Fold 3:  │TRAIN TRAIN │████████████████████ TEST │TRAIN│
Fold 4:  │TRAIN TRAIN TRAIN │████████████████████ TEST │
Fold 5:  │████████████████████ TEST │TRAIN TRAIN TRAIN │
         └──────────────────────────────────────────────┘
```

### Cross-Validation Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Mean Accuracy** | 94.0% | Average across folds |
| **Std Deviation** | ±5.5% | Variance measure |
| **Coef. of Variation** | 5.8% | Stability indicator |

### Per-Fold Performance

| Fold | Accuracy | Status |
|------|----------|--------|
| 1 | 90% | ⚠️ Slightly lower |
| 2 | 100% | ✅ Perfect |
| 3 | 100% | ✅ Perfect |
| 4 | 90% | ⚠️ Slightly lower |
| 5 | 90% | ⚠️ Slightly lower |

**Interpretation**: CV < 10% indicates good consistency.

---

## Statistical Measures

### Confidence Intervals

```python
from tmf921.utils.statistics import compute_confidence_interval

# Bootstrap confidence interval
ci_lower, ci_upper = compute_confidence_interval(
    accuracies,
    confidence=0.95
)
# Example: 94.2% (89.1% - 98.7%)
```

### Effect Size

```python
from tmf921.utils.statistics import compute_effect_size

# Compare two approaches
effect = compute_effect_size(
    baseline_results,
    improved_results
)
# Cohen's d interpretation:
# < 0.2: negligible
# 0.2-0.5: small
# 0.5-0.8: medium
# > 0.8: large
```

---

## ICM Conversion Metrics

### ICM Export Statistics

| Metric | Value | Description |
|--------|-------|-------------|
| **Conversion Rate** | 100% | % of intents converted to ICM |
| **Format Compliance** | 100% | Valid JSON-LD structure |
| **Context Present** | 100% | @context URL present |
| **Type Correct** | 100% | @type = "icm:Intent" |

### ICM Metrics in Results

```json
{
  "icm_export": {
    "enabled": true,
    "successful_conversions": 85,
    "conversion_rate": 1.0
  }
}
```

---

## Name Correction Metrics

### Fuzzy Matching Statistics

| Metric | Description |
|--------|-------------|
| **Total Corrections** | Number of name corrections made |
| **Correction Rate** | Corrections / Total characteristics |
| **Match Threshold** | 0.6 similarity (configurable) |

### Example

```
Total characteristics: 340 (across 85 intents)
Corrections needed: 12
Correction rate: 3.5%

Examples:
- "E2E latency" → "Delay tolerance"
- "Bandwidth" → "Downlink throughput per network slice..."
```

---

## Ablation Study Metrics

### Component Contribution

| Configuration | Accuracy | Delta |
|---------------|----------|-------|
| Baseline (zero-shot) | 96.7% | - |
| + RAG | 100% | +3.3% |
| + Name Correction | 100% | +0% (no additional) |
| + Few-shot examples | 0% | -100% (breaks!) |

### Key Finding

**RAG is essential**: +3.3% accuracy improvement  
**Few-shot examples are harmful**: Causes 100% failure

---

## Results File Format

### metrics_summary.json

```json
{
  "experiment": "rag_cloud_86_scenarios",
  "model": "llama3:8b",
  "honest_counts": {
    "total_scenarios": 86,
    "processing_failures": 1,
    "processing_failure_rate": 0.0116,
    "successfully_processed": 85,
    "processing_success_rate": 0.9884,
    "valid_intents": 81,
    "validation_success_rate_on_processed": 0.9529,
    "overall_success_rate": 0.9419
  },
  "num_corrections": 12,
  "feaci": {
    "format_correctness": 100.0,
    "accuracy": 95.29,
    "cost_avg_tokens": 1530,
    "cost_total_tokens": 130022,
    "inference_time_avg_seconds": 2.12,
    "inference_time_total_seconds": 180.24,
    "num_results": 85
  },
  "icm_export": {
    "enabled": true,
    "successful_conversions": 85,
    "conversion_rate": 1.0
  },
  "timestamp": "2025-12-05T08:31:01"
}
```

---

## Visualization

### Accuracy Over Time

```
Accuracy (%)
100 ┤                    ┌─────── v2.0.0: RAG + Cloud
 95 ┤              ┌─────┘ 
 90 ┤        ┌─────┘
 85 ┤   ┌────┘              
 80 ┤───┘                   ← v0.2.0: Few-shot
 70 ┤
 60 ┤
    └────────────────────────────────────────────────
      v0.1  v0.2  v1.0  v2.0  v2.1  v2.2   Version
```

### Processing Pipeline Success

```
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Input (86)
     │
98.8%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Processed (85)
     │
94.2%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Valid (81)
     │
94.2%━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ICM Converted (81)
```

---

## Comparison with Baselines

### Model Comparison

| Model | Accuracy | Time | Tokens |
|-------|----------|------|--------|
| **llama3:8b** | 94.2% | 2.1s | 1,530 |
| gpt-oss:20b-cloud | 95.3% | 1.8s | 1,450 |
| phi3.5:3.8b | ~85% | 1.5s | 1,200 |

### Approach Comparison

| Approach | Accuracy | Notes |
|----------|----------|-------|
| Zero-shot | ~20% | No context |
| Few-shot | 0% | Breaks system |
| RAG (current) | 94%+ | Best approach |

---

**Last Updated:** 2025-12-05  
**Version:** 2.2.0
