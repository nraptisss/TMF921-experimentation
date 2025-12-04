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
        Validate that characteristics exist in GST spec and values match types.
        
        ENHANCED: Now validates value types, units, and data types.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        chars = intent_dict.get('serviceSpecCharacteristic', [])
        for i, char in enumerate(chars):
            char_name = char.get('name')
            
            # Check if characteristic exists in GST
            if char_name not in self.valid_characteristics:
                errors.append(f"Characteristic '{char_name}' not found in GST specification")
                continue
            
            gst_char = self.valid_characteristics[char_name]
            
            # Get value from intent
            value_obj = char.get('value', {})
            if isinstance(value_obj, dict):
                value = value_obj.get('value')
                unit = value_obj.get('unitOfMeasure', '')
            else:
                value = value_obj
                unit = ''
            
            # ENHANCED: Validate value type matches GST specification
            expected_type = gst_char.get('valueType')
            if expected_type:
                type_errors = self._validate_value_type(char_name, value, expected_type)
                errors.extend(type_errors)
            
            # ENHANCED: Validate unit of measure
            expected_unit = gst_char.get('unitOfMeasure')
            if expected_unit and unit:
                if unit.lower() != expected_unit.lower():
                    # Allow some common variations
                    unit_variations = {
                        'percent': '%',
                        'percentage': '%',
                        'milliseconds': 'ms',
                        'msec': 'ms',
                        'millisecond': 'ms'
                    }
                    normalized_unit = unit_variations.get(unit.lower(), unit.lower())
                    normalized_expected = unit_variations.get(expected_unit.lower(), expected_unit.lower())
                    
                    if normalized_unit != normalized_expected:
                        errors.append(
                            f"{char_name}: Unit '{unit}' doesn't match GST specification '{expected_unit}'"
                        )
            
            # ENHANCED: Validate value constraints (if any)
            # Note: GST doesn't have explicit min/max, but we can add logical checks
            constraint_errors = self._validate_value_constraints(char_name, value, unit, expected_type)
            errors.extend(constraint_errors)
            
        return len(errors) == 0, errors
    
    def _validate_value_type(self, char_name: str, value: Any, expected_type: str) -> List[str]:
        """
        Validate value matches expected type from GST.
        
        Args:
            char_name: Characteristic name
            value: The value to validate
            expected_type: Expected type (INTEGER, FLOAT, TEXT, BINARY, ENUM, SET)
            
        Returns:
            List of error messages
        """
        errors = []
        
        if expected_type == 'INTEGER':
            # Must be integer or string that can convert to int
            if not isinstance(value, int):
                try:
                    int_val = int(str(value))
                    # Check if it's actually an integer (not float disguised as int)
                    if '.' in str(value):
                        errors.append(f"{char_name}: Expected INTEGER, but value '{value}' has decimal point")
                except (ValueError, TypeError):
                    errors.append(f"{char_name}: Expected INTEGER, got value '{value}' (type: {type(value).__name__})")
        
        elif expected_type == 'FLOAT':
            # Must be numeric
            if not isinstance(value, (int, float)):
                try:
                    float(str(value))
                except (ValueError, TypeError):
                    errors.append(f"{char_name}: Expected FLOAT, got value '{value}' (type: {type(value).__name__})")
        
        elif expected_type == 'TEXT':
            # Must be string
            if not isinstance(value, str):
                errors.append(f"{char_name}: Expected TEXT, got value '{value}' (type: {type(value).__name__})")
        
        elif expected_type == 'BINARY':
            # Boolean or 0/1
            if not isinstance(value, (bool, int)):
                if str(value).lower() not in ['true', 'false', '0', '1', 'yes', 'no']:
                    errors.append(f"{char_name}: Expected BINARY (boolean), got value '{value}'")
        
        elif expected_type == 'ENUM':
            # Should be string from allowed set (but GST doesn't define allowed values)
            # Just check it's a string
            if not isinstance(value, str):
                errors.append(f"{char_name}: Expected ENUM (text), got value '{value}' (type: {type(value).__name__})")
        
        elif expected_type == 'SET':
            # Should be array/list
            if not isinstance(value, (list, tuple, set)):
                errors.append(f"{char_name}: Expected SET (array), got value '{value}' (type: {type(value).__name__})")
        
        return errors
    
    def _validate_value_constraints(
        self, 
        char_name: str, 
        value: Any, 
        unit: str,
        value_type: str
    ) -> List[str]:
        """
        Validate logical constraints on values.
        
        Args:
            char_name: Characteristic name
            value: The value
            unit: Unit of measure
            value_type: Type (INTEGER, FLOAT, etc.)
            
        Returns:
            List of error messages
        """
        errors = []
        
        # Only validate numeric values
        if value_type not in ['INTEGER', 'FLOAT']:
            return errors
        
        try:
            numeric_value = float(str(value))
        except (ValueError, TypeError):
            return errors  # Type validation will catch this
        
        # Logical constraints
        
        # 1. Percentages must be 0-100
        if unit.lower() in ['%', 'percent', 'percentage']:
            if numeric_value < 0 or numeric_value > 100:
                errors.append(f"{char_name}: Percentage value {numeric_value} out of range [0, 100]")
        
        # 2. Throughput/bandwidth must be positive
        if ('throughput' in char_name.lower() or 'bandwidth' in char_name.lower()):
            if numeric_value < 0:
                errors.append(f"{char_name}: Throughput/bandwidth cannot be negative ({numeric_value})")
            
            # Reasonable upper bounds
            if unit.lower() == 'gbps' and numeric_value > 10000:
                errors.append(f"{char_name}: Unrealistic bandwidth {numeric_value} Gbps (> 10 Tbps)")
        
        # 3. Latency/delay must be positive and reasonable
        if ('latency' in char_name.lower() or 'delay' in char_name.lower()):
            if numeric_value < 0:
                errors.append(f"{char_name}: Latency/delay cannot be negative ({numeric_value})")
            
            if unit.lower() == 'ms' and numeric_value < 0.001:
                errors.append(f"{char_name}: Unrealistic latency {numeric_value} ms (< 1 microsecond)")
        
        # 4. Counts must be non-negative integers
        if ('number' in char_name.lower() or 'count' in char_name.lower() or 'density' in char_name.lower()):
            if numeric_value < 0:
                errors.append(f"{char_name}: Count cannot be negative ({numeric_value})")
            
            if value_type == 'INTEGER' and int(numeric_value) != numeric_value:
                errors.append(f"{char_name}: Count must be whole number, got {numeric_value}")
        
        return errors
    
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
