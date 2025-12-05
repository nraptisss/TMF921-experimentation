# Reproducibility Guide

> **How to exactly reproduce all results from the TMF921 Intent Translation project**

---

## Quick Reproducibility Check

Run this command to verify your setup matches our environment:

```bash
# Verify environment
python -c "
import sys
print(f'Python: {sys.version}')
import chromadb; print(f'ChromaDB: {chromadb.__version__}')
import pydantic; print(f'Pydantic: {pydantic.__version__}')
print('✓ Core dependencies OK')
"
```

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/nraptisss/TMF921-experimentation.git
cd TMF921-experimentation
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Ollama

```bash
# Install Ollama if needed (https://ollama.ai)
ollama serve

# Pull required model
ollama pull llama3:8b
```

### 5. Verify Setup

```bash
# Check Ollama connection
curl http://localhost:11434/api/tags

# Run quick test
python -c "
from tmf921.core import OllamaClient
client = OllamaClient(model='llama3:8b')
print('✓ Ollama connected')
"
```

---

## Reproducing Key Results

### Result 1: Validation Set (94.2%)

```bash
# Run full validation experiment
python scripts/evaluate_pipeline_with_icm.py

# Expected output:
# Overall Success Rate: 81/86 = 94.2%
```

**Expected Metrics:**
| Metric | Expected |
|--------|----------|
| Total Scenarios | 86 |
| Processing Success | 98.8% (85/86) |
| Validation Accuracy | 95.3% (81/85) |
| Overall Accuracy | 94.2% (81/86) |
| ICM Conversion | 100% |

### Result 2: Test Set (94.3%)

```bash
cd experiments
python run_final_test.py

# Expected output:
# Overall Success Rate: 82/87 = 94.3%
```

> ⚠️ **Warning**: Test set should only be run once to avoid data leakage.

### Result 3: Cross-Validation (94.0% ± 5.5%)

```bash
cd experiments
python cross_validation.py

# Expected output:
# Accuracy: 94.0% ± 5.5%
# Per-fold: [90%, 100%, 100%, 90%, 90%]
```

---

## Seed Configuration

All randomness is controlled via seeds for reproducibility.

### Data Splitting

```python
# In src/tmf921/utils/splitting.py
dataset.split(
    train_ratio=0.70,
    val_ratio=0.15,
    test_ratio=0.15,
    seed=42  # ← Fixed seed
)
```

### Cross-Validation

```python
# In experiments/cross_validation.py
kf = KFold(n_splits=5, shuffle=True, random_state=42)  # ← Fixed seed
```

### LLM Temperature

```python
# In experiments/base_experiment.py
response = self.client.generate(
    prompt=prompt,
    temperature=0.1,  # ← Near-deterministic
    top_p=0.9
)
```

---

## Checkpoint System

Experiments save checkpoints every 10 scenarios for recovery and verification.

### Checkpoint Files

```
results/<experiment_name>/
├── checkpoint_10.json       # First 10 results
├── checkpoint_10_icm.json   # ICM format
├── checkpoint_20.json
├── checkpoint_20_icm.json
├── ...
├── checkpoint_86.json       # Final results
├── checkpoint_86_icm.json   # Final ICM
└── metrics_summary.json     # Aggregated metrics
```

### Verifying Checkpoints

```python
import json

# Load checkpoint
with open('results/rag_cloud_86_scenarios/checkpoint_86.json') as f:
    results = json.load(f)

# Count successes
valid = sum(1 for r in results if r.get('validation', {}).get('overall_valid'))
print(f"Valid intents: {valid}/{len(results)}")
```

---

## Data Integrity

### Verify No Overlap

```python
import json

# Load all splits
with open('data/train.json') as f: train = set(json.load(f))
with open('data/val.json') as f: val = set(json.load(f))
with open('data/test.json') as f: test = set(json.load(f))

# Verify isolation
assert len(train & val) == 0, "Train/val overlap!"
assert len(train & test) == 0, "Train/test overlap!"
assert len(val & test) == 0, "Val/test overlap!"

print(f"✓ Train: {len(train)}")
print(f"✓ Val: {len(val)}")
print(f"✓ Test: {len(test)}")
print(f"✓ Total: {len(train) + len(val) + len(test)}")
print("✓ No overlap - data integrity verified")
```

### Verify Split Metadata

```python
import json

with open('data/split_metadata.json') as f:
    meta = json.load(f)

assert meta['total_scenarios'] == 574
assert meta['train_size'] == 401
assert meta['val_size'] == 86
assert meta['test_size'] == 87
assert meta['seed'] == 42
print("✓ Split metadata verified")
```

---

## Expected File Outputs

### After Full Evaluation

```
results/rag_cloud_86_scenarios/
├── checkpoint_10.json
├── checkpoint_10_icm.json
├── checkpoint_20.json
├── checkpoint_20_icm.json
├── checkpoint_30.json
├── checkpoint_30_icm.json
├── checkpoint_40.json
├── checkpoint_40_icm.json
├── checkpoint_50.json
├── checkpoint_50_icm.json
├── checkpoint_60.json
├── checkpoint_60_icm.json
├── checkpoint_70.json
├── checkpoint_70_icm.json
├── checkpoint_80.json
├── checkpoint_80_icm.json
├── checkpoint_86.json         # ~185 KB
├── checkpoint_86_icm.json     # ~417 KB
└── metrics_summary.json       # ~1 KB
```

---

## Version Pinning

### requirements.txt

```
chromadb>=0.4.0
pydantic>=2.0.0
tenacity>=8.0.0
requests>=2.28.0
numpy>=1.24.0
scikit-learn>=1.2.0
```

### Python Version

```
Python 3.10+ required
Tested on: Python 3.13.2
```

### Ollama Model

```
Model: llama3:8b
Alternative: llama3.1:8b (similar results)
```

---

## Troubleshooting

### Common Issues

**Issue: Ollama connection refused**
```bash
# Start Ollama
ollama serve

# Verify
curl http://localhost:11434/api/tags
```

**Issue: Different accuracy**
- Check model version (`llama3:8b` specifically)
- Verify temperature is 0.1
- Ensure using correct data split

**Issue: ICM files not created**
- Ensure `export_icm=True` is set
- Check recent version (v2.2.0+)

---

## Validation Checklist

Run this checklist to verify your reproduction:

```
[ ] Python 3.10+ installed
[ ] Virtual environment activated
[ ] requirements.txt installed
[ ] Ollama running with llama3:8b
[ ] Data files present (train.json, val.json, test.json)
[ ] GST specification present (gst.json)
[ ] ChromaDB index created (chroma_db/)
[ ] Quick validation passes (5 scenarios)
[ ] Full validation matches expected metrics
```

---

## Contact

If you cannot reproduce results:

1. Check the [CHANGELOG](../CHANGELOG.md) for version-specific notes
2. Verify all dependencies match requirements.txt
3. Open an issue with:
   - Python version
   - Ollama version and model
   - ChromaDB version
   - Error messages or unexpected outputs

---

**Last Updated:** 2025-12-05  
**Version:** 2.2.0
