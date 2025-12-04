"""
Post-processing type correction for TMF921 intents.

Automatically fixes common type violations:
- TEXT to SET (string to array)
- TEXT to BINARY (string to boolean)
- Ensures INTEGER values are whole numbers
"""

from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class TMF921TypeCorrector:
    """Correct value types to match GST specification."""
    
    def __init__(self, gst_spec: Dict[str, Any]):
        """
        Initialize type corrector with GST specification.
        
        Args:
            gst_spec: GST specification dictionary
        """
        self.gst_spec = gst_spec
        self.characteristic_types = {
            char['name']: char.get('valueType')
            for char in gst_spec.get('serviceSpecCharacteristic', [])
        }
        self.corrections_made = []
    
    def fix_intent_types(self, intent: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Fix value types in intent to match GST specification.
        
        Args:
            intent: Intent dictionary with serviceSpecCharacteristic
            
        Returns:
            (corrected_intent, list_of_corrections_made)
        """
        self.corrections_made = []
        
        characteristics = intent.get('serviceSpecCharacteristic', [])
        
        for char in characteristics:
            char_name = char.get('name')
            
            if char_name not in self.characteristic_types:
                continue
            
            expected_type = self.characteristic_types[char_name]
            
            # Apply type-specific corrections
            if expected_type == 'SET':
                self._fix_set_type(char, char_name)
            elif expected_type == 'BINARY':
                self._fix_binary_type(char, char_name)
            elif expected_type == 'INTEGER':
                self._fix_integer_type(char, char_name)
            elif expected_type == 'FLOAT':
                self._fix_float_type(char, char_name)
        
        return intent, self.corrections_made
    
    def _fix_set_type(self, char: Dict[str, Any], char_name: str) -> None:
        """
        Fix SET type violations.
        
        Converts:
        - "value" -> ["value"]
        - "val1, val2, val3" -> ["val1", "val2", "val3"]
        """
        value_obj = char.get('value', {})
        current_value = value_obj.get('value')
        
        # Already an array - OK
        if isinstance(current_value, (list, tuple)):
            return
        
        # String that needs to be converted to array
        if isinstance(current_value, str):
            # Check if comma-separated list
            if ', ' in current_value or ',' in current_value:
                # Split on comma
                if ', ' in current_value:
                    new_value = [v.strip() for v in current_value.split(', ')]
                else:
                    new_value = [v.strip() for v in current_value.split(',')]
            else:
                # Single value -> array with one element
                new_value = [current_value]
            
            value_obj['value'] = new_value
            self.corrections_made.append(
                f"{char_name}: Converted TEXT '{current_value}' to SET {new_value}"
            )
            logger.info(f"SET correction: {char_name}: {current_value} -> {new_value}")
        
        # Number to array (rare but possible)
        elif isinstance(current_value, (int, float)):
            new_value = [str(current_value)]
            value_obj['value'] = new_value
            self.corrections_made.append(
                f"{char_name}: Converted number {current_value} to SET {new_value}"
            )
    
    def _fix_binary_type(self, char: Dict[str, Any], char_name: str) -> None:
        """
        Fix BINARY type violations.
        
        Converts:
        - "Supported" -> true
        - "Not supported" -> false
        - "99.999" -> true
        - Numeric values -> boolean based on > 0
        """
        value_obj = char.get('value', {})
        current_value = value_obj.get('value')
        
        # Already boolean - OK
        if isinstance(current_value, bool):
            return
        
        # String to boolean
        if isinstance(current_value, str):
            lower_value = current_value.lower().strip()
            
            # Explicit true values
            if lower_value in ['supported', 'yes', 'true', 'enabled', 'available', '1']:
                new_value = True
            # Explicit false values
            elif lower_value in ['not supported', 'no', 'false', 'disabled', 'unavailable', '0']:
                new_value = False
            else:
                # Try to parse as number
                try:
                    numeric_value = float(current_value)
                    new_value = numeric_value > 0
                except ValueError:
                    # Default to True if we can't parse
                    new_value = True
                    logger.warning(
                        f"BINARY correction uncertain for {char_name}: '{current_value}' -> True (default)"
                    )
            
            value_obj['value'] = new_value
            self.corrections_made.append(
                f"{char_name}: Converted TEXT '{current_value}' to BINARY {new_value}"
            )
            logger.info(f"BINARY correction: {char_name}: {current_value} -> {new_value}")
        
        # Number to boolean
        elif isinstance(current_value, (int, float)):
            new_value = current_value > 0
            value_obj['value'] = new_value
            self.corrections_made.append(
                f"{char_name}: Converted number {current_value} to BINARY {new_value}"
            )
    
    def _fix_integer_type(self, char: Dict[str, Any], char_name: str) -> None:
        """
        Fix INTEGER type violations.
        
        Ensures value is whole number:
        - "100" -> 100
        - 100.0 -> 100
        - 100.5 -> 101 (round)
        """
        value_obj = char.get('value', {})
        current_value = value_obj.get('value')
        
        # Already int - OK
        if isinstance(current_value, int) and not isinstance(current_value, bool):
            return
        
        # Convert to integer
        try:
            if isinstance(current_value, str):
                # Try to parse
                if '.' in current_value:
                    new_value = int(round(float(current_value)))
                else:
                    new_value = int(current_value)
            elif isinstance(current_value, float):
                new_value = int(round(current_value))
            else:
                return  # Can't convert
            
            if current_value != new_value:
                value_obj['value'] = new_value
                self.corrections_made.append(
                    f"{char_name}: Converted {current_value} to INTEGER {new_value}"
                )
                logger.info(f"INTEGER correction: {char_name}: {current_value} -> {new_value}")
        except (ValueError, TypeError):
            logger.warning(f"Could not convert {char_name} value '{current_value}' to INTEGER")
    
    def _fix_float_type(self, char: Dict[str, Any], char_name: str) -> None:
        """
        Fix FLOAT type violations.
        
        Ensures value is numeric:
        - "99.5" -> 99.5
        - "100" -> 100.0
        """
        value_obj = char.get('value', {})
        current_value = value_obj.get('value')
        
        # Already float or int - OK
        if isinstance(current_value, (int, float)) and not isinstance(current_value, bool):
            return
        
        # Convert to float
        try:
            if isinstance(current_value, str):
                new_value = float(current_value)
                
                if current_value != str(new_value):
                    value_obj['value'] = new_value
                    self.corrections_made.append(
                        f"{char_name}: Converted TEXT '{current_value}' to FLOAT {new_value}"
                    )
                    logger.info(f"FLOAT correction: {char_name}: {current_value} -> {new_value}")
        except (ValueError, TypeError):
            logger.warning(f"Could not convert {char_name} value '{current_value}' to FLOAT")
    
    def get_correction_summary(self) -> Dict[str, Any]:
        """
        Get summary of corrections made.
        
        Returns:
            Dictionary with correction statistics
        """
        set_corrections = len([c for c in self.corrections_made if 'SET' in c])
        binary_corrections = len([c for c in self.corrections_made if 'BINARY' in c])
        integer_corrections = len([c for c in self.corrections_made if 'INTEGER' in c])
        float_corrections = len([c for c in self.corrections_made if 'FLOAT' in c])
        
        return {
            'total_corrections': len(self.corrections_made),
            'set_corrections': set_corrections,
            'binary_corrections': binary_corrections,
            'integer_corrections': integer_corrections,
            'float_corrections': float_corrections,
            'corrections': self.corrections_made
        }


def fix_intent_types(intent: Dict[str, Any], gst_spec: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Convenience function to fix intent types.
    
    Args:
        intent: Intent to fix
        gst_spec: GST specification
        
    Returns:
        (corrected_intent, corrections_made)
    """
    corrector = TMF921TypeCorrector(gst_spec)
    return corrector.fix_intent_types(intent)
