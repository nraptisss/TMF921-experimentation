# ICM Export - API Reference

**Version:** 2.2.0  
**Module:** `src.tmf921.icm`

---

## Module Overview

```python
from src.tmf921.icm import (
    ICMIntent,
    PropertyExpectation,
    DeliveryExpectation,
    ReportingExpectation,
    Target,
    Condition,
    SimpleToICMConverter,
    ICMToSimpleConverter
)
```

---

## Data Models

### ICMIntent

TMF921 Intent with JSON-LD structure.

**Class:** `src.tmf921.icm.models.ICMIntent`

**Attributes:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `context` | str | No | TIO v3.6.0 URL | JSON-LD context (`@context`) |
| `type` | str | No | "icm:Intent" | RDF type (`@type`) |
| `id` | str | No | None | Unique identifier (`@id`) |
| `name` | str | Yes | - | Intent name |
| `description` | str | Yes | - | Intent description |
| `hasExpectation` | List[Dict] | No | [] | List of expectations |
| `target` | List[Dict] | No | None | Target resources |

**Example:**

```python
from src.tmf921.icm.models import ICMIntent

intent = ICMIntent(
    id="#gaming-slice",
    name="Gaming Network Slice",
    description="High-performance gaming",
    hasExpectation=[...],
    target=[...]
)

# Access JSON-LD fields
print(intent.context)  # or intent.dict(by_alias=True)["@context"]
```

**Methods:**

```python
# Convert to dictionary
intent_dict = intent.dict()  # Python naming
intent_dict = intent.dict(by_alias=True)  # JSON-LD naming (@context)

# Validate
from pydantic import ValidationError
try:
    ICMIntent(**data)
except ValidationError as e:
    print(f"Invalid: {e}")
```

---

### PropertyExpectation

Property/characteristic expectation.

**Class:** `src.tmf921.icm.models.PropertyExpectation`

**Attributes:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | str | No | "icm:PropertyExpectation" | RDF type |
| `id` | str | No | None | Expectation ID |
| `target` | Dict[str, str] | Yes | - | Target reference |
| `expectationCondition` | Dict | No | None | Condition specification |

**Example:**

```python
from src.tmf921.icm.models import PropertyExpectation

expectation = PropertyExpectation(
    id="#exp-latency",
    target={"@id": "#target-1"},
    expectationCondition={
        "@type": "log:Condition",
        "quan:smaller": {
            "property": "Latency",
            "value": {"@value": 20, "quan:unit": "ms"}
        }
    }
)
```

---

### Target

Resource target specification.

**Class:** `src.tmf921.icm.models.Target`

**Attributes:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | str | Yes | - | Target ID (`@id`) |
| `type` | str | No | "icm:Target" | RDF type |
| `resourceType` | str | No | None | Resource type |
| `chooseFrom` | Dict | No | None | Set operator |

**Example:**

```python
from src.tmf921.icm.models import Target

target = Target(
    id="#target-slice",
    resourceType="NetworkSlice",
    chooseFrom={
        "@type": "set:resourcesOfType",
        "resourceType": "5GNetworkSlice"
    }
)
```

---

### Condition

Constraint condition with operators.

**Class:** `src.tmf921.icm.models.Condition`

**Attributes:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | str | No | "log:Condition" | RDF type |
| `id` | str | No | None | Condition ID |
| `smaller` | Dict | No | None | Less than (`quan:smaller`) |
| `greater` | Dict | No | None | Greater than (`quan:greater`) |
| `equal` | Dict | No | None | Equal to (`quan:equal`) |
| `allOf` | List[Dict] | No | None | AND operator (`log:allOf`) |
| `anyOf` | List[Dict] | No | None | OR operator (`log:anyOf`) |

**Example:**

```python
from src.tmf921.icm.models import Condition

# Quantity operator
condition = Condition(
    smaller={
        "property": "Latency",
        "value": {"@value": 20, "quan:unit": "ms"}
    }
)

# Logical operator
condition = Condition(
    allOf=[
        {"quan:smaller": {...}},
        {"quan:greater": {...}}
    ]
)
```

---

## Converters

### SimpleToICMConverter

Convert simple JSON to ICM JSON-LD.

**Class:** `src.tmf921.icm.converter.SimpleToICMConverter`

**Methods:**

#### `__init__()`

Initialize converter.

```python
converter = SimpleToICMConverter()
```

**Parameters:** None

**Returns:** `SimpleToICMConverter` instance

---

#### `convert(simple_json: Dict[str, Any]) -> Dict[str, Any]`

Convert simple JSON intent to ICM format.

```python
icm_intent = converter.convert(simple_intent)
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `simple_json` | Dict[str, Any] | Yes | Simple JSON intent |

**Returns:** `Dict[str, Any]` - ICM JSON-LD intent

**Raises:** 
- `KeyError` - If required fields missing
- `ValueError` - If invalid data

**Example:**

```python
from src.tmf921.icm.converter import SimpleToICMConverter

simple = {
    "name": "Test Intent",
    "description": "Test",
    "serviceSpecCharacteristic": [
        {
            "name": "Delay tolerance",
            "value": {"value": "20", "unitOfMeasure": "ms"}
        }
    ]
}

converter = SimpleToICMConverter()
icm = converter.convert(simple)

print(icm["@type"])  # "icm:Intent"
print(len(icm["hasExpectation"]))  # 1
```

---

#### Private Methods

**`_infer_operator(char_name: str) -> str`**

Infer quantity operator from characteristic name.

```python
operator = converter._infer_operator("Delay tolerance")  # "quan:smaller"
operator = converter._infer_operator("Guaranteed bandwidth")  # "quan:greater"
```

**`_normalize_property_name(char_name: str) -> str`**

Normalize characteristic name to property name.

```python
property = converter._normalize_property_name("Delay tolerance")  # "Delay"
property = converter._normalize_property_name("Guaranteed bandwidth")  # "Bandwidth"
```

**`_parse_value(value_str: str) -> Any`**

Parse string value to appropriate type.

```python
value = converter._parse_value("20")  # 20 (int)
value = converter._parse_value("99.95")  # 99.95 (float)
value = converter._parse_value("text")  # "text" (str)
```

---

### ICMToSimpleConverter

Convert ICM JSON-LD to simple JSON.

**Class:** `src.tmf921.icm.converter.ICMToSimpleConverter`

**Methods:**

#### `__init__()`

Initialize converter.

```python
converter = ICMToSimpleConverter()
```

**Parameters:** None

**Returns:** `ICMToSimpleConverter` instance

---

#### `convert(icm_json: Dict[str, Any]) -> Dict[str, Any]`

Convert ICM intent to simple JSON.

```python
simple_intent = converter.convert(icm_intent)
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `icm_json` | Dict[str, Any] | Yes | ICM JSON-LD intent |

**Returns:** `Dict[str, Any]` - Simple JSON intent

**Example:**

```python
from src.tmf921.icm.converter import ICMToSimpleConverter

icm = {
    "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
    "@type": "icm:Intent",
    "name": "Test",
    "description": "Test intent",
    "hasExpectation": [...]
}

converter = ICMToSimpleConverter()
simple = converter.convert(icm)

print(simple["name"])  # "Test"
print("serviceSpecCharacteristic" in simple)  # True
```

---

## BaseExperiment Integration

### Parameters

**Class:** `experiments.base_experiment.BaseExperiment`

**Constructor:**

```python
BaseExperiment(
    experiment_name: str,
    model_name: str,
    num_scenarios: int,
    config_path: str = "config.yaml",
    results_dir: str = "results",
    export_icm: bool = False
)
```

**New Parameter:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `export_icm` | bool | False | Enable ICM JSON-LD export |

**Attributes:**

| Name | Type | Description |
|------|------|-------------|
| `export_icm` | bool | ICM export flag |
| `icm_converter` | SimpleToICMConverter \| None | Converter instance (if enabled) |

**Example:**

```python
from experiments.rag_cloud import RAGCloudExperiment

# With ICM export
exp = RAGCloudExperiment(
    model_name="llama3:8b",
    num_scenarios=10,
    export_icm=True  # ← Enable ICM
)

# Check status
print(f"ICM Export: {exp.export_icm}")
print(f"Converter: {exp.icm_converter}")
```

---

### Methods

**`save_checkpoint(num_scenarios: int)`**

Save checkpoint in both formats if ICM enabled.

```python
exp.save_checkpoint(10)
# Creates:
# - checkpoint_10.json (always)
# - checkpoint_10_icm.json (if export_icm=True)
```

**`compute_and_save_metrics()`**

Compute and save metrics including ICM conversion stats.

```python
exp.compute_and_save_metrics()
# metrics_summary.json includes:
# - icm_export.enabled
# - icm_export.successful_conversions
# - icm_export.conversion_rate
```

---

## Constants

### TIO Context URL

```python
TIO_CONTEXT_URL = "http://tio.models.tmforum.org/tio/v3.6.0/context.json"
```

### Default Types

```python
ICM_INTENT_TYPE = "icm:Intent"
ICM_PROPERTY_EXPECTATION_TYPE = "icm:PropertyExpectation"
ICM_TARGET_TYPE = "icm:Target"
LOG_CONDITION_TYPE = "log:Condition"
```

### Operators

**Quantity Operators (quan:):**
- `quan:smaller` - Less than
- `quan:greater` - Greater than
- `quan:equal` - Equal to
- `quan:atLeast` - At least (≥)
- `quan:atMost` - At most (≤)

**Logical Operators (log:):**
- `log:allOf` - AND (all must be true)
- `log:anyOf` - OR (at least one true)
- `log:not` - NOT (negation)

**Set Operators (set:):**
- `set:resourcesOfType` - Select by resource type
- `set:intersection` - Set intersection
- `set:union` - Set union

---

## Type Hints

### Common Types

```python
from typing import Dict, List, Any, Optional

SimpleJSON = Dict[str, Any]
ICMJSONLD = Dict[str, Any]
```

### Function Signatures

```python
def convert(simple_json: SimpleJSON) -> ICMJSONLD: ...
def convert(icm_json: ICMJSONLD) -> SimpleJSON: ...
```

---

## Exceptions

### ValidationError

Raised when pydantic validation fails.

```python
from pydantic import ValidationError

try:
    intent = ICMIntent(**data)
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Errors: {e.errors()}")
```

### KeyError

Raised when required fields missing in simple JSON.

```python
try:
    icm = converter.convert(simple_json)
except KeyError as e:
    print(f"Missing required field: {e}")
```

### ValueError

Raised for invalid data values.

```python
try:
    value = converter._parse_value(invalid_value)
except ValueError as e:
    print(f"Invalid value: {e}")
```

---

## Usage Patterns

### Pattern 1: Enable ICM in Experiment

```python
from experiments.rag_cloud import RAGCloudExperiment

exp = RAGCloudExperiment(..., export_icm=True)
exp.setup()
exp.run()
```

### Pattern 2: Manual Conversion

```python
from src.tmf921.icm.converter import SimpleToICMConverter

converter = SimpleToICMConverter()
icm = converter.convert(simple_intent)
```

### Pattern 3: Batch Processing

```python
converter = SimpleToICMConverter()
icm_intents = [converter.convert(s) for s in simple_intents]
```

### Pattern 4: Round-trip Validation

```python
from src.tmf921.icm.converter import SimpleToICMConverter, ICMToSimpleConverter

to_icm = SimpleToICMConverter()
to_simple = ICMToSimpleConverter()

# Round trip
icm = to_icm.convert(original_simple)
recovered_simple = to_simple.convert(icm)

# Verify
assert recovered_simple["name"] == original_simple["name"]
```

---

## Version Compatibility

| Feature | Version | Status |
|---------|---------|--------|
| Basic ICM models | 2.2.0 | ✅ Stable |
| SimpleToICMConverter | 2.2.0 | ✅ Stable |
| ICMToSimpleConverter | 2.2.0 | ✅ Stable |
| BaseExperiment integration | 2.2.0 | ✅ Stable |
| Quantity operators | 2.2.0 | ✅ Stable |
| Logical operators | 2.2.0 | ⚠️ Partial |
| Set operators | 2.2.0 | ⚠️ Partial |

---

## See Also

- **User Guide:** `docs/ICM_USER_GUIDE.md`
- **Developer Guide:** `docs/ICM_DEVELOPER_GUIDE.md`
- **Format Specification:** `docs/TMF921_FORMAT.md`
- **TMF921 Spec:** `docs/specs/TMF921_Intent_Management_v5.0.0_specification.pdf`

---

**Last Updated:** 2025-12-03  
**Version:** 2.2.0
