"""
Data processing utilities for TMF921 intent translation research.

Handles loading, analyzing, and splitting the scenarios dataset and GST specification.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import Counter
import yaml


class ScenarioDataset:
    """Load and manage the 456 telecom scenarios."""
    
    def __init__(self, scenarios_path: str = "scenarios.json"):
        self.scenarios_path = Path(scenarios_path)
        self.scenarios = self._load_scenarios()
        
    def _load_scenarios(self) -> List[str]:
        """Load scenarios from JSON file."""
        with open(self.scenarios_path, 'r', encoding='utf-8') as f:
            scenarios = json.load(f)
        print(f"[OK] Loaded {len(scenarios)} scenarios from {self.scenarios_path}")
        return scenarios
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze dataset characteristics."""
        stats = {
            "total_scenarios": len(self.scenarios),
            "avg_length_chars": sum(len(s) for s in self.scenarios) / len(self.scenarios),
            "avg_length_words": sum(len(s.split()) for s in self.scenarios) / len(self.scenarios),
            "min_length": min(len(s) for s in self.scenarios),
            "max_length": max(len(s) for s in self.scenarios),
        }
        
        # Extract common patterns
        keywords = []
        for scenario in self.scenarios:
            # Extract bandwidth mentions
            if "Mbps" in scenario or "Gbps" in scenario or "kbps" in scenario:
                keywords.append("bandwidth")
            # Extract latency mentions
            if "ms latency" in scenario or "latency" in scenario:
                keywords.append("latency")
            # Extract reliability mentions
            if "reliability" in scenario or "uptime" in scenario or "%" in scenario:
                keywords.append("reliability")
            # Extract coverage mentions
            if "coverage" in scenario or "area" in scenario:
                keywords.append("coverage")
                
        stats["common_requirements"] = Counter(keywords).most_common(10)
        
        return stats
    
    def split(self, train_ratio: float = 0.7, val_ratio: float = 0.15, 
              test_ratio: float = 0.15, seed: int = 42) -> Tuple[List[str], List[str], List[str]]:
        """Split dataset into train/val/test."""
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, "Ratios must sum to 1"
        
        random.seed(seed)
        shuffled = self.scenarios.copy()
        random.shuffle(shuffled)
        
        n = len(shuffled)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        train = shuffled[:train_end]
        val = shuffled[train_end:val_end]
        test = shuffled[val_end:]
        
        print(f"[OK] Split: Train={len(train)}, Val={len(val)}, Test={len(test)}")
        return train, val, test
    
    def get_samples(self, n: int, seed: int = 42) -> List[str]:
        """Get n random samples for quick validation."""
        random.seed(seed)
        return random.sample(self.scenarios, min(n, len(self.scenarios)))


class GSTSpecification:
    """Load and analyze GST (Generic Slice Template) specification."""
    
    def __init__(self, gst_path: str = "gst.json"):
        self.gst_path = Path(gst_path)
        self.spec = self._load_spec()
        self.characteristics = self._extract_characteristics()
        
    def _load_spec(self) -> Dict[str, Any]:
        """Load GST specification."""
        with open(self.gst_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        print(f"[OK] Loaded GST specification: {spec.get('name', 'Unknown')}")
        return spec
    
    def _extract_characteristics(self) -> List[Dict[str, Any]]:
        """Extract service characteristics from GST."""
        chars = self.spec.get("serviceSpecCharacteristic", [])
        print(f"[OK] Extracted {len(chars)} service characteristics")
        return chars
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze GST specification structure."""
        char_types = Counter([c.get("valueType") for c in self.characteristics])
        
        stats = {
            "total_characteristics": len(self.characteristics),
            "characteristic_names": [c.get("name") for c in self.characteristics],
            "value_types": dict(char_types),
            "has_descriptions": sum(1 for c in self.characteristics if c.get("description")),
            "configurable": sum(1 for c in self.characteristics if c.get("configurable", False)),
        }
        
        # Key characteristics for intent mapping
        key_chars = []
        for char in self.characteristics:
            name = char.get("name", "").lower()
            if any(kw in name for kw in ["bandwidth", "throughput", "latency", "availability", "reliability"]):
                key_chars.append(char.get("name"))
        
        stats["key_characteristics"] = key_chars
        
        return stats
    
    def get_characteristic_schema(self) -> Dict[str, Any]:
        """Get schema structure for validation."""
        schema = {
            "name": self.spec.get("name"),
            "description": self.spec.get("description"),
            "version": self.spec.get("version"),
            "characteristics": {}
        }
        
        for char in self.characteristics:
            char_name = char.get("name")
            schema["characteristics"][char_name] = {
                "valueType": char.get("valueType"),
                "description": char.get("description"),
                "minCardinality": char.get("minCardinality"),
                "maxCardinality": char.get("maxCardinality"),
            }
        
        return schema


def main():
    """Run data analysis."""
    print("\n" + "="*60)
    print("TMF921 Intent Translation - Data Analysis")
    print("="*60 + "\n")
    
    # Load configuration
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Analyze scenarios
    print("[*] Analyzing Scenarios Dataset...")
    print("-" * 60)
    dataset = ScenarioDataset(config['data']['scenarios_path'])
    stats = dataset.analyze()
    
    print(f"\nDataset Statistics:")
    print(f"  Total scenarios: {stats['total_scenarios']}")
    print(f"  Avg length: {stats['avg_length_chars']:.1f} chars, {stats['avg_length_words']:.1f} words")
    print(f"  Range: {stats['min_length']}-{stats['max_length']} chars")
    print(f"\n  Common requirements:")
    for req, count in stats['common_requirements']:
        print(f"    - {req}: {count} mentions")
    
    # Analyze GST
    print(f"\n[*] Analyzing GST Specification...")
    print("-" * 60)
    gst = GSTSpecification(config['data']['gst_spec_path'])
    gst_stats = gst.analyze()
    
    print(f"\nGST Structure:")
    print(f"  Total characteristics: {gst_stats['total_characteristics']}")
    print(f"  Value types: {gst_stats['value_types']}")
    print(f"  Has descriptions: {gst_stats['has_descriptions']}/{gst_stats['total_characteristics']}")
    print(f"\n  Key characteristics for intent mapping:")
    for char in gst_stats['key_characteristics'][:10]:
        print(f"    - {char}")
    
    # Create splits
    print(f"\n[*] Creating Data Splits...")
    print("-" * 60)
    train, val, test = dataset.split(
        config['data']['train_split'],
        config['data']['val_split'],
        config['data']['test_split'],
        config['data']['random_seed']
    )
    
    # Save splits
    splits_dir = Path("data")
    splits_dir.mkdir(exist_ok=True)
    
    with open(splits_dir / "train.json", 'w') as f:
        json.dump(train, f, indent=2)
    with open(splits_dir / "val.json", 'w') as f:
        json.dump(val, f, indent=2)
    with open(splits_dir / "test.json", 'w') as f:
        json.dump(test, f, indent=2)
    
    print(f"[OK] Saved splits to {splits_dir}/")
    
    # Quick validation sample
    print(f"\n[*] Generating Quick Validation Sample...")
    print("-" * 60)
    quick_sample = dataset.get_samples(config['experiments']['quick_validation']['num_samples'])
    
    with open(splits_dir / "quick_validation.json", 'w') as f:
        json.dump(quick_sample, f, indent=2)
    
    print(f"[OK] Saved {len(quick_sample)} samples to {splits_dir}/quick_validation.json")
    
    print(f"\n{'='*60}")
    print(" [SUCCESS] Data analysis complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
