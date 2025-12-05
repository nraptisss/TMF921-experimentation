# Dataset Documentation

> **Comprehensive documentation of the 574-scenario TMF921 intent dataset**

---

## Overview

The TMF921 Intent Translation dataset contains **574 natural language network requirement scenarios** designed for translating human intents into TMF921-compliant JSON structures.

### Key Statistics

| Metric | Value |
|--------|-------|
| **Total Scenarios** | 574 |
| **Train Set** | 401 (69.9%) |
| **Validation Set** | 86 (15.0%) |
| **Test Set** | 87 (15.2%) |
| **Avg Length** | 121 characters |
| **Length Range** | 88-194 characters |
| **Split Seed** | 42 (reproducible) |

---

## Data Splits

### Train/Val/Test Distribution

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           574 Total Scenarios                            │
├─────────────────────────────────────────────────────────────────────────┤
│ ████████████████████████████████████████████████ Train (401)  69.9%    │
│ ████████████ Validation (86)  15.0%                                     │
│ ████████████ Test (87)  15.2%                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Split Methodology

```python
from tmf921.core import ScenarioDataset

dataset = ScenarioDataset("scenarios.json")
train, val, test = dataset.split(
    train_ratio=0.70,
    val_ratio=0.15,
    test_ratio=0.15,
    seed=42  # Reproducible split
)
```

The splits are:
- **Stratified by scenario length** to ensure balanced difficulty
- **Randomly shuffled** with fixed seed for reproducibility
- **Non-overlapping** - no scenario appears in multiple splits

### Split Metadata

File: `data/split_metadata.json`
```json
{
  "total_scenarios": 574,
  "train_size": 401,
  "val_size": 86,
  "test_size": 87,
  "train_ratio": 0.6986,
  "val_ratio": 0.1498,
  "test_ratio": 0.1516,
  "seed": 42
}
```

---

## Scenario Format

### Structure

Each scenario is a **natural language string** describing network requirements:

```
"Translate intent '<user requirement>' into: <expected parameters>."
```

### Example Scenarios

#### Gaming/Low-Latency
```
"Create a gaming slice with sub-20ms ping, 50 Mbps guaranteed, and 
99.95% uptime for 10,000 concurrent players."
```

#### IoT/Massive Scale
```
"Parse intent 'we need massive IoT deployment' into network parameters: 
1 Mbps bandwidth per device, 50ms latency tolerance, 10,000 node 
scalability, mMTC slice type."
```

#### Healthcare/Mission-Critical
```
"Translate intent 'provide carrier-grade reliability' into: 99.9999% 
uptime SLA, <4.32 seconds downtime per year."
```

#### Enterprise/Security
```
"Translate intent 'enable slice-specific security policies' into: 
per-slice encryption, isolated trust domains."
```

---

## Scenario Categories

### Distribution by Domain

| Category | Count | Percentage | Keywords |
|----------|-------|------------|----------|
| **Network Slicing** | 110 | 19.2% | slice, slicing |
| **Latency** | 70 | 12.2% | latency, delay, ms |
| **Reliability** | 19 | 3.3% | reliability, uptime |
| **Bandwidth** | 14 | 2.4% | bandwidth, Mbps, throughput |
| **Availability** | 10 | 1.7% | availability, SLA |
| **Video/Streaming** | 7 | 1.2% | video, streaming |
| **Gaming** | 6 | 1.0% | gaming, players |
| **IoT** | 6 | 1.0% | IoT, sensors, devices |
| **Coverage** | 4 | 0.7% | coverage, area |
| **5G/Cellular** | 3 | 0.5% | 5G, cellular |
| **Healthcare** | 2 | 0.3% | healthcare, medical |

### Scenario Intent Types

| Type | Pattern | Example |
|------|---------|---------|
| **Translate** | "Translate intent 'X' into: Y" | Direct mapping |
| **Parse** | "Parse intent 'X' into: parameters" | Parameter extraction |
| **Recognize** | "Recognize intent 'X' and apply" | Pattern matching |
| **Infer** | "Infer X from intent 'Y'" | Implicit extraction |

---

## GST Specification

### Overview

The system uses the **TMF921 GST (Generic Slice Template) External v10.0.0** specification as the target schema.

### GST Statistics

| Metric | Value |
|--------|-------|
| **Total Characteristics** | 87 |
| **Value Types** | 6 (INTEGER, FLOAT, TEXT, BINARY, ENUM, SET) |
| **With Descriptions** | 87 (100%) |

### Key Characteristics

The most commonly mapped characteristics:

```
1. Delay tolerance (latency requirements)
2. Availability (uptime percentage)
3. Downlink throughput per network slice: Maximum downlink throughput
4. Downlink throughput per network slice: Guaranteed downlink throughput quota
5. Uplink throughput per network slice: Maximum uplink throughput
6. Number of UEs per network slice
7. Coverage
8. Reliability
9. Jitter
10. User data rate
```

---

## Data Files

### Location

```
data/
├── train.json         # 401 training scenarios
├── val.json           # 86 validation scenarios
├── test.json          # 87 test scenarios (held-out)
├── split_metadata.json # Split configuration
└── quick_validation.json # 5 scenarios for testing
```

### File Format

All files are JSON arrays of strings:

```json
[
  "Scenario 1 text...",
  "Scenario 2 text...",
  ...
]
```

---

## Dataset Creation

### Methodology

The dataset was created through a systematic process:

1. **Requirements Analysis**
   - Reviewed TMF921 v5.0.0 specification
   - Identified common network requirement patterns
   - Catalogued GST characteristic types

2. **Scenario Generation**
   - Created diverse industry use cases
   - Covered all 87 GST characteristics
   - Varied complexity levels

3. **Quality Assurance**
   - Reviewed for grammatical correctness
   - Validated technical accuracy
   - Ensured coverage of edge cases

4. **Splitting**
   - Random shuffle with seed=42
   - 70/15/15 train/val/test split
   - Verified no overlap

### Complexity Levels

| Level | Characteristics | Example |
|-------|----------------|---------|
| **Simple** | 1-2 requirements | "Gaming slice with 20ms latency" |
| **Medium** | 3-4 requirements | "IoT with bandwidth, latency, coverage" |
| **Complex** | 5+ requirements | "Full enterprise slice specification" |

---

## Usage

### Loading Data

```python
from tmf921.core import ScenarioDataset

# Load validation set
val_dataset = ScenarioDataset("data/val.json")
print(f"Loaded {len(val_dataset.scenarios)} scenarios")

# Access scenarios
for scenario in val_dataset.scenarios[:3]:
    print(f"- {scenario[:60]}...")
```

### Analyzing Data

```python
# Get dataset statistics
stats = val_dataset.analyze()
print(f"Average length: {stats['avg_length_chars']:.0f} chars")
print(f"Common requirements: {stats['common_requirements']}")
```

---

## Integrity Verification

### Checksums

To verify data integrity:

```bash
# Generate checksums
md5sum data/*.json

# Expected (example):
# a1b2c3... data/train.json
# d4e5f6... data/val.json
# g7h8i9... data/test.json
```

### Validation

```python
import json

# Verify no overlap between splits
with open('data/train.json') as f: train = set(json.load(f))
with open('data/val.json') as f: val = set(json.load(f))
with open('data/test.json') as f: test = set(json.load(f))

assert len(train & val) == 0, "Train/val overlap!"
assert len(train & test) == 0, "Train/test overlap!"
assert len(val & test) == 0, "Val/test overlap!"
print("✓ No overlap - data integrity verified")
```

---

## Limitations

### Known Limitations

1. **Synthetic Data**: Scenarios are synthetically generated, not from real deployments
2. **English Only**: All scenarios in English
3. **Format Consistency**: Some variation in scenario phrasing
4. **Implicit Requirements**: Some scenarios have implied (not explicit) requirements

### Recommendations

- Use for research and development
- Validate on real-world data when possible
- Consider augmentation for production systems

---

## Citation

When using this dataset:

```bibtex
@dataset{tmf921_intent_dataset,
  title = {TMF921 Intent Translation Dataset},
  author = {Research Team},
  year = {2025},
  version = {2.0},
  size = {574 scenarios},
  split = {401/86/87 train/val/test}
}
```

---

**Last Updated:** 2025-12-05  
**Version:** 2.0  
**Maintainer:** Research Team
