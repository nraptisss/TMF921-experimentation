# Dataset Generation Process

> **Comprehensive documentation of the synthetic dataset generation methodology for TMF921 intent translation**

---

## Overview

This document describes the three-tier methodology used to generate high-quality synthetic training data for the TMF921 intent translation task. The process uses large language models (LLMs) to create diverse, realistic network requirement scenarios with ground truth mappings to GST characteristics.

### Why Synthetic Data?

No public dataset exists for TMF921 intent translation. Creating one requires:
- Deep domain knowledge of telecommunications
- Understanding of GST (Generic Slice Template) specifications
- Diverse representation of real-world use cases

Our approach uses powerful LLMs to generate scenarios that would traditionally require telecom domain experts.

---

## Three-Tier Generation Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TIER 1: Characteristic-Driven Generation                              │
│  • Start from each GST characteristic                                   │
│  • Generate 3 natural language requirements per characteristic          │
│  • Ensures 100% coverage of all 75 leaf characteristics                 │
│  • Ground truth is deterministic                                        │
│  • Output: 225 scenarios                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  TIER 2: Domain-Driven Generation                                       │
│  • Start from industry use cases (gaming, healthcare, etc.)             │
│  • Generate realistic multi-characteristic requirements                 │
│  • 15 industry domains × 5 scenarios each                               │
│  • Tests real-world applicability                                       │
│  • Output: 75 scenarios                                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  TIER 3: Complexity-Driven Generation                                   │
│  • Generate hard/implicit scenarios                                     │
│  • Includes ambiguous, relative, and domain-specific requirements       │
│  • Tests true intent understanding vs. keyword extraction               │
│  • Output: 20 scenarios                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Tier 1: Characteristic-Driven Generation

### Purpose
Ensure every GST characteristic is represented in the training data.

### Process

For each of the **75 leaf characteristics** in the GST specification:

1. Extract characteristic metadata:
   - Name (e.g., "Availability")
   - Description (e.g., "percentage value of uptime...")
   - Value type (FLOAT, INTEGER, BINARY, ENUM, etc.)
   - Unit of measure (percent, ms, kbps, etc.)
   - Example values from the spec

2. Prompt the LLM to generate 3 scenarios with varying difficulty:
   - **Easy**: Explicit value stated directly
   - **Medium**: Some inference required
   - **Hard**: Implicit or qualitative description

### Prompt Template

```
You are generating training data for a network intent translation system.

CHARACTERISTIC:
- Name: {characteristic_name}
- Description: {characteristic_description}
- Value Type: {value_type}
- Unit: {unit_of_measure}
- Example Values: {example_values}

TASK: Generate 3 different natural language requirements that would 
map to this characteristic. Each should:
1. Be a realistic network operator request
2. Use different phrasing/vocabulary
3. Include a plausible value
4. Vary in difficulty (easy, medium, hard)

OUTPUT: Return ONLY a valid JSON array with exactly 3 objects:
[
  {
    "natural_language": "requirement in plain English",
    "value": "the value to extract",
    "unit": "{unit}",
    "difficulty": "easy|medium|hard"
  }
]
```

### Example Output

**Characteristic: Availability**

| Difficulty | Generated Scenario |
|------------|-------------------|
| Easy | "Our SLA requires the end-to-end communication service to be available 99 percent of the time in the metro area." |
| Medium | "We are aiming for a yearly availability target of at least 99.5% for the 5G voice service across the region." |
| Hard | "The service must be up almost all the time, allowing only a few minutes of downtime per month." |

### Statistics
- **Input**: 75 leaf characteristics
- **Output**: 225 scenarios (75 × 3)
- **Difficulty split**: 33% easy, 33% medium, 33% hard

---

## Tier 2: Domain-Driven Generation

### Purpose
Generate realistic multi-characteristic requirements from specific industries.

### Industry Domains

| Domain | Description | Key Characteristics |
|--------|-------------|---------------------|
| **Gaming** | Online gaming, esports | Latency, Jitter, Packet loss |
| **Healthcare** | Telemedicine, remote surgery | Availability, Reliability, Security |
| **Manufacturing** | Smart factory, Industry 4.0 | Deterministic comm, Cycle time |
| **Autonomous Vehicles** | V2X communication | Latency, Reliability, Positioning |
| **Video Streaming** | Live streaming, VoD | Throughput, Jitter |
| **Massive IoT** | Sensors, smart meters | Device density, Battery life |
| **Smart Grid** | Power grid monitoring | Availability, Synchronicity |
| **Financial Trading** | High-frequency trading | Ultra-low latency |
| **Emergency Services** | Public safety | Priority, Availability |
| **Agriculture** | Smart farming | Rural coverage |
| **Port Logistics** | Port automation | Positioning, Throughput |
| **Stadium Events** | Large venue connectivity | Capacity, Peak load |
| **Retail** | Point of sale, inventory | Availability, Security |
| **Education** | Remote learning | Campus coverage |
| **Mining** | Underground operations | Coverage, Reliability |

### Prompt Template

```
You are generating realistic network slice requirements.

DOMAIN: {domain_name}
DESCRIPTION: {domain_description}
KEY CHARACTERISTICS: {characteristic_list}
TYPICAL VALUES: {typical_values_json}

Generate 5 different realistic requirements from a {domain_name} 
stakeholder. Requirements should:
1. Sound like real business requests from this industry
2. Combine 2-4 characteristics naturally
3. Include actual numeric values
4. Vary in specificity and difficulty
5. Include context about WHY the requirement matters

OUTPUT: Return ONLY a valid JSON array:
[
  {
    "natural_language": "the requirement with business context",
    "characteristics": [
      {"name": "GST characteristic name", "value": "value", "unit": "unit"}
    ],
    "difficulty": "easy|medium|hard"
  }
]
```

### Example Output

**Domain: Gaming**

| Difficulty | Generated Scenario |
|------------|-------------------|
| Easy | "Our casual MMO can operate with latency up to 50 ms and jitter as high as 15 ms, and we can accept packet loss up to 1%." |
| Medium | "Our mobile battle-royale title can tolerate an average latency of 30 ms and a maximum jitter of 10 ms, but we still need 99.5% availability." |
| Hard | "For our upcoming global FPS tournament we need round-trip latency of no more than 15 ms, jitter under 2 ms, packet loss below 0.1% and 99.99% availability during the event window." |

### Statistics
- **Input**: 15 industry domains
- **Output**: 75 scenarios (15 × 5)
- **Average characteristics per scenario**: 2-4

---

## Tier 3: Complexity-Driven Generation

### Purpose
Generate challenging scenarios that require deeper reasoning and domain knowledge.

### Scenario Types

| Type | Description | Example |
|------|-------------|---------|
| **Implicit** | Domain implies characteristics | "Gaming network" → low latency |
| **Relative** | Values relative to something else | "Twice as fast as current 50ms" |
| **Qualitative** | Descriptive rather than numeric | "Ultra-reliable connection" |
| **Incomplete** | Missing expected details | "Video streaming" (no bitrate) |
| **Domain-Specific** | Industry jargon | "URLLC-grade service" |

### Prompt Template

```
You are generating HARD training scenarios for a network intent 
translation system.

Generate 10 challenging network requirements that require deeper 
reasoning. Include:
1. IMPLICIT: Requirements that imply characteristics without stating them
2. RELATIVE: Requirements with relative values
3. QUALITATIVE: Requirements using descriptive terms
4. INCOMPLETE: Requirements missing some expected details
5. DOMAIN-SPECIFIC: Industry jargon requiring domain knowledge

For each requirement, provide:
- natural_language: The challenging requirement
- characteristics: Ground truth that SHOULD be inferred
- difficulty: Always "hard"
- reasoning: Why this is hard to parse
```

### Example Output

| Scenario | Inferred Characteristics |
|----------|-------------------------|
| "Our esports tournament needs a seamless experience for 10,000 concurrent players worldwide." | latency: 20ms, jitter: 5ms, bandwidth: 5Mbps/user |
| "We need the backup link to be twice as fast as the current 200 Mbps MPLS line." | bandwidth: 400 Mbps, latency: 30ms |
| "Deploy a mission-critical network for autonomous vehicle coordination." | reliability: 99.9999%, latency: 5ms |

### Statistics
- **Output**: 20 hard scenarios
- **Difficulty**: 100% hard

---

## Generation Model

### Model Used
- **Name**: `gpt-oss:120b-cloud`
- **Provider**: Ollama Cloud
- **Parameters**: 120 billion
- **Temperature**: 0.8-0.9 (for diversity)

### Why This Model?
- **High instruction following**: Produces valid JSON consistently
- **Domain knowledge**: Understands telecommunications concepts
- **Creative diversity**: Generates varied phrasings
- **Quality output**: Natural, realistic language

---

## Validation Pipeline

### Automatic Validation

Every generated scenario is validated for:

| Check | Description |
|-------|-------------|
| **Non-empty text** | natural_language ≥ 10 characters |
| **Has characteristics** | At least one characteristic mapping |
| **Valid difficulty** | One of: easy, medium, hard |
| **Valid tier** | One of: tier1, tier2, tier3 |
| **No duplicates** | Unique natural language text |

### Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Total scenarios | 320 | ✅ |
| Unique texts | 320 (100%) | ✅ |
| Has characteristics | 320 (100%) | ✅ |
| Valid difficulty | 320 (100%) | ✅ |
| GST name matches | 243/494 (49%) | ⚠️ Expected |

> Note: Not all characteristic names exactly match GST because domain-driven generation uses natural variations (e.g., "latency" vs. "Delay tolerance").

---

## Dataset Splits

### Split Configuration

```python
random.seed(42)  # Reproducibility
random.shuffle(all_scenarios)

train = scenarios[:224]   # 70%
val = scenarios[224:272]  # 15%
test = scenarios[272:]    # 15%
```

### Split Statistics

| Split | Count | Percentage |
|-------|-------|------------|
| Train | 224 | 70.0% |
| Validation | 48 | 15.0% |
| Test | 48 | 15.0% |
| **Total** | **320** | 100% |

### No Overlap Guarantee

```python
train_set ∩ val_set = ∅
train_set ∩ test_set = ∅
val_set ∩ test_set = ∅
```

---

## Output Files

### File Structure

```
data/generated/
├── tier1_characteristics.json   # Tier 1 raw output (225)
├── tier2_domains.json           # Tier 2 raw output (75)
├── tier3_complexity.json        # Tier 3 raw output (20)
├── all_scenarios_full.json      # Combined with metadata
├── all_scenarios_simple.json    # Just natural language strings
├── train_full.json              # Training set with metadata
├── train_simple.json            # Training set (strings only)
├── val_full.json                # Validation set with metadata
├── val_simple.json              # Validation set (strings only)
├── test_full.json               # Test set with metadata
├── test_simple.json             # Test set (strings only)
└── split_metadata.json          # Split configuration
```

### Full Format (with metadata)

```json
{
  "natural_language": "We need at least 99.99% uptime for our trading platform",
  "characteristics": [
    {"name": "Availability", "value": "99.99", "unit": "percent"}
  ],
  "difficulty": "easy",
  "tier": "tier1",
  "domain": null
}
```

### Simple Format (for backward compatibility)

```json
[
  "We need at least 99.99% uptime for our trading platform",
  "Deploy a gaming network with sub-20ms latency",
  ...
]
```

---

## Running the Generation

### Command

```bash
# Generate all tiers
python scripts/generate_dataset.py \
    --tier all \
    --model gpt-oss:120b-cloud \
    --tier1-per-char 3 \
    --tier2-per-domain 5 \
    --tier3-count 50 \
    --output data/generated
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--tier` | all | Which tier(s) to generate |
| `--model` | llama3:8b | Ollama model to use |
| `--tier1-per-char` | 3 | Scenarios per characteristic |
| `--tier2-per-domain` | 5 | Scenarios per domain |
| `--tier3-count` | 50 | Total Tier 3 scenarios |
| `--output` | data/generated | Output directory |

---

## Comparison: Old vs. New Dataset

| Aspect | Old Dataset (574) | New Dataset (320) |
|--------|-------------------|-------------------|
| **Format** | Templated ("Translate intent 'X' into: Y") | Natural language |
| **Characteristic coverage** | ~15 frequently used | All 75 leaf chars |
| **Difficulty levels** | Mostly medium | 29/32/39% easy/med/hard |
| **Domain diversity** | ~5 domains | 15 industries |
| **Ground truth** | Implicit in text | Explicit JSON mappings |
| **Generation method** | Manual/semi-automated | LLM with methodology |

---

## Reproducibility

### Fixed Seeds
- Data shuffling: `seed=42`
- LLM temperature: `0.8-0.9` (controlled randomness)

### Regeneration Command

```bash
# Exact reproduction
python scripts/generate_dataset.py \
    --tier all \
    --model gpt-oss:120b-cloud \
    --output data/generated_v2
```

> Note: Due to LLM stochasticity, exact reproduction requires the same model version and infrastructure.

---

## Future Improvements

1. **Increase Tier 3 count** - More hard/implicit scenarios
2. **Add multi-language** - Non-English requirements
3. **Real-world validation** - Compare with actual operator data
4. **Active learning** - Focus generation on weak areas
5. **Human annotation** - Validate a sample of ground truth

---

**Generated**: 2025-12-05  
**Model**: gpt-oss:120b-cloud via Ollama  
**Total Scenarios**: 320 (224 train / 48 val / 48 test)
