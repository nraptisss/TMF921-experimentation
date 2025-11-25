"""
Characteristic name fuzzy matching and correction.

Maps common LLM-generated names to correct GST characteristic names.
"""

from typing import Dict, Optional, List
from difflib import get_close_matches
import re


class CharacteristicNameMapper:
    """Maps generic characteristic names to exact GST names."""
    
    def __init__(self, gst_spec: Dict):
        """Initialize with GST specification."""
        self.gst_spec = gst_spec
        self.valid_names = [
            char['name'] 
            for char in gst_spec.get('serviceSpecCharacteristic', [])
        ]
        
        # Common name mappings learned from errors
        self.KNOWN_MAPPINGS = {
            # Latency variations
            "E2E latency": "Delay tolerance",
            "End-to-end latency": "Delay tolerance",
            "Latency": "Delay tolerance",
            "E2E Latency": "Delay tolerance",
            "Network latency": "Delay tolerance",
            
            # Bandwidth variations
            "Bandwidth": "Downlink throughput per network slice: Maximum downlink throughput",
            "Throughput": "Downlink throughput per network slice: Maximum downlink throughput",
            "Data rate": "Downlink throughput per network slice: Maximum downlink throughput",
            
            # Availability variations
            "Uptime": "Availability",
            "Reliability": "Availability",
            "Service availability": "Availability",
            
            # User variations
            "Number of users": "Number of UEs per network slice",
            "User count": "Number of UEs per network slice",
            "Concurrent users": "Number of UEs per network slice",
        }
    
    def correct_name(self, name: str, threshold: float = 0.6) -> Optional[str]:
        """
        Correct a characteristic name to valid GST name.
        
        Args:
            name: Potentially incorrect characteristic name
            threshold: Similarity threshold for fuzzy matching
            
        Returns:
            Corrected name if found, None otherwise
        """
        # Exact match (already correct)
        if name in self.valid_names:
            return name
        
        # Check known mappings
        if name in self.KNOWN_MAPPINGS:
            return self.KNOWN_MAPPINGS[name]
        
        # Fuzzy matching using difflib
        matches = get_close_matches(name, self.valid_names, n=1, cutoff=threshold)
        if matches:
            return matches[0]
        
        # Partial string matching (contains)
        name_lower = name.lower()
        for valid_name in self.valid_names:
            if name_lower in valid_name.lower() or valid_name.lower() in name_lower:
                # Check if it's a meaningful match (not just "a" matching)
                if len(name_lower) > 3:
                    return valid_name
        
        return None
    
    def correct_intent(self, intent_dict: Dict) -> tuple[Dict, List[str]]:
        """
        Correct all characteristic names in an intent.
        
        Args:
            intent_dict: TMF921 intent dictionary
            
        Returns:
            (corrected_intent, list_of_corrections_made)
        """
        corrections = []
        
        if 'serviceSpecCharacteristic' not in intent_dict:
            return intent_dict, corrections
        
        for char in intent_dict['serviceSpecCharacteristic']:
            original_name = char.get('name')
            if not original_name:
                continue
            
            corrected_name = self.correct_name(original_name)
            
            if corrected_name and corrected_name != original_name:
                char['name'] = corrected_name
                corrections.append(f"{original_name} → {corrected_name}")
        
        return intent_dict, corrections


if __name__ == "__main__":
    import json
    
    # Load GST spec
    with open('gst.json', 'r', encoding='utf-8') as f:
        gst_spec = json.load(f)
    
    mapper = CharacteristicNameMapper(gst_spec)
    
    # Test cases
    test_names = [
        "E2E latency",
        "Bandwidth",
        "Delay tolerance",  # Should stay the same
        "Network latency",
        "Throughput",
        "Number of users",
        "Made up characteristic",  # Should return None
    ]
    
    print("Characteristic Name Correction Tests:")
    print("=" * 60)
    
    for name in test_names:
        corrected = mapper.correct_name(name)
        if corrected == name:
            print(f"✓ '{name}' (already correct)")
        elif corrected:
            print(f"→ '{name}' → '{corrected}'")
        else:
            print(f"✗ '{name}' (no match found)")
    
    # Test full intent correction
    print("\n" + "=" * 60)
    print("Full Intent Correction Test:")
    print("=" * 60)
    
    test_intent = {
        "name": "Test Intent",
        "description": "Test",
        "serviceSpecCharacteristic": [
            {
                "name": "E2E latency",
                "value": {"value": 100, "unitOfMeasure": "ms"}
            },
            {
                "name": "Bandwidth",
                "value": {"value": 50000, "unitOfMeasure": "kbps"}
            },
            {
                "name": "Delay tolerance",  # Already correct
                "value": {"value": 50, "unitOfMeasure": "ms"}
            }
        ]
    }
    
    corrected_intent, corrections = mapper.correct_intent(test_intent)
    
    print(f"\nCorrections made: {len(corrections)}")
    for correction in corrections:
        print(f"  - {correction}")
    
    print(f"\nCorrected intent:")
    for char in corrected_intent['serviceSpecCharacteristic']:
        print(f"  - {char['name']}")
