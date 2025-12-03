# ICM Export - User Guide

**Feature:** Intent Common Model (ICM) JSON-LD Export  
**Version:** 2.2.0  
**Status:** Production Ready

---

## Overview

The ICM Export feature enables your TMF921 intent translation system to output intents in TM Forum's Intent Common Model (ICM) format alongside the standard simple JSON format.

### What is ICM?

ICM (Intent Common Model) is TM Forum's standard for representing network intents using semantic web technologies (JSON-LD). It provides:

- **Semantic structure** - Machine-readable intent representation
- **Industry standard** - TM Forum TMF921 v5.0.0 compliance
- **Interoperability** - Compatible with TM Forum systems
- **Rich semantics** - Explicit expectations, targets, conditions

### Why Use ICM Export?

✅ **TM Forum Compliance** - Meet industry standards  
✅ **System Interoperability** - Exchange intents with other systems  
✅ **Semantic Clarity** - Explicit expectations and conditions  
✅ **Future-proof** - Ready for semantic web integration  

### Key Benefit: Zero Risk

The ICM export is **completely optional** and has:
- ✅ No impact on existing accuracy (maintains 94.3%)
- ✅ No breaking changes
- ✅ Minimal performance overhead
- ✅ Automatic conversion

---

## Quick Start

### Enable ICM Export

Simply add `export_icm=True` when creating an experiment:

```python
from experiments.rag_cloud import RAGCloudExperiment

# Create experiment with ICM export enabled
exp = RAGCloudExperiment(
    model_name="llama3:8b",
    num_scenarios=10,
    export_icm=True  # ← Enable ICM export
)

exp.setup()
exp.run()
```

### Output

The experiment will save **both** formats:

```
results/rag_cloud_10_scenarios/
├── checkpoint_10.json         # Simple JSON (always)
├── checkpoint_10_icm.json     # ICM JSON-LD (new!)
└── metrics_summary.json       # Includes ICM stats
```

That's it! 🎉

---

## Usage Examples

### Example 1: Basic ICM Export

```python
from experiments.rag_cloud import RAGCloudExperiment

# Standard experiment with ICM export
exp = RAGCloudExperiment(
    model_name="llama3:8b",
    num_scenarios=50,
    export_icm=True
)

exp.setup()
exp.run()

# Check ICM conversion stats
import json
with open('results/rag_cloud_50_scenarios/metrics_summary.json') as f:
    metrics = json.load(f)
    
print(f"ICM Conversions: {metrics['icm_export']['successful_conversions']}")
print(f"Conversion Rate: {metrics['icm_export']['conversion_rate']*100}%")
```

### Example 2: Manual Conversion

Convert existing simple JSON to ICM:

```python
from src.tmf921.icm.converter import SimpleToICMConverter
import json

# Load existing simple intent
with open('my_intent_simple.json') as f:
    simple_intent = json.load(f)

# Convert to ICM
converter = SimpleToICMConverter()
icm_intent = converter.convert(simple_intent)

# Save ICM format
with open('my_intent_icm.json', 'w') as f:
    json.dump(icm_intent, f, indent=2)

print("✓ Converted to ICM format")
```

### Example 3: Batch Conversion

Convert multiple intents:

```python
from src.tmf921.icm.converter import SimpleToICMConverter
from pathlib import Path
import json

converter = SimpleToICMConverter()

# Process all simple JSON files
simple_dir = Path('results/simple_intents')
icm_dir = Path('results/icm_intents')
icm_dir.mkdir(exist_ok=True)

for simple_file in simple_dir.glob('*.json'):
    with open(simple_file) as f:
        simple_intent = json.load(f)
    
    icm_intent = converter.convert(simple_intent)
    
    icm_file = icm_dir / f"{simple_file.stem}_icm.json"
    with open(icm_file, 'w') as f:
        json.dump(icm_intent, f, indent=2)

print(f"✓ Converted {len(list(simple_dir.glob('*.json')))} intents")
```

---

## Output Formats

### Simple JSON Format

**Current format** - Optimized for LLM generation:

```json
{
  "name": "Gaming Network Slice",
  "description": "High-performance gaming slice",
  "serviceSpecCharacteristic": [
    {
      "name": "Delay tolerance",
      "value": {
        "value": "20",
        "unitOfMeasure": "ms"
      }
    }
  ]
}
```

**Characteristics:**
- Flat structure
- Direct name-value pairs
- Simple to parse
- Optimized for 94.3% accuracy

### ICM JSON-LD Format

**TM Forum format** - Semantic web compliant:

```json
{
  "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
  "@type": "icm:Intent",
  "@id": "#intent-1",
  "name": "Gaming Network Slice",
  "description": "High-performance gaming slice",
  "hasExpectation": [
    {
      "@type": "icm:PropertyExpectation",
      "@id": "#expectation-1",
      "target": {"@id": "#target-1"},
      "expectationCondition": {
        "@type": "log:Condition",
        "quan:smaller": {
          "property": "Delay",
          "value": {
            "@value": 20,
            "quan:unit": "ms"
          }
        }
      }
    }
  ],
  "target": [
    {
      "@id": "#target-1",
      "@type": "icm:Target",
      "resourceType": "NetworkSlice"
    }
  ]
}
```

**Characteristics:**
- Hierarchical structure
- Explicit expectations and targets
- Semantic operators (quan:, log:, set:)
- RDF-compatible

---

## Configuration

### Experiment Parameters

All experiments that inherit from `BaseExperiment` support ICM export:

```python
BaseExperiment(
    experiment_name="my_experiment",
    model_name="llama3:8b",
    num_scenarios=100,
    config_path="config.yaml",      # Optional
    results_dir="results",           # Optional
    export_icm=False                # Optional, default=False
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_icm` | bool | False | Enable ICM JSON-LD export |

### Enable by Default

To enable ICM export for all experiments, modify the experiment class:

```python
class MyExperiment(BaseExperiment):
    def __init__(self, **kwargs):
        # Enable ICM by default
        kwargs.setdefault('export_icm', True)
        super().__init__(**kwargs)
```

---

## Understanding Results

### Metrics Summary

When ICM export is enabled, `metrics_summary.json` includes:

```json
{
  "experiment": "rag_cloud_50_scenarios",
  "model": "llama3:8b",
  "honest_counts": {
    "total_scenarios": 50,
    "valid_intents": 47,
    "overall_success_rate": 0.94
  },
  "icm_export": {
    "enabled": true,
    "successful_conversions": 47,
    "conversion_rate": 1.0
  },
  "feaci": {...}
}
```

**ICM Metrics:**
- `enabled`: Whether ICM export was enabled
- `successful_conversions`: Number of intents successfully converted
- `conversion_rate`: Percentage of valid intents converted to ICM

### ICM Checkpoint Files

ICM checkpoints contain both formats:

```json
[
  {
    "scenario": "Create a gaming slice...",
    "generated_intent_simple": {...},  // Simple JSON
    "generated_intent_icm": {...},     // ICM JSON-LD
    "validation": {...},
    "metrics": {...}
  }
]
```

---

## Performance

### Conversion Overhead

ICM conversion has minimal performance impact:

| Metric | Value | Impact |
|--------|-------|--------|
| **Conversion time** | ~0.1ms per intent | Negligible |
| **File size increase** | ~2.5x | Manageable |
| **Accuracy impact** | 0% | None |
| **Success rate** | 100% | Reliable |

### Recommendations

✅ **Enable for production** - Minimal overhead  
✅ **Archive both formats** - Maximum flexibility  
✅ **Use simple for LLM** - Optimized accuracy  
✅ **Use ICM for export** - Standards compliance  

---

## Troubleshooting

### Issue: ICM checkpoint not created

**Symptoms:** Only `checkpoint_N.json` exists, no `checkpoint_N_icm.json`

**Solutions:**
1. Verify `export_icm=True` is set
2. Check for error messages during conversion
3. Ensure intents generated successfully

```python
# Check if ICM converter initialized
print(f"ICM Export: {exp.export_icm}")
print(f"Converter: {exp.icm_converter}")
```

### Issue: Conversion failures

**Symptoms:** Warning messages like "ICM conversion failed for result"

**Solutions:**
1. Check simple JSON is valid
2. Verify characteristics have proper structure
3. Review conversion logs

```python
# Manual conversion test
converter = SimpleToICMConverter()
try:
    icm = converter.convert(simple_intent)
    print("✓ Conversion successful")
except Exception as e:
    print(f"✗ Error: {e}")
```

### Issue: ICM metrics missing

**Symptoms:** No `icm_export` field in metrics_summary.json

**Solution:** ICM must be enabled when experiment runs

```python
# Correct
exp = RAGCloudExperiment(..., export_icm=True)
exp.run()  # ICM metrics will be included
```

---

## Best Practices

### 1. Default to Disabled

Keep `export_icm=False` for routine development:

```python
# Development/testing - simple JSON only
exp = RAGCloudExperiment(..., export_icm=False)
```

### 2. Enable for Production

Enable ICM for production runs and archival:

```python
# Production - dual format
exp = RAGCloudExperiment(..., export_icm=True)
```

### 3. Archive Both Formats

Store both formats for maximum interoperability:

```
archive/
├── 2025-12-03_experiment/
│   ├── simple/          # For LLM retraining
│   └── icm/             # For TM Forum systems
```

### 4. Monitor Conversion Rate

Aim for 100% conversion rate:

```python
# Check conversion success
if metrics['icm_export']['conversion_rate'] < 1.0:
    print("⚠ Some conversions failed - investigate")
```

---

## FAQ

**Q: Does ICM export affect accuracy?**  
A: No. LLM still generates simple JSON (94.3% accuracy). ICM is created by post-processing conversion.

**Q: Can I use ICM format with existing intents?**  
A: Yes! Use `SimpleToICMConverter` to convert any existing simple JSON intents.

**Q: What if conversion fails?**  
A: The simple JSON is always saved. ICM conversion failures are logged but don't stop the experiment.

**Q: Is ICM format larger?**  
A: Yes, ~2.5x larger due to semantic structure. This is manageable and expected.

**Q: Which format should I use?**  
A: Use simple JSON for LLM generation. Use ICM for TM Forum compliance and system interoperability.

**Q: Can I convert ICM back to simple?**  
A: Yes! Use `ICMToSimpleConverter` for reverse conversion.

---

## Next Steps

1. ✅ **Try it out** - Add `export_icm=True` to an experiment
2. ✅ **Check results** - Review both JSON and ICM outputs
3. ✅ **Read format guide** - See `docs/TMF921_FORMAT.md`
4. ✅ **Explore API** - See `docs/ICM_API_REFERENCE.md`

---

**Questions?** See the developer guide: `docs/ICM_DEVELOPER_GUIDE.md`
