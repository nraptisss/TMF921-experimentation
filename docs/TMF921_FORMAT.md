# TMF921 Intent Common Model (ICM) Format

**Version:** TMF921 v5.0.0 + TR290 v3.6.0  
**Format:** JSON-LD with TM Forum Intent Ontology (TIO)  
**Purpose:** TM Forum compliant intent representation

---

## Overview

The Intent Common Model (ICM) is TM Forum's standard format for expressing network intents using semantic web technologies. It uses JSON-LD (JSON for Linked Data) with specific ontology namespaces.

### Key Differences vs. Simple JSON

| Aspect | Simple JSON (Current) | ICM JSON-LD (TM Forum) |
|--------|----------------------|------------------------|
| **Format** | Plain JSON | JSON-LD with @context |
| **Structure** | Flat characteristics | Hierarchical (Expectations → Conditions → Targets) |
| **Characteristics** | `serviceSpecCharacteristic[]` | `hasExpectation[]` |
| **Values** | Direct name-value pairs | Typed expectations with operators |
| **Operators** | Implicit | Explicit (quan:, log:, set:) |
| **Targets** | Not specified | Explicit target resources |
| **Complexity** | Low | High |

---

## Structure

### Core Intent

```json
{
  "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
  "@type": "icm:Intent",
  "@id": "unique-intent-id",
  "name": "Intent Name",
  "description": "What this intent achieves",
  "hasExpectation": [...],
  "target": [...]
}
```

**Fields:**
- `@context`: JSON-LD context URL (TIO v3.6.0)
- `@type`: RDF type identifier (`icm:Intent`)
- `@id`: Unique identifier (URI or URN)
- `name`: Human-readable name
- `description`: Detailed description
- `hasExpectation`: Array of expectations
- `target`: Array of target resources

---

## Expectation Types

### 1. PropertyExpectation

Specifies desired properties/characteristics.

```json
{
  "@type": "icm:PropertyExpectation",
  "@id": "#expectation-1",
  "target": {"@id": "#target-1"},
  "expectationCondition": {
    "@type": "log:Condition",
    "quan:smaller": {
      "property": "Latency",
      "value": {
        "@value": 20,
        "quan:unit": "ms"
      }
    }
  }
}
```

**Used for:** Latency, bandwidth, availability, etc.

### 2. DeliveryExpectation

Specifies what should be delivered.

```json
{
  "@type": "icm:DeliveryExpectation",
  "@id": "#expectation-delivery",
  "target": {"@id": "#target-1"},
  "targetType": "NetworkSlice"
}
```

**Used for:** Service delivery, resource provisioning

### 3. ReportingExpectation

Specifies how to report intent status.

```json
{
  "@type": "icm:ReportingExpectation",
  "@id": "#expectation-reporting",
  "target": {"@id": "#intent-id"},
  "reportDestination": ["urn:intent-manager:portal"],
  "reportTriggers": [
    "imo:IntentAccepted",
    "imo:IntentComplies",
    "imo:IntentDegrades"
  ]
}
```

**Used for:** Lifecycle reporting, status updates

---

## Targets

Targets identify the resources the intent applies to.

```json
{
  "@id": "#target-1",
  "@type": "icm:Target",
  "resourceType": "NetworkSlice",
  "chooseFrom": {
    "@type": "set:resourcesOfType",
    "resourceType": "5GNetworkSlice"
  }
}
```

**Fields:**
- `@id`: Target identifier
- `resourceType`: General resource type
- `chooseFrom`: Set operator for resource selection

---

## Operators

### Quantity Operators (TR292D)

From `quan:` namespace:

| Operator | Meaning | Example Use |
|----------|---------|-------------|
| `quan:smaller` | Less than | Latency < 20ms |
| `quan:greater` | Greater than | Bandwidth > 100 Mbps |
| `quan:equal` | Equal to | Exactly 5G |
| `quan:atLeast` | At least | >= 99.9% uptime |
| `quan:atMost` | At most | <= 500 devices |

**Example:**
```json
"quan:smaller": {
  "property": "Latency",
  "value": {"@value": 20, "quan:unit": "ms"}
}
```

### Logical Operators (TR292E)

From `log:` namespace:

| Operator | Meaning | Example Use |
|----------|---------|-------------|
| `log:allOf` | AND (all must be true) | Latency AND Bandwidth |
| `log:anyOf` | OR (at least one true) | 4G OR 5G |
| `log:not` | NOT (negation) | Not legacy network |

**Example:**
```json
"log:allOf": [
  {"quan:smaller": {...}},
  {"quan:greater": {...}}
]
```

### Set Operators (TR292F)

From `set:` namespace:

| Operator | Meaning | Example Use |
|----------|---------|-------------|
| `set:resourcesOfType` | Select by type | All 5G slices |
| `set:intersection` | Set intersection | Common resources |
| `set:union` | Set union | Combined resources |

---

## Conversion Examples

### Simple JSON → ICM

**Input (Simple):**
```json
{
  "name": "Gaming Slice",
  "description": "Low latency gaming",
  "serviceSpecCharacteristic": [
    {
      "name": "Delay tolerance",
      "value": {"value": "20", "unitOfMeasure": "ms"}
    }
  ]
}
```

**Output (ICM):**
```json
{
  "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
  "@type": "icm:Intent",
  "@id": "#intent-1",
  "name": "Gaming Slice",
  "description": "Low latency gaming",
  "hasExpectation": [
    {
      "@type": "icm:PropertyExpectation",
      "@id": "#expectation-1",
      "target": {"@id": "#target-1"},
      "expectationCondition": {
        "@type": "log:Condition",
        "quan:smaller": {
          "property": "Delay",
          "value": {"@value": 20, "quan:unit": "ms"}
        }
      }
    }
  ],
  "target": [
    {
      "@id": "#target-1",
      "@type": "icm:Target",
      "resourceType": "NetworkSlice"
    }
  ]
}
```

---

## Usage in Our System

### Option B: Pragmatic Hybrid

```python
from src.tmf921.icm.converter import SimpleToICMConverter

# Generate simple JSON (current pipeline)
simple_intent = generate_intent(scenario)  # 94.3% accuracy

# Convert to ICM for TM Forum compliance
converter = SimpleToICMConverter()
icm_intent = converter.convert(simple_intent)

# Export both formats
save_json(simple_intent, "output_simple.json")
save_json(icm_intent, "output_icm.json")
```

### Benefits

1. **Maintain Accuracy**: LLM generates simple JSON (proven 94.3%)
2. **TM Forum Compliance**: Export to ICM when needed
3. **Flexibility**: Support both formats
4. **Lower Risk**: No impact to current pipeline

---

## References

- **TMF921 v5.0.0:** Pages 159-178 (Intent creation)
- **TR290A v3.6.0:** Pages 11-26 (Intent Expression)
- **TR290B v3.6.0:** Pages 17-20 (Intent Reporting)
- **TR290V v3.6.0:** Vocabulary reference
- **TR292D v3.6.0:** Quantity operators
- **TR292E v3.6.0:** Logical operators
- **TR292F v3.6.0:** Set operators

---

## Validation

### ICM Validation Checklist

- [ ] Has `@context` with TIO URL
- [ ] Has `@type` = "icm:Intent"
- [ ] Has unique `@id`
- [ ] Has `name` and `description`
- [ ] All expectations have `@type`
- [ ] All conditions use proper operators (quan:, log:, set:)
- [ ] All targets have `@id` and `@type`
- [ ] Values have proper units (`quan:unit`)
- [ ] Valid JSON-LD structure

### Tools

```python
from src.tmf921.icm.models import ICMIntent
from pydantic import ValidationError

try:
    intent = ICMIntent(**icm_json)
    print("✓ Valid ICM Intent")
except ValidationError as e:
    print(f"✗ Invalid: {e}")
```

---

**Status:** Documentation Complete  
**Next:** Validate against official TMF921 v5.0.0 examples
