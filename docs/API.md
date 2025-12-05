# API Reference

Complete API documentation for the TMF921 Intent Translation package.

## Core Module (`tmf921.core`)

### ScenarioDataset

Load and manage TMF921 intent scenarios.

```python
from tmf921.core import ScenarioDataset

# Load scenarios
dataset = ScenarioDataset("data/val.json")

# Access scenarios
scenarios = dataset.scenarios  # List of scenario strings

# Analyze dataset
stats = dataset.analyze()
# Returns: {
#     'total_scenarios': int,
#     'avg_length_chars': float,
#     'common_requirements': List[Tuple[str, int]]
# }

# Split dataset
train, val, test = dataset.split(
    train_ratio=0.7, 
    val_ratio=0.15, 
    test_ratio=0.15,
    seed=42
)
```

### GSTSpecification

Load and work with TMF921 GST specifications.

```python
from tmf921.core import GSTSpecification

# Load GST
gst = GSTSpecification("gst.json")

# Access specification
spec = gst.spec  # Full specification dict
characteristics = gst.characteristics  # List of characteristics

# Analyze
stats = gst.analyze()
# Returns: {
#     'total_characteristics': int,
#     'characteristic_names': List[str],
#     'value_types': Dict[str, int],
#     'key_characteristics': List[str]
# }
```

### TMF921Validator

Validate TMF921 intent JSON structures.

```python
from tmf921.core import TMF921Validator

# Initialize
validator = TMF921Validator(gst_spec)

# Validate intent
intent = {
    "name": "Test Intent",
    "description": "...",
    "serviceSpecCharacteristic": [...]
}

validation = validator.validate_all(intent)
# Returns: {
#     'format_valid': bool,
#     'characteristics_valid': bool,
#     'plausibility_valid': bool,
#     'errors': List[str],
#     'warnings': List[str],
#     'overall_valid': bool
# }
```

### OllamaClient

Interface to Ollama LLM models.

```python
from tmf921.core import OllamaClient

# Initialize
client = OllamaClient(
    model="gpt-oss:20b-cloud",
    base_url="http://localhost:11434"
)

# Check connection
if client._check_connection():
    print("Connected")

# Generate
response = client.generate(
    prompt="Your prompt here",
    system_prompt="System prompt",
    temperature=0.1,
    max_tokens=2048,
    top_p=0.9
)
# Returns: {
#     'response': str,
#     'tokens': int,
#     'time_seconds': float,
#     'model': str
# }

# Extract JSON
intent_json = client.extract_json(response['response'])
```

---

## Prompting Module (`tmf921.prompting`)

### TMF921PromptBuilder

Build prompts for intent translation.

```python
from tmf921.prompting import TMF921PromptBuilder, EXAMPLE_SCENARIOS

# Initialize
builder = TMF921PromptBuilder(gst_spec)

# System prompt
system_prompt = builder.build_system_prompt()

# Zero-shot prompt
zero_shot = builder.build_zero_shot_prompt(scenario)

# Few-shot prompt
few_shot = builder.build_few_shot_prompt(
    scenario,
    EXAMPLE_SCENARIOS[:3],  # List of examples
    max_examples=3
)

# RAG prompt
rag_prompt = builder.build_rag_prompt(
    scenario,
    retrieved_characteristics,  # List from GSTRetriever
    include_examples=True
)
```

---

## RAG Module (`tmf921.rag`)

### GSTIndexer

Index GST characteristics for retrieval.

```python
from tmf921.rag import GSTIndexer

# Initialize
indexer = GSTIndexer(
    gst_path="gst.json",
    db_path="chroma_db"
)

# Create index
collection = indexer.create_index(
    collection_name="gst_characteristics"
)

# Get statistics
stats = indexer.get_stats()
```

### GSTRetriever

Retrieve relevant characteristics.

```python
from tmf921.rag import GSTRetriever

# Initialize
retriever = GSTRetriever(
    db_path="chroma_db",
    collection_name="gst_characteristics"
)

# Retrieve for scenario
characteristics = retriever.retrieve_for_scenario(
    scenario,
    n_results=8
)
# Returns: List[{
#     'name': str,
#     'description': str,
#     'valueType': str,
#     'similarity': float
# }]

# Direct retrieval
results = retriever.retrieve(
    query="network latency requirements",
    n_results=5,
    min_similarity=-1.0
)
```

---

## Post-Processing Module (`tmf921.post_processing`)

### CharacteristicNameMapper

Correct characteristic names via fuzzy matching.

```python
from tmf921.post_processing import CharacteristicNameMapper

# Initialize
mapper = CharacteristicNameMapper(gst_spec)

# Correct intent
corrected_intent, corrections = mapper.correct_intent(intent_json)
# Returns: (corrected_intent_dict, List[str] of corrections)

# Correct single name
correct_name = mapper.correct_name("E2E latency")
# Returns: "Delay tolerance"
```

---

## Utils Module (`tmf921.utils`)

### Configuration

```python
from tmf921.utils import load_config, get_model_config

# Load config
config = load_config("config.yaml")

# Get model config
model_cfg = get_model_config(config, "gpt-oss:20b-cloud")
```

### Metrics

```python
from tmf921.utils import compute_feaci_metrics, print_feaci_metrics

# Compute metrics
results = [...]  # List of experiment results
metrics = compute_feaci_metrics(results)
# Returns: {
#     'format_correctness': float,
#     'accuracy': float,
#     'cost_avg_tokens': float,
#     'inference_time_avg_seconds': float,
#     'num_results': int
# }

# Print metrics
print_feaci_metrics(metrics)
```

---

## ICM Module (`tmf921.icm`) — *NEW in v2.2.0*

### SimpleToICMConverter

Convert simple JSON to TM Forum ICM JSON-LD format.

```python
from tmf921.icm import SimpleToICMConverter

# Initialize converter
converter = SimpleToICMConverter()

# Convert simple intent to ICM
simple_intent = {
    "name": "Gaming Slice",
    "description": "Low latency gaming",
    "serviceSpecCharacteristic": [
        {
            "name": "Delay tolerance",
            "value": {"value": "20", "unitOfMeasure": "ms"}
        }
    ]
}

icm_intent = converter.convert(simple_intent)
# Returns: {
#     "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
#     "@type": "icm:Intent",
#     "@id": "#intent-1",
#     "name": "Gaming Slice",
#     "hasExpectation": [...],
#     "target": [...]
# }
```

### ICMToSimpleConverter

Convert ICM format back to simple JSON (reverse conversion).

```python
from tmf921.icm import ICMToSimpleConverter

converter = ICMToSimpleConverter()
simple_intent = converter.convert(icm_intent)
# Returns: Original simple format
```

### Using with Experiments

```python
from experiments.rag_cloud import RAGCloudExperiment

# Enable ICM export in experiments
exp = RAGCloudExperiment(
    model_name="llama3:8b",
    num_scenarios=10,
    export_icm=True  # ← Enable ICM export
)

exp.setup()
exp.run()

# Both formats saved:
# - checkpoint_10.json (simple)
# - checkpoint_10_icm.json (ICM JSON-LD)
```

---

## Experiments

### BaseExperiment

Abstract base class for experiments.

```python
from experiments.base_experiment import BaseExperiment

class MyExperiment(BaseExperiment):
    def build_prompt(self, scenario):
        # Implement prompt building
        system_prompt = "..."
        user_prompt = "..."
        return system_prompt, user_prompt

# Run experiment
exp = MyExperiment(
    experiment_name="my_experiment",
    model_name="gpt-oss:20b-cloud",
    num_scenarios=10
)
exp.setup()
exp.run()
```

### FewShotExperiment

```python
from experiments.few_shot import FewShotExperiment

exp = FewShotExperiment(
    model_name="llama3:latest",
    num_scenarios=10,
    num_examples=3
)
exp.setup()
exp.run()
```

### RAGCloudExperiment

```python
from experiments.rag_cloud import RAGCloudExperiment

exp = RAGCloudExperiment(
    model_name="gpt-oss:20b-cloud",
    num_scenarios=50
)
exp.setup()
exp.run()
```

---

## Complete Example

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

from tmf921 import (
    ScenarioDataset, GSTSpecification, TMF921Validator,
    OllamaClient, TMF921PromptBuilder, EXAMPLE_SCENARIOS,
    CharacteristicNameMapper
)

# Load data
gst = GSTSpecification("gst.json")
scenarios = ScenarioDataset("data/val.json")

# Initialize components
validator = TMF921Validator(gst.spec)
prompt_builder = TMF921PromptBuilder(gst.spec)
name_mapper = CharacteristicNameMapper(gst.spec)
client = OllamaClient(model="gpt-oss:20b-cloud")

# Process a scenario
scenario = scenarios.scenarios[0]
system_prompt = prompt_builder.build_system_prompt()
user_prompt = prompt_builder.build_few_shot_prompt(
    scenario, EXAMPLE_SCENARIOS[:3], max_examples=3
)

# Generate
response = client.generate(
    prompt=user_prompt,
    system_prompt=system_prompt
)

# Extract and validate
intent = client.extract_json(response['response'])
corrected, corrections = name_mapper.correct_intent(intent)
validation = validator.validate_all(corrected)

print(f"Valid: {validation['overall_valid']}")
```
