# ICM Implementation - Developer Guide

**Audience:** Developers maintaining or extending the ICM implementation  
**Level:** Technical  
**Version:** 2.2.0

---

## Architecture Overview

### Design Philosophy

The ICM implementation follows the **Adapter Pattern** to provide TM Forum compliance without impacting the core LLM generation pipeline.

```
┌─────────────────────────────────────────────────┐
│          Natural Language Input                  │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│      LLM Generation (RAG + Prompting)            │
│      Accuracy: 94.3%                             │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│         Simple JSON Intent                       │
│         (Core Format)                            │
└───────────────┬─────────────────────────────────┘
                │
                ├─────────────────────┐
                │                     │
                ▼                     ▼
    ┌───────────────────┐   ┌──────────────────┐
    │  Save Simple JSON │   │ SimpleToICM      │
    │  (Always)         │   │ Converter        │
    └───────────────────┘   │ (If enabled)     │
                            └────────┬──────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  ICM JSON-LD     │
                            │  (TM Forum)      │
                            └──────────────────┘
```

### Key Design Decisions

1. **Post-processing conversion** - Not LLM-direct generation
   - **Rationale:** Maintains proven 94.3% accuracy
   - **Trade-off:** Requires conversion step
   
2. **Optional feature** -  `export_icm` parameter
   - **Rationale:** Backward compatibility
   - **Trade-off:** None (pure addition)

3. **Automatic  inference** - Operators auto-detected
   - **Rationale:** Simplifies usage
   - **Trade-off:** May need manual override for edge cases

---

## Module Structure

```
src/tmf921/icm/
├── __init__.py           # Module exports
├── models.py             # Pydantic data models
└── converter.py          # Conversion logic

experiments/
└── base_experiment.py    # Integration point

docs/
├── TMF921_FORMAT.md      # Format specification
├── ICM_USER_GUIDE.md     # User documentation
└── ICM_DEVELOPER_GUIDE.md # This file
```

---

## Core Components

### 1. ICM Data Models (`models.py`)

**Purpose:** Define TMF921 ICM structure using Pydantic

#### ICMIntent

Main intent class with JSON-LD support:

```python
class ICMIntent(BaseModel):
    context: str = Field(
        default="http://tio.models.tmforum.org/tio/v3.6.0/context.json",
        alias="@context"
    )
    type: str = Field(default="icm:Intent", alias="@type")
    id: Optional[str] = Field(None, alias="@id")
    name: str
    description: str
    hasExpectation: List[Dict[str, Any]] = Field(default_factory=list)
    target: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        populate_by_name = True  # Support both 'context' and '@context'
```

**Key Features:**
- `alias` for JSON-LD @ notation
- `populate_by_name` for dual access
- Default values for TIO v3.6.0

#### PropertyExpectation

Represents characteristic expectations:

```python
class PropertyExpectation(BaseModel):
    type: str = Field(default="icm:PropertyExpectation", alias="@type")
    id: Optional[str] = Field(None, alias="@id")
    target: Dict[str, str]  # Reference to Target
    expectationCondition: Optional[Dict[str, Any]] = None
```

**Usage:**
```python
expectation = PropertyExpectation(
    id="#exp-1",
    target={"@id": "#target-1"},
    expectationCondition={
        "@type": "log:Condition",
        "quan:smaller": {...}
    }
)
```

#### Other Models

- `Target` - Resource identification
- `Condition` - Constraint specification
- `DeliveryExpectation` - Resource delivery
- `ReportingExpectation` - Status reporting
- `IntentReport` - Lifecycle reports

---

### 2. Converters (`converter.py`)

#### SimpleToICMConverter

**Purpose:** Convert simple JSON → ICM JSON-LD

**Algorithm:**

1. **Intent Creation**
   ```python
   icm_intent = {
       "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
       "@type": "icm:Intent",
       "@id": f"#intent-{counter}",
       "name": simple["name"],
       "description": simple["description"]
   }
   ```

2. **Target Generation**
   ```python
   target = {
       "@id": f"#target-{counter}",
       "@type": "icm:Target",
       "resourceType": "NetworkSlice"  # Default
   }
   ```

3. **Characteristic → Expectation**
   ```python
   for char in simple["serviceSpecCharacteristic"]:
       operator = _infer_operator(char["name"])
       expectation = {
           "@type": "icm:PropertyExpectation",
           "@id": f"#expectation-{counter}",
           "target": {"@id": target_id},
           "expectationCondition": {
               "@type": "log:Condition",
               operator: {...}
           }
       }
   ```

**Operator Inference Logic:**

```python
def _infer_operator(self, char_name: str) -> str:
    lower_name = char_name.lower()
    
    # Less than (quan:smaller)
    if any(kw in lower_name for kw in [
        "maximum", "max", "tolerance", "delay", "latency"
    ]):
        return "quan:smaller"
    
    # Greater than (quan:greater)
    elif any(kw in lower_name for kw in [
        "minimum", "min", "guaranteed", "bandwidth"
    ]):
        return "quan:greater"
    
    # Equal (quan:equal)
    else:
        return "quan:equal"
```

**Property Name Normalization:**

```python
def _normalize_property_name(self, char_name: str) -> str:
    name = char_name
    for suffix in [" tolerance", " guaranteed", " minimum", " maximum"]:
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]
    return name.strip()
```

**Examples:**
- "Delay tolerance" → property:"Delay", operator:"quan:smaller"
- "Guaranteed bandwidth" → property:"Bandwidth", operator:"quan:greater"
- "Maximum latency" → property:"Latency", operator:"quan:smaller"

#### ICMToSimpleConverter

**Purpose:** Convert ICM JSON-LD → simple JSON (reverse)

**Algorithm:**

1. Extract basic fields
2. Iterate through expectations
3. Convert PropertyExpectation → characteristic
4. Reconstruct characteristic name

**Usage:**
```python
converter = ICMToSimpleConverter()
simple = converter.convert(icm_intent)
```

---

### 3. BaseExperiment Integration

#### Initialization

```python
class BaseExperiment(ABC):
    def __init__(self, ..., export_icm: bool = False):
        self.export_icm = export_icm
        self.icm_converter = None if not export_icm else SimpleToICMConverter()
```

**Lazy Initialization:** Converter only created if `export_icm=True`

#### Checkpoint Save

```python
def save_checkpoint(self, num_scenarios: int):
    # Always save simple format
    checkpoint_file = self.results_dir / f"checkpoint_{num_scenarios}.json"
    with open(checkpoint_file, 'w') as f:
        json.dump(self.results, f, indent=2)
    
    # Optionally save ICM format
    if self.export_icm and self.icm_converter:
        icm_results = []
        for result in self.results:
            if result.get('generated_intent'):
                try:
                    icm_intent = self.icm_converter.convert(result['generated_intent'])
                    icm_results.append({
                        'generated_intent_icm': icm_intent,
                        'generated_intent_simple': result['generated_intent'],
                        ...
                    })
                except Exception as e:
                    print(f"[WARNING] ICM conversion failed: {e}")
                    icm_results.append(result)
```

**Error Handling:**
- Conversion failures logged but not fatal
- Original simple JSON always preserved
- Partial ICM export possible

#### Metrics Tracking

```python
def compute_and_save_metrics(self):
    ...
    
    if self.export_icm and self.icm_converter:
        icm_success_count = 0
        for result in self.results:
            if result.get('generated_intent'):
                try:
                    self.icm_converter.convert(result['generated_intent'])
                    icm_success_count += 1
                except:
                    pass
        
        metrics_summary['icm_export'] = {
            'enabled': True,
            'successful_conversions': icm_success_count,
            'conversion_rate': icm_success_count / successfully_processed
        }
```

---

## Testing Strategy

### Unit Tests

**Converter Tests** (`tests/test_icm_converter.py`):
- Basic conversion
- Multiple characteristics
- Operator inference
- Value parsing
- Reverse conversion
- Round-trip preservation

**Integration Tests** (`tests/test_icm_export_base.py`):
- Converter initialization
- Parameter handling
- Export flag behavior

### Test Coverage

```
tests/
├── test_icm_converter.py      # 6 tests
├── test_icm_export_base.py    # 2 tests
└── fixtures/
    └── tmf921_examples/        # Reference examples
```

**Run Tests:**
```bash
# All ICM tests
pytest tests/test_icm_*.py -v

# Specific test
pytest tests/test_icm_converter.py::TestSimpleToICMConverter::test_basic_conversion -v
```

---

## Extension Points

### 1. Adding New Operators

**Location:** `src/tmf921/icm/converter.py`

```python
def _infer_operator(self, char_name: str) -> str:
    lower_name = char_name.lower()
    
    # Add new operator
    if "between" in lower_name:
        return "quan:between"  # New operator
    
    # Existing logic...
```

**Update Condition Model:**

```python
# In models.py
class Condition(BaseModel):
    ...
    between: Optional[Dict[str, Any]] = Field(
        None,
        alias="quan:between",
        description="Range constraint"
    )
```

### 2. Custom Resource Types

Override in converter:

```python
class CustomICMConverter(SimpleToICMConverter):
    def _get_resource_type(self, scenario: str) -> str:
        if "iot" in scenario.lower():
            return "IoTNetworkSlice"
        elif "5g" in scenario.lower():
            return "5GNetworkSlice"
        return "NetworkSlice"  # Default
```

### 3. Additional Expectations

Add DeliveryExpectation:

```python
def convert(self, simple_json: Dict) -> Dict:
    icm_intent = {...}
    
    # Add delivery expectation
    delivery_exp = {
        "@type": "icm:DeliveryExpectation",
        "@id": "#delivery-1",
        "target": {"@id": target_id},
        "targetType": "NetworkSlice"
    }
    icm_intent["hasExpectation"].append(delivery_exp)
    
    return icm_intent
```

---

## Performance Optimization

### Current Performance

| Operation | Time | Memory |
|-----------|------|--------|
| Single conversion | ~0.1ms | ~50KB |
| 100 conversions | ~10ms | ~5MB |
| 1000 conversions | ~100ms | ~50MB |

### Optimization Opportunities

1. **Batch Conversion**
   ```python
   def convert_batch(self, intents: List[Dict]) -> List[Dict]:
       return [self.convert(intent) for intent in intents]
   ```

2. **Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def _infer_operator(self, char_name: str) -> str:
       # Cached operator inference
   ```

3. **Parallel Processing**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor() as executor:
       icm_intents = list(executor.map(converter.convert, simple_intents))
   ```

---

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('tmf921.icm')

# In converter
logger.debug(f"Converting: {simple_intent['name']}")
logger.debug(f"Inferred operator: {operator}")
```

### Common Issues

**Issue: Operator inference wrong**

Solution: Override manually

```python
class ManualOperatorConverter(SimpleToICMConverter):
    def __init__(self, operator_map: Dict[str, str]):
        super().__init__()
        self.operator_map = operator_map
    
    def _infer_operator(self, char_name: str) -> str:
        return self.operator_map.get(char_name, super()._infer_operator(char_name))

# Usage
converter = ManualOperatorConverter({
    "Custom metric": "quan:greater"
})
```

**Issue: Missing characteristics in ICM**

Check:
1. Characteristic structure in simple JSON
2. Conversion try-except blocks
3. Validation errors

```python
# Validate before conversion
from src.tmf921.core.schema import TMF921Intent

try:
    validated = TMF921Intent(**simple_intent)
except ValidationError as e:
    print(f"Invalid simple JSON: {e}")
```

---

## Future Enhancements

### Planned Features

1. **Logical Operators** (log:allOf, log:anyOf)
   - Combine multiple conditions
   - Complex constraint expressions

2. **Set Operators** (set:resourcesOfType, set:intersection)
   - Advanced target selection
   - Resource filtering

3. **Direct ICM Generation**
   - LLM generates ICM directly
   - Compare accuracy vs conversion approach

4. **ICM Validation**
   - Validate against TMF921 schemas
   - JSON-LD verification
   - RDF triple correctness

### Research Questions

- Can LLMs generate ICM directly with acceptable accuracy?
- What is the optimal prompt structure for ICM generation?
- How does semantic validation improve intent quality?

---

## Code Style Guidelines

### Follow Project Standards

1. **Type Hints**
   ```python
   def convert(self, simple_json: Dict[str, Any]) -> Dict[str, Any]:
   ```

2. **Docstrings**
   ```python
   def convert(self, simple_json: Dict) -> Dict:
       """
       Convert simple JSON to ICM format.
       
       Args:
           simple_json: Simple JSON intent
           
       Returns:
           ICM JSON-LD intent
           
       Raises:
           ValueError: If simple_json invalid
       """
   ```

3. **Error Handling**
   ```python
   try:
       icm_intent = converter.convert(simple_intent)
   except Exception as e:
       logger.error(f"Conversion failed: {e}")
       # Graceful degradation
   ```

---

## Contributing

### Adding New Features

1. Create feature branch
2. Implement with tests
3. Update documentation
4. Submit PR

### Testing Checklist

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] Examples provided
- [ ] Backward compatible

---

## References

- **TMF921 v5.0.0:** `docs/specs/TMF921_Intent_Management_v5.0.0_specification.pdf`
- **TR290A v3.6.0:** Intent Expression Model
- **TR290V v3.6.0:** Vocabulary Reference
- **TR292D v3.6.0:** Quantity Ontology
- **TR292E v3.6.0:** Conditions and Logical Operators

---

**Maintainer:** Development Team  
**Last Updated:** 2025-12-03  
**Version:** 2.2.0
