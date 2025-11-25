# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
