# Deprecated Scripts Archive

This directory contains old experimental scripts that have been replaced by the new modular framework.

## Migration Guide

| Old Script | New Command |
|------------|-------------|
| `quick_validation.py` | `python scripts/run_experiment.py --experiment few_shot --scenarios 10` |
| `few_shot_validation.py` | `python scripts/run_experiment.py --experiment few_shot --scenarios 10` |
| `validation_50.py` | `python scripts/run_experiment.py --experiment few_shot --scenarios 50` |
| `rag_validation.py` | `python scripts/run_experiment.py --experiment rag_cloud --scenarios 10` |
| `rag_validation_50.py` | `python scripts/run_experiment.py --experiment rag_cloud --scenarios 50` |
| `rag_validation_50_cloud.py` | `python scripts/run_experiment.py --experiment rag_cloud --scenarios 50` |
| `test_cloud_model.py` | Use `interactive_testing.ipynb` |
| `analyze_results.py` | `python scripts/analyze_results.py` |
| `compare_results.py` | `python scripts/analyze_results.py --compare` |

## Why These Were Deprecated

1. **Duplicate Code:** Each script had similar validation logic
2. **Hard to Maintain:** Changes needed in multiple files
3. **No Unified Interface:** Hard to discover available experiments
4. **Limited Extensibility:** Required full script duplication for new experiments

## New Framework Benefits

1. **Single Entry Point:** `scripts/run_experiment.py`
2. **Modular Design:** Clear separation of concerns
3. **Easy Extension:** Inherit from `BaseExperiment`
4. **Better Testing:** Interactive notebook for experimentation

## Preserved Functionality

All functionality from these scripts is preserved in the new framework:
- ✅ Same FEACI metrics
- ✅ Same validation logic
- ✅ Same checkpoint saving
- ✅ Identical results

## If You Need Old Scripts

These files are kept for reference only. For production use, please migrate to the new framework as shown in the table above.
