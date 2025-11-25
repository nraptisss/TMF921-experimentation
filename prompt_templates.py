"""
Structured prompt templates for TMF921 intent translation.

Based on SOTA 5-section prompting (Bimo et al., 2025) and TMF921 specification.
"""

import json
from typing import List, Dict, Any, Optional


class TMF921PromptBuilder:
    """Build structured prompts following SOTA best practices."""
    
    def __init__(self, gst_spec: Dict[str, Any]):
        """
        Initialize with GST specification.
        
        Args:
            gst_spec: Loaded GST specification JSON
        """
        self.gst_spec = gst_spec
        self.characteristic_names = [
            char['name'] 
            for char in gst_spec.get('serviceSpecCharacteristic', [])
        ]
        
        # Key characteristics for examples
        self.key_chars = self._extract_key_characteristics()
    
    def _extract_key_characteristics(self) -> List[str]:
        """Extract most relevant characteristics for prompting."""
        priority_keywords = [
            'bandwidth', 'throughput', 'latency', 'delay',
            'availability', 'reliability', 'coverage', 'area'
        ]
        
        key_chars = []
        for char in self.gst_spec.get('serviceSpecCharacteristic', []):
            name = char.get('name', '').lower()
            if any(kw in name for kw in priority_keywords):
                key_chars.append(char.get('name'))
        
        return key_chars[:20]  # Top 20 most relevant
    
    def build_zero_shot_prompt(
        self,
        scenario: str,
        include_schema: bool = True,
        include_examples_list: bool = False
    ) -> str:
        """
        Build zero-shot structured 5-section prompt.
        
        Following Bimo et al., 2025 architecture:
        - Section 1: Intent specification
        - Section 2: Network topology context
        - Section 3: KPIs and constraints
        - Section 4: Configuration parameter space
        - Section 5: Output format specification
        
        Args:
            scenario: Natural language scenario to translate
            include_schema: Whether to include full characteristic list
            include_examples_list: Whether to list example characteristic names
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""# SECTION 1: Intent Specification

You are tasked with translating a natural language network requirement into a TMF921-compliant Intent JSON structure.

**Input Scenario:**
"{scenario}"

# SECTION 2: Network Context

The target is a 5G/6G network slice configuration based on the TMF GST (Generic Slice Template) External specification v10.0.0.

**Network Type:** Network Slice Intent
**Technology:** 5G/6G
**Standard:** TMF921 Intent Management API

# SECTION 3: KPIs and Constraints

Extract the following types of requirements from the scenario:
- **Bandwidth/Throughput:** Maximum or guaranteed data rates (kbps, Mbps, Gbps)
- **Latency/Delay:** Maximum allowable latency (ms, seconds)
- **Availability/Reliability:** Uptime percentage or reliability requirements
- **Coverage/Area:** Geographic scope, regions, altitude requirements
- **User Count:** Number of concurrent users or devices
- **QoS Parameters:** Priority, jitter, packet loss requirements

# SECTION 4: Configuration Parameter Space (TMF921 Service Characteristics)

The output MUST use characteristics from the GST specification. """

        if include_schema:
            prompt += f"Available characteristics include:\n\n"
            for char_name in self.key_chars:
                prompt += f"- {char_name}\n"
        
        if include_examples_list:
            prompt += f"\n**Key Characteristics to Consider:**\n"
            prompt += "- Availability\n"
            prompt += "- Downlink throughput per network slice: Maximum downlink throughput\n"
            prompt += "- Uplink throughput per network slice: Maximum uplink throughput\n"
            prompt += "- E2E latency\n"
            prompt += "- Jitter\n"
            prompt += "- Reliability\n"
            prompt += "- User data rate\n"
            prompt += "- Area of Service\n"
        
        prompt += f"""

# SECTION 5: Output Format Specification

Generate a valid JSON object with the following structure:

{{
  "name": "<descriptive intent name>",
  "description": "<human-readable description of what this intent achieves>",
  "serviceSpecCharacteristic": [
    {{
      "name": "<characteristic name from GST>",
      "value": {{
        "value": "<extracted value>",
        "unitOfMeasure": "<unit if applicable, e.g., 'kbps', 'ms', 'percent'>"
      }}
    }}
  ]
}}

**Critical Instructions:**
1. Use ONLY characteristic names that exist in the TMF GST specification
2. Extract ALL relevant requirements from the scenario
3. Provide appropriate units of measure
4. Values must be realistic for telecom networks (e.g., latency 1-1000ms, bandwidth 1kbps-10Gbps)
5. Return ONLY the JSON object, no additional text

**Output (JSON only):**
"""
        return prompt
    
    def build_few_shot_prompt(
        self,
        scenario: str,
        examples: List[Dict[str, Any]],
        max_examples: int = 3
    ) -> str:
        """
        Build few-shot prompt with examples.
        
        Args:
            scenario: Natural language scenario to translate
            examples: List of (scenario, tmf921_json) example pairs
            max_examples: Maximum number of examples to include
            
        Returns:
            Formatted few-shot prompt
        """
        base_prompt = """You are an expert in translating natural language network requirements into TMF921-compliant Intent JSON structures.

# Task

Translate the given scenario into a valid TMF921 Intent JSON following the examples below.

"""
        
        # Add examples
        for i, example in enumerate(examples[:max_examples], 1):
            base_prompt += f"""## Example {i}

**Scenario:** {example['scenario']}

**TMF921 Intent:**
```json
{json.dumps(example['intent'], indent=2)}
```

"""
        
        # Add actual task
        base_prompt += f"""# Your Task

**Scenario:** {scenario}

**TMF921 Intent (JSON only):**
"""
        
        return base_prompt
    
    def build_cot_prompt(self, scenario: str) -> str:
        """
        Build Chain-of-Thought reasoning prompt.
        
        Multi-stage reasoning process:
        1. Understand requirements
        2. Extract key parameters
        3. Map to TMF characteristics
        4. Generate JSON
        5. Validate output
        """
        prompt = f"""# Chain-of-Thought Intent Translation

Translate the following scenario step-by-step.

**Scenario:** "{scenario}"

**Step 1: Understand Requirements**
List all network requirements mentioned in the scenario (bandwidth, latency, reliability, coverage, users, etc.):

**Step 2: Extract Key Parameters**
For each requirement, extract the specific value and unit:

**Step 3: Map to TMF Characteristics**
Match each parameter to the appropriate TMF921 service characteristic name:

**Step 4: Generate TMF921 JSON**
Create the complete JSON structure:

**Step 5: Validate**
Check that:
- All characteristic names are valid TMF GST characteristics
- Values are realistic for telecom networks
- Units of measure are appropriate
- JSON is properly formatted

**Final TMF921 Intent (JSON only):**
"""
        return prompt
    
    def build_rag_prompt(
        self,
        scenario: str,
        retrieved_characteristics: List[Dict[str, Any]],
        include_examples: bool = True
    ) -> str:
        """
        Build RAG-enhanced prompt with retrieved characteristics.
        
        Args:
            scenario: Natural language scenario to translate
            retrieved_characteristics: List of relevant characteristics from RAG
            include_examples: Whether to include few-shot examples
            
        Returns:
            Formatted RAG prompt
        """
        prompt = f"""# Task: TMF921 Intent Translation

Translate the following network requirement into a TMF921-compliant Intent JSON structure.

## Scenario
"{scenario}"

## Relevant TMF921 Characteristics (Retrieved from Specification)

Based on this scenario, the following characteristics are most relevant:

"""
        
        # Add retrieved characteristics
        for i, char in enumerate(retrieved_characteristics, 1):
            prompt += f"{i}. **{char['name']}**\n"
            prompt += f"   - Type: {char['valueType']}\n"
            if char.get('description'):
                prompt += f"   - Description: {char['description']}\n"
            prompt += "\n"
        
        # Add instruction
        prompt += """## Instructions

1. Extract network requirements from the scenario (bandwidth, latency, availability, etc.)
2. Map each requirement to the MOST APPROPRIATE characteristic from the list above
3. Use the EXACT characteristic names as provided
4. Provide realistic values with appropriate units

"""
        
        # Optionally add few-shot examples
        if include_examples and EXAMPLE_SCENARIOS:
            prompt += f"""## Example Translation

**Scenario:** {EXAMPLE_SCENARIOS[0]['scenario']}

**TMF921 Intent:**
```json
{json.dumps(EXAMPLE_SCENARIOS[0]['intent'], indent=2)}
```

"""
        
        # Add output format
        prompt += f"""## Output Format

Generate valid JSON with this structure:

{{
  "name": "<descriptive intent name>",
  "description": "<what this intent achieves>",
  "serviceSpecCharacteristic": [
    {{
      "name": "<EXACT name from list above>",
      "value": {{
        "value": "<extracted value>",
        "unitOfMeasure": "<unit, e.g., 'kbps', 'ms', 'percent'>"
      }}
    }}
  ]
}}

**CRITICAL:** Use ONLY characteristic names from the retrieved list above.

**Output (JSON only):**
"""
        return prompt
    
    def build_system_prompt(self) -> str:
        """Build system prompt for LLM."""
        return """You are a telecommunications network configuration expert specializing in TMF921 Intent Management API standards. Your role is to translate natural language network requirements into precise, standards-compliant TMF921 Intent JSON structures.

You have deep knowledge of:
- TMF921 Intent Management API specification
- TMF GST (Generic Slice Template) for network slices
- 5G/6G network architecture and KPIs
- Telecommunications terminology and best practices

Your translations must be:
- Accurate: Correctly extract all requirements from natural language
- Compliant: Use only valid TMF921 characteristic names  
- Realistic: Values must be plausible for real telecom networks
- Complete: Cover all mentioned requirements
- Precise: Include appropriate units of measure

You MUST output valid JSON only, with no additional commentary."""


# Pre-defined high-quality examples for few-shot learning
EXAMPLE_SCENARIOS = [
    {
        "scenario": "Create a network slice for remote surgery with ultra-low latency (1ms), 99.999% reliability, and 100 Mbps guaranteed bandwidth.",
        "intent": {
            "name": "Remote Surgery Ultra-Reliable Low-Latency Network Slice",
            "description": "Mission-critical network slice for remote surgery applications requiring 1ms latency, 99.999% availability, and 100 Mbps guaranteed throughput",
            "serviceSpecCharacteristic": [
                {
                    "name": "Availability",
                    "value": {"value": "99.999", "unitOfMeasure": "percent"}
                },
                {
                    "name": "Downlink throughput per network slice: Guaranteed downlink throughput quota",
                    "value": {"value": "100000", "unitOfMeasure": "kbps"}
                },
                {
                    "name": "Uplink throughput per network slice: Guaranteed uplink throughput quota",
                    "value": {"value": " 100000", "unitOfMeasure": "kbps"}
                },
                {
                    "name": "E2E latency",
                    "value": {"value": "1", "unitOfMeasure": "ms"}
                }
            ]
        }
    },
    {
        "scenario": "Deploy IoT agricultural network requiring 1 Mbps bandwidth, 50ms latency tolerance, and coverage across 10,000 hectares.",
        "intent": {
            "name": "Agricultural IoT Network Slice",
            "description": "Wide-area IoT network slice for agricultural monitoring with 1 Mbps bandwidth, 50ms latency, covering 10,000 hectares",
            "serviceSpecCharacteristic": [
                {
                    "name": "Downlink throughput per network slice: Maximum downlink throughput",
                    "value": {"value": "1000", "unitOfMeasure": "kbps"}
                },
                {
                    "name": "E2E latency",
                    "value": {"value": "50", "unitOfMeasure": "ms"}
                },
                {
                    "name": "Coverage",
                    "value": {"value": "10000", "unitOfMeasure": "hectares"}
                }
            ]
        }
    },
    {
        "scenario": "Set up VPN for Finance department with 500 Mbps throughput, Gold isolation level, and military-grade encryption.",
        "intent": {
            "name": "Finance Department Secure VPN Slice",
            "description": "High-security VPN network slice for finance operations with 500 Mbps throughput, gold-level isolation, and military-grade encryption",
            "serviceSpecCharacteristic": [
                {
                    "name": "Downlink throughput per network slice: Maximum downlink throughput",
                    "value": {"value": "500000", "unitOfMeasure": "kbps"}
                },
                {
                    "name": "Uplink throughput per network slice: Maximum uplink throughput",
                    "value": {"value": "500000", "unitOfMeasure": "kbps"}
                },
                {
                    "name": "Isolation level",
                    "value": {"value": "Gold", "unitOfMeasure": "N/A"}
                },
                {
                    "name": "Security",
                    "value": {"value": "Military-grade encryption", "unitOfMeasure": "N/A"}
                }
            ]
        }
    }
]


if __name__ == "__main__":
    # Test prompt generation
    import json
    
    # Load GST
    with open('gst.json', 'r', encoding='utf-8') as f:
        gst_spec = json.load(f)
    
    builder = TMF921PromptBuilder(gst_spec)
    
    # Test scenario
    test_scenario = "Create a gaming slice with sub-20ms ping, 50 Mbps guaranteed, and 99.95% uptime for 10,000 concurrent players."
    
    print("=" * 80)
    print("ZERO-SHOT PROMPT")
    print("=" * 80)
    zero_shot = builder.build_zero_shot_prompt(test_scenario, include_examples_list=True)
    print(zero_shot[:1000])
    print("\n... (truncated) ...\n")
    
    print("=" * 80)
    print("FEW-SHOT PROMPT")
    print("=" * 80)
    few_shot = builder.build_few_shot_prompt(test_scenario, EXAMPLE_SCENARIOS, max_examples=2)
    print(few_shot[:1000])
    print("\n... (truncated) ...\n")
    
    print("=" * 80)
    print("CHAIN-OF-THOUGHT PROMPT")
    print("=" * 80)
    cot = builder.build_cot_prompt(test_scenario)
    print(cot)
    
    print("\n" + "=" * 80)
    print("SYSTEM PROMPT")
    print("=" * 80)
    print(builder.build_system_prompt())
