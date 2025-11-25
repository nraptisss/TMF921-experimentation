# TMF921 Intent Translation - Research Experimentation Suite

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Research Achievement:** 100% accuracy on TMF921 intent translation using RAG + Cloud LLMs

Professional research codebase for translating natural language network requirements into TMF921-compliant Intent JSON structures using lightweight LLMs.

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
