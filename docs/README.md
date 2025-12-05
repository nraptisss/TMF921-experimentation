# TMF921 Documentation Hub

> **Complete documentation for the TMF921 Intent Translation Research Suite**

---

## Quick Navigation

| Category | Document | Description |
|----------|----------|-------------|
| 📖 **Getting Started** | [README](../README.md) | Project overview and quick start |
| 📖 **Getting Started** | [TUTORIAL](TUTORIAL.md) | Step-by-step tutorial |
| 🏗️ **Architecture** | [ARCHITECTURE](ARCHITECTURE.md) | System design and components |
| 🔬 **Pipeline** | [PIPELINE_WALKTHROUGH](PIPELINE_WALKTHROUGH.md) | Complete pipeline demo |
| 📊 **Data** | [DATASET](DATASET.md) | Dataset documentation |
| 📈 **Evaluation** | [METRICS](METRICS.md) | Metrics definitions |
| 🔄 **Reproducibility** | [REPRODUCIBILITY](REPRODUCIBILITY.md) | Reproducibility guide |
| 🧪 **Scientific** | [SCIENTIFIC_RIGOR](SCIENTIFIC_RIGOR_COMPLETE.md) | Scientific methodology |
| 🔧 **ICM Export** | [ICM_USER_GUIDE](ICM_USER_GUIDE.md) | ICM export usage |
| 🔧 **ICM Export** | [ICM_DEVELOPER_GUIDE](ICM_DEVELOPER_GUIDE.md) | ICM implementation |
| 🔧 **ICM Export** | [ICM_API_REFERENCE](ICM_API_REFERENCE.md) | ICM API docs |
| 📋 **Reference** | [TMF921_FORMAT](TMF921_FORMAT.md) | TMF921 format spec |
| 📋 **Reference** | [API](API.md) | Full API reference |

---

## Reading Order

### For New Users
1. **[README](../README.md)** - What this project does
2. **[TUTORIAL](TUTORIAL.md)** - Get started quickly
3. **[PIPELINE_WALKTHROUGH](PIPELINE_WALKTHROUGH.md)** - See how it works

### For Researchers
1. **[DATASET](DATASET.md)** - Understand the data
2. **[METRICS](METRICS.md)** - How we measure success
3. **[SCIENTIFIC_RIGOR](SCIENTIFIC_RIGOR_COMPLETE.md)** - Methodology
4. **[REPRODUCIBILITY](REPRODUCIBILITY.md)** - Reproduce our results

### For Developers
1. **[ARCHITECTURE](ARCHITECTURE.md)** - System design
2. **[API](API.md)** - API reference
3. **[ICM_DEVELOPER_GUIDE](ICM_DEVELOPER_GUIDE.md)** - ICM implementation

---

## Key Results (v2.2.0)

| Metric | Value | Dataset |
|--------|-------|---------|
| **Test Accuracy** | 94.3% | 87 scenarios (held-out) |
| **Validation Accuracy** | 94.2% | 86 scenarios |
| **ICM Conversion** | 100% | All processed intents |
| **Inference Time** | 2.1s avg | llama3:8b |

---

## Project Structure

```
TMF921-experimentation/
├── docs/                    # ← You are here
│   ├── README.md           # This file
│   ├── ARCHITECTURE.md     # System design
│   ├── PIPELINE_WALKTHROUGH.md
│   ├── DATASET.md          # Data documentation
│   ├── METRICS.md          # Evaluation metrics
│   ├── REPRODUCIBILITY.md  # Reproducibility
│   ├── ICM_*.md            # ICM documentation (3 files)
│   └── ...
├── src/tmf921/             # Core package
├── experiments/            # Experiment classes
├── scripts/                # Utility scripts
├── data/                   # Train/val/test splits
├── results/                # Experiment outputs
└── tests/                  # Unit tests
```

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| **2.2.0** | 2025-12-05 | ICM export, 94.2% validation |
| 2.1.0 | 2025-12-03 | Test set eval, 94.3% |
| 2.0.0 | 2025-11-25 | Scientific rigor, 574 scenarios |
| 1.0.0 | 2025-11-25 | Initial package release |

See [CHANGELOG](../CHANGELOG.md) for full details.

---

## Citation

```bibtex
@software{tmf921_intent_translation,
  title = {TMF921 Intent Translation using Lightweight LLMs},
  author = {Research Team},
  year = {2025},
  version = {2.2.0},
  url = {https://github.com/nraptisss/TMF921-experimentation}
}
```
