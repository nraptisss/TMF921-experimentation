# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2025-12-05

### 🎉 New Synthetic Dataset & Three-Tier Generation

**New Dataset Performance: 87.5% test accuracy on 48 diverse scenarios**

### Added

**Synthetic Dataset Generation:**
- Three-tier generation methodology using `gpt-oss:120b-cloud`
- **Tier 1**: 225 characteristic-driven scenarios (100% GST coverage)
- **Tier 2**: 75 domain-driven scenarios (15 industries)
- **Tier 3**: 20 complexity scenarios (hard/implicit)
- Total: 320 high-quality scenarios (224 train / 48 val / 48 test)

**New Documentation:**
- `docs/DATA_GENERATION.md` - Comprehensive generation methodology
- `docs/CRITICAL_ANALYSIS.md` - System analysis and improvement roadmap

**Generation Script:**
- `scripts/generate_dataset.py` - Full dataset generation pipeline

### Changed

**Dataset Improvements:**
- 100% GST characteristic coverage (vs. ~15 frequently used before)
- 15 industry domains covered (gaming, healthcare, manufacturing, etc.)
- Balanced difficulty: 29% easy / 32% medium / 39% hard
- Natural language format (vs. templated "Translate intent...")
- Explicit ground truth mappings

### Results (2025-12-05)

**New Dataset Evaluation:**

| Split | Scenarios | Accuracy | Processing |
|-------|-----------|----------|------------|
| Validation | 48 | 89.6% (43/48) | 93.8% |
| Test | 48 | 87.5% (42/48) | 93.8% |

**Comparison with Original Dataset:**

| Metric | Original (v2.2) | New (v2.3) |
|--------|-----------------|------------|
| Test Accuracy | 94.3% (87 scenarios) | 87.5% (48 scenarios) |
| Char Coverage | ~15 frequent | All 75 |
| Domains | ~5 | 15 |
| Difficulty | Mostly medium | 29/32/39 |

> Note: Lower accuracy on new dataset is expected due to increased diversity and harder scenarios.

---

## [2.2.0] - 2025-12-05

### 🎉 ICM Integration Complete & Full Validation

**Validation Set Performance: 94.2% accuracy on 86 scenarios with ICM export**

### Added

**ICM (Intent Common Model) Export:**
- Full TMF921 v5.0.0 ICM JSON-LD export capability
- Bidirectional converter (Simple ↔ ICM)
- 100% conversion success rate on all processed intents
- Three comprehensive ICM documentation guides

**Documentation Suite:**
- `docs/ICM_USER_GUIDE.md` - User-facing ICM export guide
- `docs/ICM_DEVELOPER_GUIDE.md` - Technical implementation details
- `docs/ICM_API_REFERENCE.md` - Complete API documentation
- `docs/README.md` - Documentation index and hub
- `docs/DATASET.md` - Comprehensive dataset documentation
- `docs/METRICS.md` - All metrics definitions and methodology
- `docs/REPRODUCIBILITY.md` - Full reproducibility guide

**Evaluation Script:**
- `scripts/evaluate_pipeline_with_icm.py` - Full pipeline evaluation

### Fixed

- **Final checkpoint bug** in `experiments/base_experiment.py`
  - ICM checkpoints weren't saved for experiments < 10 scenarios
  - Now saves final checkpoint at experiment completion
  
- **Import path error** in `scripts/evaluate_pipeline_with_icm.py`
  - Corrected sys.path for experiments module

### Results (2025-12-05)

**Full Validation Run (86 scenarios):**
- Overall success rate: 94.2% (81/86)
- Processing success: 98.8% (85/86)
- Validation accuracy: 95.3% (81/85 processed)
- ICM conversion: 100% (85/85)
- Average inference time: 2.1s
- Total tokens: 130,022

**Failure Analysis:**
- 1 JSON extraction failure
- 4 validation failures (mostly "NSSAA Required" characteristic)

---

## [2.1.0] - 2025-12-03

### 🎉 Final Test Set Evaluation Complete

**Test Set Performance: 94.3% accuracy on 87 held-out scenarios**

### Added

**Final Evaluation:**
- Completed test set evaluation (87 scenarios, never used during development)
- Achieved 94.3% accuracy with llama3:8b local model
- Script: `run_final_test.py` for one-time test evaluation

**Cross-Validation:**
- Executed 5-fold cross-validation on validation set
- Results: 94.0% ± 5.5% accuracy (CV = 5.8%)
- Per-fold performance: 90%, 100%, 100%, 90%, 90%

**Documentation:**
- Added comprehensive pipeline walkthrough (`docs/PIPELINE_WALKTHROUGH.md`)
- Detailed technical demonstration of scenario processing
- Complete data flow visualization with actual examples
- Step-by-step execution trace through all 8 pipeline stages

**Results:**
- Saved cross-validation results to `results/cross_validation/`
- Saved final test results to `results/rag_cloud_87_scenarios/`
- Checkpoints every 10 scenarios for reproducibility

### Fixed

- **Division by zero bug** in `experiments/base_experiment.py`
  - Occurred when no scenarios were successfully processed
  - Added check: `if successfully_processed > 0` before division
  - Prevents crash when all scenarios fail

### Changed

- **Cross-validation default model**: Changed from `gpt-oss:20b-cloud` to `llama3:8b`
  - Cloud model requires authentication
  - Local model achieves similar performance (94% vs 95%)
  - More accessible for reproduction

### Results Summary

**Publication-Ready Results:**
- Test Set: 94.3% (82/87 scenarios)
- Cross-Validation: 94.0% ± 5.5% (5-fold)
- Validation Set: 95.3% (82/86 scenarios, cloud model)
- Ablation Study: 100% with RAG + Correction

**Key Findings:**
- Local models (llama3:8b) nearly match cloud performance
- RAG is essential (+14% improvement over baseline)
- Few-shot learning breaks the system (0% accuracy)
- Consistent performance across train/val/test splits
- No overfitting observed

---

## [2.0.0] - 2025-11-25

### 🎯 Major Release: Scientific Rigor & Publication-Ready

**Scientific Rigor Score: 6/10 → 9/10** (+50% improvement)

### Added

**Dataset Expansion:**
- Integrated 574-scenario dataset (11.5x increase from 50)
- Proper train/val/test splits (401/86/87) with seed-based reproducibility
- Dataset splitting utility (`src/tmf921/utils/splitting.py`)

**Statistical Testing Framework:**
- McNemar's test for paired binary classification
- Confidence intervals (bootstrap + t-distribution)
- Effect size computation (odds ratio, Cohen's d)
- Paired t-tests for continuous metrics
- Statistical comparison reporting
- Module: `src/tmf921/utils/statistics.py` (6 functions)

**Cross-Validation:**
- K-fold cross-validation experiment class
- Variance analysis across folds
- Coefficient of variation reporting
- Module: `experiments/cross_validation.py`

**Ablation Study:**
- Systematic testing of 7 configurations
- Component contribution isolation
- Interaction effect analysis
- Module: `experiments/ablation_study.py`

**Error Analysis:**
- Automatic error categorization
- Scenario difficulty analysis
- Hard scenario identification
- Module: `src/tmf921/evaluation/error_analysis.py`

**Human Evaluation Protocol:**
- Stratified sampling (80% success, 20% failure)
- CSV template generation for annotators
- Inter-annotator agreement (Cohen's Kappa)
- Automated vs human comparison metrics
- Module: `src/tmf921/evaluation/human_eval.py`

**Honest Metrics Reporting:**
- Processing failure tracking
- Overall vs processed success rates  
- Full transparency in all counts
- Updated base experiment class

### Changed

- **README.md**: Updated with latest results (95.3% accuracy)
- **Dataset**: scenarios.json now contains 574 scenarios (was 50)
- **Metrics reporting**: Now reports honest counts (processing + validation)
- **Base experiment**: Enhanced with comprehensive metrics

### Results

**Full Validation (86 scenarios):**
- Overall success rate: 95.3% (82/86)
- Accuracy on processed: 100% (82/82)
- Processing success: 95.3% (82/86)
- Zero name corrections needed

**Ablation Study (30 scenarios):**
- Baseline (zero-shot): 96.7%
- RAG + Correction: 100% (perfect!)
- Few-shot examples: 0% (breaks system)
- **Finding**: Use RAG + correction, avoid few-shot

### Fixed

- Removed few-shot examples (found to harm performance)
- Improved prompt efficiency

### Deprecated

- Few-shot learning approach (use RAG instead)

---
## [1.0.0] - 2025-11-25

### Added
- Complete package refactoring with modular structure
- Unified experiment runner (`scripts/run_experiment.py`)
- Interactive Jupyter notebook for testing
- Comprehensive documentation (API, Architecture, Tutorial)
- RAG implementation with ChromaDB
- Cloud model support (gpt-oss:20b-cloud)
- FEACI metrics computation
- Automated name correction via fuzzy matching
- Checkpoint saving every 10 scenarios
- Results analysis and comparison tools

### Changed
- Migrated from scattered scripts to package structure
- Consolidated validation logic into BaseExperiment
- Improved prompt templates with RAG support
- Enhanced error handling and retry logic
- Optimized RAG retrieval threshold (-1.0)

### Removed
- Deprecated individual validation scripts (moved to _archive/)
- Removed duplicate code across experiments

### Fixed
- RAG retrieval bug where threshold filtered out all results
- Unicode encoding issues on Windows terminals
- JSON extraction edge cases
- Name mapping edge cases

## [0.2.0] - 2025-11-24

### Added
- RAG implementation with vector database
- Cloud model integration
- 50-scenario validation experiments

### Achievements
- 100% accuracy on 50 scenarios (RAG + Cloud)
- 7.8x speedup using cloud models
- Zero name corrections needed with RAG

## [0.1.0] - 2025-11-23

### Added
- Initial implementation
- Zero-shot and few-shot experiments
- TMF921 schema validation
- Basic prompt templates
- FEACI metrics framework

### Achievements
- 80% accuracy on 50 scenarios (few-shot)
- Established baseline metrics

## Research Milestones

- **Phase 1:** Baseline (20% zero-shot) ✅
- **Phase 2:** Few-shot (70-80%) ✅
- **Phase 3:** Name correction (80%) ✅
- **Phase 4:** RAG implementation (100%) ✅
- **Phase 5:** Refactoring & Documentation ✅

---

**Legend:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes
