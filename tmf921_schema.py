"""
TMF921 Intent schema definition and validation utilities.

Based on TMF921 Intent Management API specification.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class IntentType(str, Enum):
    """TMF921 Intent types."""
    CUSTOMER_FACING = "CustomerFacingServiceIntent"
    RESOURCE_FACING = "ResourceFacingServiceIntent"
    NETWORK_SLICE = "NetworkSliceIntent"


class CharacteristicValueType(str, Enum):
    """GST characteristic value types."""
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    BINARY = "BINARY"
    ENUM = "ENUM"
    SET = "SET"

class ServiceCharacteristicValue(BaseModel):
    """A value for a service characteristic."""
    value: Any
    alias: Optional[str] = None
    unitOfMeasure: Optional[str] = None


class ServiceCharacteristic(BaseModel):
    """TMF921 service characteristic."""
    name: str
    description: Optional[str] = None
    valueType: Optional[CharacteristicValueType] = None
    value: Optional[ServiceCharacteristicValue] = None
    
    class Config:
        use_enum_values = True


class TMF921Intent(BaseModel):
    """
    TMF921 Intent structure for network slice configuration.
    
    Based on GST External specification v10.0.0.
    """
    # Core intent attributes
    name: str = Field(..., description="Intent name/identifier")
    description: str = Field(..., description="Human-readable intent description")
    
    # Service characteristics - key network requirements
    serviceSpecCharacteristic: List[ServiceCharacteristic] = Field(
        default_factory=list,
        description="List of service characteristics defining network slice requirements"
    )
    
    # Optional metadata
    version: Optional[str] = "1.0.0"
    intentType: Optional[IntentType] = IntentType.NETWORK_SLICE
    
    class Config:
        use_enum_values = True


class TMF921Validator:
    """Validate TMF921 intent translations."""
    
    def __init__(self, gst_spec: Dict[str, Any]):
        """Initialize validator with GST specification."""
        self.gst_spec = gst_spec
        self.valid_characteristics = {
            char['name']: char 
            for char in gst_spec.get('serviceSpecCharacteristic', [])
        }
        
    def validate_format(self, intent_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate TMF921 format correctness.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if 'name' not in intent_dict:
            errors.append("Missing required field: 'name'")
        if 'description' not in intent_dict:
            errors.append("Missing required field: 'description'")
            
        # Check characteristics structure
        if 'serviceSpecCharacteristic' in intent_dict:
            chars = intent_dict['serviceSpecCharacteristic']
            if not isinstance(chars, list):
                errors.append("'serviceSpecCharacteristic' must be a list")
            else:
                for i, char in enumerate(chars):
                    if 'name' not in char:
                        errors.append(f"Characteristic {i} missing 'name' field")
                    if 'value' not in char:
                        errors.append(f"Characteristic {i} missing 'value' field")
        
        return len(errors) == 0, errors
    
    def validate_characteristics(self, intent_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that characteristics exist in GST spec.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        warnings = []
        
        chars = intent_dict.get('serviceSpecCharacteristic', [])
        for char in chars:
            char_name = char.get('name')
            
            # Check if characteristic exists in GST
            if char_name not in self.valid_characteristics:
                errors.append(f"Characteristic '{char_name}' not found in GST specification")
                continue
            
            # Check value type compatibility
            gst_char = self.valid_characteristics[char_name]
            expected_type = gst_char.get('valueType')
            
            # Value validation would go here
            # For now, we just check existence
            
        return len(errors) == 0, errors
    
    def validate_plausibility(self, intent_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate plausibility of values (hallucination detection).
        
        Returns:
            (is_valid, list_of_warnings)
        """
        warnings = []
        
        chars = intent_dict.get('serviceSpecCharacteristic', [])
        char_values = {char['name']: char.get('value', {}).get('value') for char in chars}
        
        # Bandwidth plausibility (should be reasonable for telecom)
        bandwidth_chars = [c for c in chars if 'bandwidth' in c.get('name', '').lower() or 'throughput' in c.get('name', '').lower()]
        for char in bandwidth_chars:
            value = char.get('value', {}).get('value')
            unit = char.get('value', {}).get('unitOfMeasure', '')
            
            if value and isinstance(value, (int, float, str)):
                try:
                    val_num = float(str(value))
                    # Check if bandwidth is unreasonably high (>1Tbps) or low (<1kbps)
                    if 'gbps' in unit.lower() and val_num > 1000:
                        warnings.append(f"Unusually high bandwidth: {val_num} {unit}")
                    elif 'kbps' in unit.lower() and val_num < 1:
                        warnings.append(f"Unusually low bandwidth: {val_num} {unit}")
                except:
                    pass
        
        # Latency plausibility
        latency_chars = [c for c in chars if 'latency' in c.get('name', '').lower()]
        for char in latency_chars:
            value = char.get('value', {}).get('value')
            
            if value and isinstance(value, (int, float, str)):
                try:
                    val_num = float(str(value))
                    # Check if latency is unreasonably low (<0.1ms) or high (>10000ms)
                    if val_num < 0.1:
                        warnings.append(f"Unrealistically low latency: {val_num}ms")
                    elif val_num > 10000:
                        warnings.append(f"Unusually high latency: {val_num}ms")
                except:
                    pass
        
        # Availability/reliability plausibility (should be 0-100%)
        availability_chars = [c for c in chars if 'availability' in c.get('name', '').lower() or 'reliability' in c.get('name', '').lower()]
        for char in availability_chars:
            value = char.get('value', {}).get('value')
            
            if value and isinstance(value, (int, float, str)):
                try:
                    val_num = float(str(value))
                    if val_num < 0 or val_num > 100:
                        warnings.append(f"Availability/reliability out of range: {val_num}%")
                except:
                    pass
        
        return True, warnings  # Warnings don't invalidate, just flag
    
    def validate_all(self, intent_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all validations and return comprehensive results.
        
        Returns:
            {
                'format_valid': bool,
                'characteristics_valid': bool,
                'plausibility_valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'overall_valid': bool
            }
        """
        format_valid, format_errors = self.validate_format(intent_dict)
        char_valid, char_errors = self.validate_characteristics(intent_dict)
        plaus_valid, plaus_warnings = self.validate_plausibility(intent_dict)
        
        return {
            'format_valid': format_valid,
            'characteristics_valid': char_valid,
            'plausibility_valid': plaus_valid,
            'errors': format_errors + char_errors,
            'warnings': plaus_warnings,
            'overall_valid': format_valid and char_valid
        }


def extract_key_characteristics(gst_spec: Dict[str, Any]) -> List[str]:
    """Extract key characteristics names from GST for prompt construction."""
    chars = gst_spec.get('serviceSpecCharacteristic', [])
    
    # Priority characteristics for intent mapping
    priority_keywords = [
        'bandwidth', 'throughput', 'latency', 'delay', 
        'availability', 'reliability', 'coverage', 'area',
        'energy', 'efficiency', 'user', 'communication'
    ]
    
    key_chars = []
    for char in chars:
        name = char.get('name', '').lower()
        if any(kw in name for kw in priority_keywords):
            key_chars.append(char.get('name'))
    
    return key_chars


if __name__ == "__main__":
    # Test with a sample intent
    import json
    
    # Load GST spec
    with open('gst.json', 'r', encoding='utf-8') as f:
        gst_spec = json.load(f)
    
    # Create validator
    validator = TMF921Validator(gst_spec)
    
    # Test intent
    test_intent = {
        "name": "Remote Surgery Network Slice",
        "description": "Ultra-low latency network slice for remote surgery applications",
        "serviceSpecCharacteristic": [
            {
                "name": "Availability",
                "value": {"value": "99.999", "unitOfMeasure": "percent"}
            },
            {
                "name": "Downlink throughput per network slice: Maximum downlink throughput",
                "value": {"value": "100000", "unitOfMeasure": "kbps"}
            }
        ]
    }
    
    # Validate
    results = validator.validate_all(test_intent)
    
    print("Validation Results:")
    print(f"  Format Valid: {results['format_valid']}")
    print(f"  Characteristics Valid: {results['characteristics_valid']}")
    print(f"  Overall Valid: {results['overall_valid']}")
    print(f"  Errors: {results['errors']}")
    print(f"  Warnings: {results['warnings']}")
    
    # Extract key characteristics
    key_chars = extract_key_characteristics(gst_spec)
    print(f"\nKey Characteristics ({len(key_chars)}):")
    for char in key_chars[:15]:
        print(f"  - {char}")
