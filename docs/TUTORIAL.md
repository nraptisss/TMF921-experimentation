# Getting Started Tutorial

Welcome to the TMF921 Intent Translation system! This tutorial will guide you through using the system.

## Prerequisites

1. **Python 3.11+** installed
2. **Ollama** running locally
3. Basic understanding of LLMs

## Installation

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `ollama` - LLM client
- `pydantic` - Data validation
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings
- `pyyaml` - Configuration
- And more...

### 2. Setup Ollama

**For local models:**
```powershell
ollama pull llama3:latest
```

**For cloud models (recommended):**
```powershell
ollama signin
ollama pull gpt-oss:20b-cloud
```

### 3. Setup RAG (Optional but Recommended)

```powershell
python scripts/setup_rag.py
```

This indexes the 87 GST characteristics for retrieval.

---

## Quick Start

### Option 1: Command Line

**List available experiments:**
```powershell
python scripts/run_experiment.py --list
```

**Run few-shot experiment:**
```powershell
python scripts/run_experiment.py --experiment few_shot --scenarios 10
```

**Run RAG + Cloud (best results):**
```powershell
python scripts/run_experiment.py --experiment rag_cloud --scenarios 50
```

### Option 2: Interactive Notebook

```powershell
jupyter notebook interactive_testing.ipynb
```

Open the notebook and run cells interactively.

### Option 3: Python API

```python
from experiments.rag_cloud import RAGCloudExperiment

exp = RAGCloudExperiment(
    model_name="gpt-oss:20b-cloud",
    num_scenarios=10
)
exp.setup()
exp.run()
```

---

## Tutorial: Step by Step

### Step 1: Test Single Scenario

```python
import sys
from pathlib import Path
sys.path.insert(0, "src")

from tmf921 import (
    GSTSpecification, TMF921Validator, OllamaClient,
    TMF921PromptBuilder, EXAMPLE_SCENARIOS
)

# Load GST
gst = GSTSpecification("gst.json")

# Initialize components
validator = TMF921Validator(gst.spec)
prompt_builder = TMF921PromptBuilder(gst.spec)
client = OllamaClient(model="gpt-oss:20b-cloud")

# Test scenario
scenario = "Deploy IoT network: 1 Mbps, 500ms latency, 99.9% uptime."

# Build prompt
system_prompt = prompt_builder.build_system_prompt()
user_prompt = prompt_builder.build_few_shot_prompt(
    scenario,
    EXAMPLE_SCENARIOS[:3],
    max_examples=3
)

# Generate
response = client.generate(
    prompt=user_prompt,
    system_prompt=system_prompt
)

# Extract and validate
intent = client.extract_json(response['response'])
validation = validator.validate_all(intent)

print(f"Valid: {validation['overall_valid']}")
```

### Step 2: Run Full Experiment

```powershell
python scripts/run_experiment.py --experiment rag_cloud --scenarios 50
```

Results saved to `results/rag_cloud_50_scenarios/`

### Step 3: Analyze Results

```powershell
python scripts/analyze_results.py --experiment rag_cloud_50_scenarios
```

Output:
```
Experiment: rag_cloud_50_scenarios
Model: gpt-oss:20b-cloud
Accuracy: 100.0%
Avg Time: 11.9s
```

### Step 4: Compare Experiments

```powershell
python scripts/analyze_results.py --compare validation_50 rag_cloud_50_scenarios
```

---

## Common Workflows

### Workflow 1: Test New Model

1. Add model to `config.yaml`:
```yaml
models:
  ollama:
    models:
      - name: "new-model:latest"
        alias: "new-model"
        parameters:
          temperature: 0.1
```

2. Run experiment:
```powershell
python scripts/run_experiment.py --experiment few_shot --model new-model:latest --scenarios 10
```

### Workflow 2: Create Custom Experiment

1. Create `experiments/my_experiment.py`:
```python
from base_experiment import BaseExperiment

class MyExperiment(BaseExperiment):
    def build_prompt(self, scenario):
        # Your custom prompt logic
        return system_prompt, user_prompt
```

2. Register in `scripts/run_experiment.py`

3. Run:
```powershell
python scripts/run_experiment.py --experiment my_experiment
```

### Workflow 3: Batch Processing

```python
from tmf921 import ScenarioDataset

# Load all scenarios
dataset = ScenarioDataset("scenarios.json")

# Process in batches
for batch in chunks(dataset.scenarios, 100):
    process_batch(batch)
```

---

## Configuration

Edit `config.yaml` to customize:

```yaml
# Model settings
models:
  ollama:
    models:
      - name: "gpt-oss:20b-cloud"
        temperature: 0.1
        max_tokens: 4096

# Experiment settings
experiments:
  few_shot:
    num_examples: [1, 3, 5]
  
  rag:
    top_k_retrieval: 8
```

---

## Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```powershell
# Start Ollama
ollama serve

# Check status
ollama list
```

### Issue: "RAG not available"

**Solution:**
```powershell
python scripts/setup_rag.py
```

### Issue: "Model not found"

**Solution:**
```powershell
ollama pull gpt-oss:20b-cloud
```

### Issue: "Unicode errors on Windows"

**Solution:**  
This is a Windows console encoding issue. Already handled in code.

---

## Next Steps

1. **Try the notebook:** `jupyter notebook interactive_testing.ipynb`
2. **Read API docs:** `docs/API.md`
3. **Explore architecture:** `docs/ARCHITECTURE.md`
4. **Run experiments:** Compare different approaches
5. **Extend the system:** Add new experiments

---

## Best Practices

1. **Start small:** Test with 10 scenarios before running 50
2. **Use cloud models:** Much faster for experiments
3. **Enable RAG:** Significantly improves accuracy
4. **Save checkpoints:** Experiment runner does this automatically
5. **Compare results:** Use analysis tools to track improvements

---

## Support

- **Documentation:** See `docs/` directory
- **Examples:** See `interactive_testing.ipynb`
- **Issues:** Check existing experiment results for patterns

---

## Performance Expectations

| Configuration | Accuracy | Speed | Use Case |
|--------------|----------|-------|----------|
| Zero-shot + local | 20% | 90s | Baseline |
| Few-shot + local | 70% | 31s | Development |
| Few-shot + cloud | 80% | 12s | Fast iteration |
| RAG + cloud | 100% | 12s | Production |

**Recommendation:** Use RAG + Cloud (gpt-oss:20b-cloud) for best results.
