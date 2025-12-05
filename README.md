# TMF921 Intent Translation - Research Experimentation Suite

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Research Achievement:** 94.3% accuracy on held-out test set using RAG + Local LLM  
> **Scientific Rigor:** Publication-ready with statistical testing, cross-validation, and ablation studies  
> **TM Forum Compliance:** ICM JSON-LD export support (v2.2.0)

Professional research codebase for translating natural language network requirements into TMF921-compliant Intent JSON structures using lightweight LLMs with Retrieval-Augmented Generation (RAG).

## 🎯 Key Results

**Final Test Set Evaluation (87 held-out scenarios):**
- **94.3% accuracy** (82/87 valid intents)
- **100% processing success** (all scenarios generated valid JSON)
- **Model:** llama3:8b (local, 8B parameters)
- **Inference time:** 2.1s average per scenario
- **Zero corrections** needed (RAG provides exact characteristic names)

**Cross-Validation (5-fold, 50 scenarios):**
- **94.0% ± 5.5%** accuracy across folds
- **Coefficient of Variation:** 5.8% (good consistency)
- **Per-fold:** 90%, 100%, 100%, 90%, 90%

**Ablation Study Findings:**
- Baseline (zero-shot): 96.7%
- RAG + Name Correction: **100%** (perfect synergy)
- Few-shot examples: 0% (breaks the system - don't use!)

**Scientific Rigor:**
- 574 scenarios with proper train/val/test splits (401/86/87)
- Statistical testing framework (CI, p-values, effect sizes)
- K-fold cross-validation (94.0% ± 5.5%)
- Systematic ablation studies
- Human evaluation protocol
- Honest metrics reporting

**TM Forum Compliance (NEW in v2.2.0):**
- Intent Common Model (ICM) JSON-LD export
- TMF921 v5.0.0 specification compliance
- Dual-format support (Simple JSON + ICM)
- Backward compatible (optional feature)

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/tmf921-intent-translation.git
cd tmf921-intent-translation

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Running Experiments

```bash
# Run validation on 86 scenarios
python scripts/run_experiment.py --experiment rag_cloud --scenarios 86

# Run ablation study
python experiments/ablation_study.py
```
#### With ICM Export (NEW in v2.2.0)

Enable TM Forum Intent Common Model (ICM) JSON-LD export:

```python
from experiments.rag_cloud import RAGCloudExperiment

exp = RAGCloudExperiment(
    model_name="llama3:8b",
    num_scenarios=10,
    export_icm=True  # ← Enable ICM export
)

exp.setup()
exp.run()

# Results saved in both formats:
# - results/rag_cloud_10_scenarios/checkpoint_10.json (simple)
# - results/rag_cloud_10_scenarios/checkpoint_10_icm.json (ICM)
```

**Benefits:**
- ✅ TM Forum TMF921 v5.0.0 compliant
- ✅ Semantic JSON-LD format
- ✅ No impact on accuracy (maintains 94.3%)
- ✅ Automatic conversion
- ✅ Dual-format support

See [`docs/ICM_USER_GUIDE.md`](docs/ICM_USER_GUIDE.md) for details.

## 📖 Documentation

Complete documentation available in [`docs/`](docs/README.md):

| Category | Guide | Description |
|----------|-------|-------------|
| **Start** | [TUTORIAL](docs/TUTORIAL.md) | Step-by-step getting started |
| **Data** | [DATASET](docs/DATASET.md) | 574 scenarios, splits, categories |
| **Metrics** | [METRICS](docs/METRICS.md) | FEACI, honest counts, cross-validation |
| **Reproduce** | [REPRODUCIBILITY](docs/REPRODUCIBILITY.md) | Environment setup, verification |
| **Architecture** | [ARCHITECTURE](docs/ARCHITECTURE.md) | System design, pipeline flow |
| **ICM** | [ICM_USER_GUIDE](docs/ICM_USER_GUIDE.md) | TM Forum export |
| **API** | [API](docs/API.md) | Complete API reference |

### 4. Cross-Validation
python experiments/cross_validation.py

## 📊 Project Structure

```
tmf921-intent-translation/
├── src/tmf921/              # Core implementation
│   ├── core/                # Data, client, schema, validation
│   ├── prompting/           # Prompt templates and builders
│   ├── rag/                 # RAG indexer and retriever
│   ├── post_processing/     # Name correction
│   ├── utils/               # Statistics, splitting, metrics
│   └── evaluation/          # Error analysis, human eval
├── experiments/             # Experiment classes
│   ├── base_experiment.py   # Base experiment framework
│   ├── few_shot.py          # Few-shot learning (deprecated)
│   ├── rag_cloud.py         # RAG + Cloud (optimal)
│   ├── cross_validation.py  # K-fold CV
│   └── ablation_study.py    # Component ablation
├── scripts/                 # Utility scripts
│   ├── run_experiment.py    # Main experiment runner
│   ├── setup_rag.py         # Initialize RAG index
│   └── prepare_semantic_eval.py  # Human evaluation
├── data/                    # Dataset splits
│   ├── train.json           # 401 training scenarios
│   ├── val.json             # 86 validation scenarios
│   └── test.json            # 87 test scenarios (held-out)
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md      # System architecture  
│   ├── PIPELINE_WALKTHROUGH.md  # Complete pipeline demo
│   ├── SCIENTIFIC_RIGOR_COMPLETE.md
│   ├── SEMANTIC_EVALUATION_GUIDE.md
│   ├── TMF921_FORMAT.md     # TMF921 ICM format specification
│   ├── ICM_USER_GUIDE.md    # ICM export user guide (NEW)
│   ├── ICM_DEVELOPER_GUIDE.md  # ICM developer guide (NEW)
│   ├── ICM_API_REFERENCE.md    # ICM API reference (NEW)
│   └── PHASE_1_2_COMPLETE.md
└── results/                 # Experiment results


## Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Setup (One-time)

**For RAG experiments:**
```powershell
python scripts/setup_rag.py
```

**Sign into Ollama Cloud (for cloud experiments):**
```powershell
ollama signin
ollama pull gpt-oss:20b-cloud
```

### 3. Run Experiments

**List available experiments:**
```powershell
python scripts/run_experiment.py --list
```

**Run few-shot experiment:**
```powershell
python scripts/run_experiment.py --experiment few_shot --scenarios 10
```

**Run RAG + Cloud experiment:**
```powershell
python scripts/run_experiment.py --experiment rag_cloud --scenarios 50
```

### 4. Analyze Results

**View single experiment results:**
```powershell
python scripts/analyze_results.py --experiment few_shot_10_scenarios
```

**Compare multiple experiments:**
```powershell
python scripts/analyze_results.py --compare few_shot_10_scenarios rag_cloud_50_scenarios
```

**List all results:**
```powershell
python scripts/analyze_results.py --list
```

## Project Structure

```
.
├── src/tmf921/              # Main package
│   ├── core/                # Core functionality
│   │   ├── data_processor.py
│   │   ├── schema.py
│   │   └── client.py
│   ├── prompting/           # Prompt engineering
│   │   └── templates.py
│   ├── rag/                 # RAG components
│   │   ├── indexer.py
│   │   └── retriever.py
│   ├── post_processing/     # Post-processing
│   │   └── name_mapper.py
│   └── utils/               # Utilities
│       ├── config.py
│       └── metrics.py
│
├── experiments/             # Experiment implementations
│   ├── base_experiment.py
│   ├── few_shot.py
│   └── rag_cloud.py
│
├── scripts/                 # Utility scripts
│   ├── run_experiment.py   # Unified runner
│   ├── analyze_results.py  # Results analysis
│   └── setup_rag.py        # RAG setup
│
├── data/                    # Data files
├── results/                 # Experiment results
└── config.yaml              # Configuration

```

## Available Experiments

### 1. Few-Shot Learning
Uses example scenarios to guide the LLM.

```powershell
python scripts/run_experiment.py --experiment few_shot --scenarios 10 --examples 3
```

- Default model: `llama3:latest`
- Accuracy: ~70%
- Speed: ~31s/scenario

### 2. RAG + Cloud
RAG retrieval with Ollama Cloud model for best accuracy and speed.

```powershell
python scripts/run_experiment.py --experiment rag_cloud --scenarios 50
```

- Default model: `gpt-oss:20b-cloud`
- Accuracy: ~100%
- Speed: ~12s/scenario (7x faster than local)

## Results

All experiment results are saved to `results/<experiment_name>/`:
- `metrics_summary.json` - FEACI metrics
- `all_results.json` - Full results
- `checkpoint_N.json` - Checkpoints every 10 scenarios

## FEACI Metrics

- **Format Correctness**: % of valid TMF921 JSON
- **Accuracy**: % of overall valid intents
- **Cost**: Token usage
- **Inference Time**: Generation speed

## Research Achievement

✅ **100% Accuracy** on 50 scenarios with RAG + Cloud  
✅ **7x Speedup** using cloud models  
✅ **Zero Corrections** needed with proper RAG retrieval

## Configuration

Edit `config.yaml` to:
- Add new models
- Adjust model parameters
- Configure experiments

## Development

The codebase is modular and extensible:

1. **Add new experiments**: Create class in `experiments/` inheriting from `BaseExperiment`
2. **Add new models**: Update `config.yaml` and `src/tmf921/core/client.py`
3. **Customize prompts**: Edit `src/tmf921/prompting/templates.py`

## Citation

If you use this codebase in your research, please cite:

```
TMF921 Intent Translation using Lightweight LLMs
Research Experimentation Suite v1.0
2025
```

## License

Research use only.
