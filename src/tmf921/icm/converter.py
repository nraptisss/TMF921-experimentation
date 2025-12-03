"""
Converters between Simple JSON and ICM (Intent Common Model) formats.

Option B: Pragmatic Hybrid Implementation
- SimpleToICMConverter: Current JSON → TMF Forum ICM JSON-LD
- ICMToSimpleConverter: ICM JSON-LD → Current JSON (for compatibility)

This allows the system to:
1. Continue generating simple JSON (maintain 94.3% accuracy)
2. Export to ICM format when TM Forum compliance needed
3. Support both formats in parallel
"""

from typing import Dict, Any, List
from .models import ICMIntent, PropertyExpectation, Target


class SimpleToICMConverter:
    """
    Convert our simple TMF921 JSON to TMF Forum ICM JSON-LD format.
    
    Maps:
    - serviceSpecCharacteristic[] → hasExpectation[PropertyExpectation]
    - Adds @context, @type, @id
    - Creates Target resources
    - Wraps values in proper condition structures
    """
    
    def __init__(self):
        self.intent_counter = 0
        self.target_counter = 0
        self.expectation_counter = 0
    
    def convert(self, simple_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert simple JSON intent to ICM format.
        
        Input (Simple):
        {
          "name": "Gaming Slice",
          "description": "...",
          "serviceSpecCharacteristic": [
            {"name": "Delay tolerance", "value": {"value": "20", "unitOfMeasure": "ms"}}
          ]
        }
        
        Output (ICM):
        {
          "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
          "@type": "icm:Intent",
          "@id": "#intent-1",
          "name": "Gaming Slice",
          "description": "...",
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
        """
        self.intent_counter += 1
        intent_id = f"#intent-{self.intent_counter}"
        
        # Create target
        self.target_counter += 1
        target_id = f"#target-{self.target_counter}"
        target = {
            "@id": target_id,
            "@type": "icm:Target",
            "resourceType": "NetworkSlice"  # Default assumption
        }
        
        # Convert characteristics to expectations
        expectations = []
        characteristics = simple_json.get("serviceSpecCharacteristic", [])
        
        for char in characteristics:
            self.expectation_counter += 1
            expectation_id = f"#expectation-{self.expectation_counter}"
            
            expectation = self._convert_characteristic_to_expectation(
                char,
                expectation_id,
                target_id
            )
            expectations.append(expectation)
        
        # Build ICM intent
        icm_intent = {
            "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
            "@type": "icm:Intent",
            "@id": intent_id,
            "name": simple_json.get("name", ""),
            "description": simple_json.get("description", ""),
            "hasExpectation": expectations,
            "target": [target]
        }
        
        return icm_intent
    
    def _convert_characteristic_to_expectation(
        self,
        characteristic: Dict[str, Any],
        expectation_id: str,
        target_id: str
    ) -> Dict[str, Any]:
        """Convert a single characteristic to PropertyExpectation."""
        
        char_name = characteristic.get("name", "")
        char_value = characteristic.get("value", {})
        
        # Determine operator based on characteristic name
        operator = self._infer_operator(char_name)
        property_name = self._normalize_property_name(char_name)
        
        # Build condition
        condition = {
            "@type": "log:Condition"
        }
        
        # Add value with operator
        value_data = {
            "property": property_name,
            "value": {
                "@value": self._parse_value(char_value.get("value", "")),
                "quan:unit": char_value.get("unitOfMeasure", "")
            }
        }
        
        condition[operator] = value_data
        
        # Build expectation
        expectation = {
            "@type": "icm:PropertyExpectation",
            "@id": expectation_id,
            "target": {"@id": target_id},
            "expectationCondition": condition
        }
        
        return expectation
    
    def _infer_operator(self, char_name: str) -> str:
        """Infer quantity operator from characteristic name."""
        lower_name = char_name.lower()
        
        if any(kw in lower_name for kw in ["maximum", "max", "tolerance", "delay", "latency"]):
            return "quan:smaller"  # Less than
        elif any(kw in lower_name for kw in ["minimum", "min", "guaranteed", "bandwidth"]):
            return "quan:greater"  # Greater than
        elif any(kw in lower_name for kw in ["equal", "exactly"]):
            return "quan:equal"
        else:
            return "quan:equal"  # Default
    
    def _normalize_property_name(self, char_name: str) -> str:
        """
        Normalize characteristic name to property name.
        
        "Delay tolerance" → "Delay"
        "Guaranteed bandwidth" → "Bandwidth"
        """
        # Remove common suffixes
        name = char_name
        for suffix in [" tolerance", " guaranteed", " minimum", " maximum"]:
            if name.lower().endswith(suffix):
                name = name[:-len(suffix)]
        
        return name.strip()
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse string value to appropriate type."""
        try:
            # Try integer
            if "." not in str(value_str):
                return int(value_str)
            # Try float
            return float(value_str)
        except (ValueError, TypeError):
            # Return as string
            return value_str


class ICMToSimpleConverter:
    """
    Convert TMF Forum ICM JSON-LD to our simple JSON format.
    
    For backward compatibility and testing.
    """
    
    def convert(self, icm_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert ICM intent to simple JSON.
        
        Input (ICM):
        {
          "@context": "...",
          "@type": "icm:Intent",
          "name": "Gaming Slice",
          "hasExpectation": [...],
          "target": [...]
        }
        
        Output (Simple):
        {
          "name": "Gaming Slice",
          "description": "...",
          "serviceSpecCharacteristic": [...]
        }
        """
        # Extract basic fields
        simple_intent = {
            "name": icm_json.get("name", ""),
            "description": icm_json.get("description", ""),
            "serviceSpecCharacteristic": []
        }
        
        # Convert expectations to characteristics
        expectations = icm_json.get("hasExpectation", [])
        
        for expectation in expectations:
            if expectation.get("@type") == "icm:PropertyExpectation":
                characteristic = self._convert_expectation_to_characteristic(expectation)
                if characteristic:
                    simple_intent["serviceSpecCharacteristic"].append(characteristic)
        
        return simple_intent
    
    def _convert_expectation_to_characteristic(
        self,
        expectation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert PropertyExpectation to characteristic."""
        
        condition = expectation.get("expectationCondition", {})
        
        # Extract operator and value
        char_name = ""
        char_value = {}
        
        for key, value in condition.items():
            if key.startswith("quan:"):
                operator = key
                property_name = value.get("property", "")
                value_data = value.get("value", {})
                
                # Reconstruct characteristic name from operator + property
                if operator == "quan:smaller":
                    char_name = f"{property_name} tolerance"
                elif operator == "quan:greater":
                    char_name = f"Guaranteed {property_name.lower()}"
                else:
                    char_name = property_name
                
                char_value = {
                    "value": str(value_data.get("@value", "")),
                    "unitOfMeasure": value_data.get("quan:unit", "")
                }
                break
        
        if not char_name:
            return None
        
        return {
            "name": char_name,
            "value": char_value
        }
