# Architecture Guide

## System Overview

The TMF921 Intent Translation system is designed as a modular research experimentation suite for translating natural language network requirements into TMF921-compliant JSON structures.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CLI Runner   │  │ Jupyter NB   │  │ Python API   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                    Experiment Framework                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ BaseExperiment│ │ FewShot      │  │ RAG+Cloud    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                      Core Pipeline                           │
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Data    │───▶│ Prompting│───▶│   LLM    │              │
│  │ Loading  │    │ Strategy │    │ Client   │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                         │                │                   │
│                         ▼                ▼                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │   RAG    │    │  Prompt  │    │ Response │              │
│  │Retrieval │    │ Builder  │    │  Parser  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                        │                     │
│                                        ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │   Name   │───▶│  Schema  │───▶│  Result  │              │
│  │ Mapping  │    │Validation│    │  Output  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Core Modules (`src/tmf921/`)

#### 1. Core (`tmf921.core`)
**Purpose:** Fundamental data structures and interfaces

**Components:**
- `data_processor.py` - Load/process scenarios and GST spec
- `schema.py` - TMF921 validation and Pydantic models
- `client.py` - LLM client abstraction (Ollama)

**Responsibilities:**
- Data loading and validation
- Schema enforcement
- LLM communication

#### 2. Prompting (`tmf921.prompting`)
**Purpose:** Prompt engineering strategies

**Components:**
- `templates.py` - All prompt templates
- `EXAMPLE_SCENARIOS` - Few-shot examples

**Strategies:**
- Zero-shot: Minimal prompt
- Few-shot: With exemplars
- RAG: With retrieved context

#### 3. RAG (`tmf921.rag`)
**Purpose:** Retrieval-augmented generation

**Components:**
- `indexer.py` - Vector DB indexing (ChromaDB)
- `retriever.py` - Semantic search

**Flow:**
1. Index GST characteristics once
2. Retrieve relevant chars per scenario
3. Inject into prompt

#### 4. Post-Processing (`tmf921.post_processing`)
**Purpose:** Output corrections

**Components:**
- `name_mapper.py` - Fuzzy name matching

**Function:**
- Map LLM outputs to exact GST names
- Fallback for when RAG doesn't work

#### 5. Utils (`tmf921.utils`)
**Purpose:** Support utilities

**Components:**
- `config.py` - Configuration management
- `metrics.py` - FEACI metrics computation

---

## Experiment Framework

### Design Pattern: Template Method

```python
class BaseExperiment(ABC):
    # Template method
    def run(self):
        self.setup()
        for scenario in scenarios:
            self.process_scenario(scenario)
        self.compute_and_save_metrics()
    
    # Hook method (abstract)
    @abstractmethod
    def build_prompt(self, scenario):
        pass
```

### Concrete Implementations

**FewShotExperiment:**
- Uses few-shot examples
- Local or cloud models
- 70-80% accuracy

**RAGCloudExperiment:**
- RAG retrieval + cloud model
- Best accuracy (100%)
- Fastest (12s/scenario)

---

## Data Flow

### 1. Preprocessing
```
scenarios.json → ScenarioDataset → List[str]
gst.json → GSTSpecification → Dict
```

### 2. Prompt Building
```
scenario → PromptBuilder → (system_prompt, user_prompt)
                ↑
        few-shot examples / RAG
```

### 3. Generation
```
prompts → OllamaClient → raw_response
         └─ Model: llama3 / gpt-oss:20b
```

### 4. Post-Processing
```
raw_response → extract_json() → intent_dict
              → NameMapper → corrected_intent
              → Validator → validation_result
```

### 5. Output
```
validation_result → save_results()
                  → compute_metrics()
                  → FEACI scores
```

---

## Design Principles

### 1. Modularity
Each component has single responsibility:
- **Core**: Data and communication
- **Prompting**: Strategy selection
- **RAG**: Retrieval logic
- **Post-processing**: Corrections
- **Utils**: Cross-cutting concerns

### 2. Extensibility
Easy to add new:
- Experiments (inherit BaseExperiment)
- Prompt strategies (add to PromptBuilder)
- Models (extend OllamaClient)
- Metrics (extend metrics.py)

### 3. Configurability
All parameters in `config.yaml`:
- Model selection
- Experiment settings
- Evaluation metrics
- Directory paths

### 4. Testability
Each module independently testable:
- Mock LLM client
- Test with sample data
- Unit test validators

---

## Performance Architecture

### Local vs Cloud Models

**Local (llama3:latest):**
- Pros: Privacy, no API costs
- Cons: Slow (90s/scenario), limited RAM
- Use case: Development, testing

**Cloud (gpt-oss:20b-cloud):**
- Pros: Fast (12s/scenario), better quality
- Cons: Requires internet, Ollama Cloud account
- Use case: Production, experiments

### RAG Performance

**Without RAG:**
- Accuracy: 70-80%
- Issues: Wrong characteristic names

**With RAG:**
- Accuracy: 100%
- Fixed: Provides exact names
- Trade-off: Slightly slower (indexing + retrieval)

---

## Scaling Considerations

### Horizontal Scaling
Run multiple experiments in parallel:
```python
# Process scenarios in batches
for batch in batches(scenarios, batch_size=10):
    process_batch(batch)
```

### Vertical Scaling
Use better models:
- llama3:8b → gpt-oss:20b → gpt-oss:120b
- Trade-off: accuracy vs speed vs cost

### Caching
Cache LLM responses:
- Avoid re-generating same scenarios
- Significant speedup for repeated runs

---

## Error Handling

### Pipeline Resilience

**1. Data Loading**
- Validate JSON structure
- Handle missing files
- Provide helpful errors

**2. LLM Generation**
- Retry on network errors (3x with backoff)
- Timeout protection
- Extract JSON robustly

**3. Validation**
- Graceful failure on invalid JSON
- Detailed error messages
- Continue processing other scenarios

**4. Storage**
- Checkpoint every 10 scenarios
- Atomic writes
- Resume from checkpoint

---

## Future Architecture

### Phase 1: Current (Completed)
- ✅ Modular package structure
- ✅ Experiment framework
- ✅ RAG implementation
- ✅ 100% accuracy achieved

### Phase 2: Enhanced (Next)
- [ ] REST API wrapper
- [ ] Async processing
- [ ] Batch optimization
- [ ] Fine-tuning pipeline

### Phase 3: Production
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Monitoring/logging
- [ ] A/B testing framework

---

## Technology Stack

**Core:**
- Python 3.11+
- Pydantic for validation
- YAML for configuration

**LLM:**
- Ollama (local & cloud)
- Models: llama3, gpt-oss

**RAG:**
- ChromaDB for vector storage
- sentence-transformers for embeddings

**Experimentation:**
- Jupyter notebooks
- Custom experiment framework
- FEACI metrics

**Dependencies:**
- See `requirements.txt`
