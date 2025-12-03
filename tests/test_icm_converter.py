"""
Tests for ICM (Intent Common Model) converters.

Validates that conversion between Simple JSON and ICM JSON-LD works correctly.
"""

import pytest
from src.tmf921.icm.converter import SimpleToICMConverter, ICMToSimpleConverter


class TestSimpleToICMConverter:
    """Test Simple JSON → ICM JSON-LD conversion."""
    
    def setup_method(self):
        self.converter = SimpleToICMConverter()
    
    def test_basic_conversion(self):
        """Test basic intent conversion."""
        simple_intent = {
            "name": "Gaming Network Slice",
            "description": "High-performance gaming slice",
            "serviceSpecCharacteristic": [
                {
                    "name": "Delay tolerance",
                    "value": {
                        "value": "20",
                        "unitOfMeasure": "ms"
                    }
                }
            ]
        }
        
        icm_intent = self.converter.convert(simple_intent)
        
        # Check JSON-LD structure
        assert icm_intent["@context"] == "http://tio.models.tmforum.org/tio/v3.6.0/context.json"
        assert icm_intent["@type"] == "icm:Intent"
        assert "@id" in icm_intent
        
        # Check basic fields
        assert icm_intent["name"] == "Gaming Network Slice"
        assert icm_intent["description"] == "High-performance gaming slice"
        
        # Check expectations
        assert len(icm_intent["hasExpectation"]) == 1
        expectation = icm_intent["hasExpectation"][0]
        assert expectation["@type"] == "icm:PropertyExpectation"
        
        # Check condition
        condition = expectation["expectationCondition"]
        assert condition["@type"] == "log:Condition"
        assert "quan:smaller" in condition  # Delay tolerance → smaller
        
        # Check target
        assert len(icm_intent["target"]) == 1
        assert icm_intent["target"][0]["@type"] == "icm:Target"
    
    def test_multiple_characteristics(self):
        """Test conversion with multiple characteristics."""
        simple_intent = {
            "name": "Test Intent",
            "description": "Test",
            "serviceSpecCharacteristic": [
                {
                    "name": "Delay tolerance",
                    "value": {"value": "10", "unitOfMeasure": "ms"}
                },
                {
                    "name": "Guaranteed bandwidth",
                    "value": {"value": "100", "unitOfMeasure": "Mbps"}
                }
            ]
        }
        
        icm_intent = self.converter.convert(simple_intent)
        
        assert len(icm_intent["hasExpectation"]) == 2
        
        # First expectation (Delay) should use quan:smaller
        exp1 = icm_intent["hasExpectation"][0]
        assert "quan:smaller" in exp1["expectationCondition"]
        
        # Second expectation (Bandwidth) should use quan:greater
        exp2 = icm_intent["hasExpectation"][1]
        assert "quan:greater" in exp2["expectationCondition"]
    
    def test_operator_inference(self):
        """Test that operators are correctly inferred from characteristic names."""
        converter = SimpleToICMConverter()
        
        assert converter._infer_operator("Delay tolerance") == "quan:smaller"
        assert converter._infer_operator("Maximum latency") == "quan:smaller"
        assert converter._infer_operator("Guaranteed bandwidth") == "quan:greater"
        assert converter._infer_operator("Minimum throughput") == "quan:greater"
        assert converter._infer_operator("Exactly 5G") == "quan:equal"
    
    def test_value_parsing(self):
        """Test value type parsing."""
        converter = SimpleToICMConverter()
        
        assert converter._parse_value("20") == 20  # integer
        assert converter._parse_value("99.95") == 99.95  # float
        assert converter._parse_value("text") == "text"  # string


class TestICMToSimpleConverter:
    """Test ICM JSON-LD → Simple JSON conversion."""
    
    def setup_method(self):
        self.converter = ICMToSimpleConverter()
    
    def test_basic_reverse_conversion(self):
        """Test converting ICM back to simple JSON."""
        icm_intent = {
            "@context": "http://tio.models.tmforum.org/tio/v3.6.0/context.json",
            "@type": "icm:Intent",
            "@id": "#intent-1",
            "name": "Gaming Slice",
            "description": "Test intent",
            "hasExpectation": [
                {
                    "@type": "icm:PropertyExpectation",
                    "@id": "#exp-1",
                    "target": {"@id": "#target-1"},
                    "expectationCondition": {
                        "@type": "log:Condition",
                        "quan:smaller": {
                            "property": "Delay",
                            "value": {
                                "@value": 20,
                                "quan:unit": "ms"
                            }
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
        
        simple_intent = self.converter.convert(icm_intent)
        
        assert simple_intent["name"] == "Gaming Slice"
        assert simple_intent["description"] == "Test intent"
        assert len(simple_intent["serviceSpecCharacteristic"]) == 1
        
        char = simple_intent["serviceSpecCharacteristic"][0]
        assert "Delay" in char["name"]
        assert char["value"]["value"] == "20"
        assert char["value"]["unitOfMeasure"] == "ms"


class TestRoundTripConversion:
    """Test that Simple → ICM → Simple round-trip preserves intent."""
    
    def test_round_trip(self):
        """Test full round-trip conversion."""
        original = {
            "name": "Test Slice",
            "description": "Test description",
            "serviceSpecCharacteristic": [
                {
                    "name": "Delay tolerance",
                    "value": {"value": "15", "unitOfMeasure": "ms"}
                }
            ]
        }
        
        # Convert to ICM
        to_icm = SimpleToICMConverter()
        icm = to_icm.convert(original)
        
        # Verify ICM structure
        assert icm["@type"] == "icm:Intent"
        assert len(icm["hasExpectation"]) == 1
        
        # Convert back to Simple
        to_simple = ICMToSimpleConverter()
        result = to_simple.convert(icm)
        
        # Verify essential fields preserved
        assert result["name"] == original["name"]
        assert result["description"] == original["description"]
        assert len(result["serviceSpecCharacteristic"]) == 1
