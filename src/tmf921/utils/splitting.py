"""
Dataset splitting utilities for reproducible train/val/test splits.
"""

import json
import random
from pathlib import Path
from typing import List, Tuple, Dict


def create_splits(
    scenarios: List[str],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Tuple[List[str], List[str], List[str]]:
    """
    Create reproducible train/val/test splits.
    
    Args:
        scenarios: List of scenario strings
        train_ratio: Proportion for training (default 0.7)
        val_ratio: Proportion for validation (default 0.15)
        test_ratio: Proportion for testing (default 0.15)
        seed: Random seed for reproducibility
        
    Returns:
        (train_scenarios, val_scenarios, test_scenarios)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"
    
    # Set seed for reproducibility
    random.seed(seed)
    
    # Shuffle scenarios
    shuffled = scenarios.copy()
    random.shuffle(shuffled)
    
    # Calculate split indices
    n = len(scenarios)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    # Split
    train = shuffled[:train_end]
    val = shuffled[train_end:val_end]
    test = shuffled[val_end:]
    
    return train, val, test


def save_splits(
    train: List[str],
    val: List[str],
    test: List[str],
    output_dir: str = "data"
):
    """
    Save splits to separate JSON files.
    
    Args:
        train: Training scenarios
        val: Validation scenarios
        test: Test scenarios
        output_dir: Directory to save files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save train
    with open(output_path / "train.json", 'w') as f:
        json.dump(train, f, indent=2)
    
    # Save val
    with open(output_path / "val.json", 'w') as f:
        json.dump(val, f, indent=2)
    
    # Save test
    with open(output_path / "test.json", 'w') as f:
        json.dump(test, f, indent=2)
    
    # Save metadata
    metadata = {
        'total_scenarios': len(train) + len(val) + len(test),
        'train_size': len(train),
        'val_size': len(val),
        'test_size': len(test),
        'train_ratio': len(train) / (len(train) + len(val) + len(test)),
        'val_ratio': len(val) / (len(train) + len(val) + len(test)),
        'test_ratio': len(test) / (len(train) + len(val) + len(test)),
        'seed': 42
    }
    
    with open(output_path / "split_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Saved splits to {output_dir}/")
    print(f"  Train: {len(train)} scenarios")
    print(f"  Val:   {len(val)} scenarios")
    print(f"  Test:  {len(test)} scenarios")


if __name__ == "__main__":
    # Load new dataset
    with open("scenarios_new.json") as f:
        scenarios = json.load(f)
    
    print(f"Loaded {len(scenarios)} scenarios from scenarios_new.json")
    
    # Create splits
    train, val, test = create_splits(
        scenarios,
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        seed=42
    )
    
    # Save splits
    save_splits(train, val, test, output_dir="data")
    
    print("\n[SUCCESS] Dataset splits created!")
    print("Use data/train.json, data/val.json, data/test.json for experiments")
