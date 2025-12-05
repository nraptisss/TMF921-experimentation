"""
Dataset Generation Script for TMF921 Intent Translation

Generates high-quality synthetic scenarios using a three-tier approach:
- Tier 1: Characteristic-driven (ensures all 87 GST chars covered)
- Tier 2: Domain-driven (realistic industry scenarios)
- Tier 3: Complexity-driven (hard/implicit scenarios)
"""

import json
import sys
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tmf921.core import OllamaClient, GSTSpecification


@dataclass
class GeneratedScenario:
    """A generated scenario with ground truth."""
    natural_language: str
    characteristics: List[Dict[str, Any]]
    difficulty: str  # easy, medium, hard
    tier: str  # tier1, tier2, tier3
    domain: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class DatasetGenerator:
    """Generate high-quality synthetic TMF921 intent scenarios."""
    
    # Industry domains with typical characteristics
    DOMAINS = {
        "gaming": {
            "description": "Online gaming and esports",
            "key_chars": ["Delay tolerance", "Jitter", "Packet loss rate", "Availability"],
            "typical_values": {"latency": "20ms", "jitter": "5ms", "availability": "99.9%"}
        },
        "healthcare": {
            "description": "Telemedicine and remote surgery",
            "key_chars": ["Availability", "Reliability", "Delay tolerance", "Security"],
            "typical_values": {"latency": "10ms", "availability": "99.999%", "reliability": "99.9999%"}
        },
        "manufacturing": {
            "description": "Smart factory and industrial IoT",
            "key_chars": ["Deterministic communication: Availability", "Delay tolerance", "Reliability"],
            "typical_values": {"latency": "5ms", "cycle_time": "10ms", "availability": "99.99%"}
        },
        "autonomous_vehicles": {
            "description": "Connected and autonomous vehicles (V2X)",
            "key_chars": ["Delay tolerance", "Reliability", "Positioning support", "V2X communication mode"],
            "typical_values": {"latency": "5ms", "reliability": "99.9999%", "positioning": "10cm"}
        },
        "video_streaming": {
            "description": "Live streaming and video on demand",
            "key_chars": ["Downlink throughput per network slice: Maximum downlink throughput", "Jitter", "Availability"],
            "typical_values": {"throughput": "50Mbps", "jitter": "30ms", "availability": "99.9%"}
        },
        "massive_iot": {
            "description": "Massive IoT deployments (sensors, meters)",
            "key_chars": ["Number of terminals", "Device velocity", "UE density"],
            "typical_values": {"devices": "1000000", "density": "1000000/km2"}
        },
        "smart_grid": {
            "description": "Power grid monitoring and control",
            "key_chars": ["Availability", "Synchronicity", "Reliability", "Delay tolerance"],
            "typical_values": {"availability": "99.99%", "latency": "20ms", "sync": "1us"}
        },
        "financial_trading": {
            "description": "High-frequency trading platforms",
            "key_chars": ["Delay tolerance", "Availability", "Jitter"],
            "typical_values": {"latency": "1ms", "availability": "99.999%", "jitter": "0.1ms"}
        },
        "emergency_services": {
            "description": "Public safety and first responders",
            "key_chars": ["Availability", "Slice priority level", "MMTel support"],
            "typical_values": {"availability": "99.999%", "priority": "1"}
        },
        "agriculture": {
            "description": "Smart farming and rural connectivity",
            "key_chars": ["Area of Service", "Coverage", "UE density"],
            "typical_values": {"coverage": "rural", "density": "low"}
        },
        "port_logistics": {
            "description": "Port automation and logistics",
            "key_chars": ["Positioning support", "Delay tolerance", "Reliability"],
            "typical_values": {"positioning": "10cm", "latency": "10ms"}
        },
        "stadium_events": {
            "description": "Large venue connectivity",
            "key_chars": ["Number of terminals", "Downlink throughput per network slice: Maximum downlink throughput"],
            "typical_values": {"users": "100000", "throughput": "1Gbps"}
        },
        "retail": {
            "description": "Smart retail and point of sale",
            "key_chars": ["Availability", "Security", "Downlink throughput per network slice: Maximum downlink throughput"],
            "typical_values": {"availability": "99.9%"}
        },
        "education": {
            "description": "Remote learning and campus networks",
            "key_chars": ["Area of Service", "Availability", "Downlink throughput per network slice: Maximum downlink throughput"],
            "typical_values": {"availability": "99%", "coverage": "campus"}
        },
        "mining": {
            "description": "Underground mining operations",
            "key_chars": ["Coverage", "Availability", "Positioning support"],
            "typical_values": {"coverage": "underground", "availability": "99.9%"}
        }
    }
    
    def __init__(self, model_name: str = "llama3:8b", gst_path: str = "gst.json"):
        self.client = OllamaClient(model=model_name)
        self.gst = GSTSpecification(gst_path)
        self.characteristics = self.gst.spec.get('serviceSpecCharacteristic', [])
        
        # Filter to only leaf characteristics (those with values)
        self.leaf_chars = [
            c for c in self.characteristics 
            if c.get('serviceSpecCharacteristicValue')
        ]
        
        print(f"[OK] Loaded {len(self.leaf_chars)} leaf characteristics from GST")
        
    def generate_tier1_scenarios(self, scenarios_per_char: int = 3) -> List[GeneratedScenario]:
        """Generate scenarios for each GST characteristic."""
        print(f"\n{'='*60}")
        print("TIER 1: Characteristic-Driven Generation")
        print(f"{'='*60}")
        print(f"Generating {scenarios_per_char} scenarios per characteristic...")
        
        all_scenarios = []
        
        for i, char in enumerate(self.leaf_chars, 1):
            char_name = char.get('name', '')
            char_desc = char.get('description', '')
            value_type = char.get('valueType', 'TEXT')
            
            # Get example values
            values = char.get('serviceSpecCharacteristicValue', [])
            example_values = []
            unit = "N/A"
            for v in values[:3]:
                if v.get('value'):
                    example_values.append(str(v['value'].get('value', '')))
                    if v.get('unitOfMeasure'):
                        unit = v['unitOfMeasure']
            
            print(f"\n[{i}/{len(self.leaf_chars)}] {char_name}")
            
            prompt = f"""You are generating training data for a network intent translation system.

TASK: Generate {scenarios_per_char} different natural language network requirements that would map to this GST characteristic.

CHARACTERISTIC:
- Name: {char_name}
- Description: {char_desc}
- Value Type: {value_type}
- Unit: {unit}
- Example Values: {', '.join(example_values) if example_values else 'varies'}

REQUIREMENTS:
1. Each scenario should sound like a real network operator request
2. Use different phrasing and vocabulary for each
3. Include realistic values appropriate for the characteristic
4. Vary difficulty: 1 easy (explicit value), 1 medium (some inference), 1 hard (implicit)
5. DO NOT use templated "Translate intent 'X' into: Y" format - use natural speech

OUTPUT: Return ONLY a valid JSON array with exactly {scenarios_per_char} objects:
[
  {{
    "natural_language": "requirement in plain English",
    "value": "the value to extract",
    "unit": "{unit}",
    "difficulty": "easy|medium|hard"
  }}
]"""

            try:
                response = self.client.generate(
                    prompt=prompt,
                    temperature=0.8,
                    max_tokens=1500
                )
                
                # Extract JSON from response
                json_data = self.client.extract_json(response['response'])
                
                if json_data and isinstance(json_data, list):
                    for item in json_data[:scenarios_per_char]:
                        scenario = GeneratedScenario(
                            natural_language=item.get('natural_language', ''),
                            characteristics=[{
                                "name": char_name,
                                "value": item.get('value', ''),
                                "unit": item.get('unit', unit)
                            }],
                            difficulty=item.get('difficulty', 'medium'),
                            tier='tier1'
                        )
                        all_scenarios.append(scenario)
                    print(f"  [OK] Generated {len(json_data)} scenarios")
                else:
                    print(f"  [FAIL] Could not parse response")
                    
            except Exception as e:
                print(f"  [ERROR] {e}")
            
            # Small delay to avoid overwhelming the model
            time.sleep(0.5)
        
        print(f"\n[TIER 1 COMPLETE] Generated {len(all_scenarios)} scenarios")
        return all_scenarios
    
    def generate_tier2_scenarios(self, scenarios_per_domain: int = 5) -> List[GeneratedScenario]:
        """Generate scenarios for each industry domain."""
        print(f"\n{'='*60}")
        print("TIER 2: Domain-Driven Generation")
        print(f"{'='*60}")
        print(f"Generating {scenarios_per_domain} scenarios per domain...")
        
        all_scenarios = []
        
        for i, (domain_name, domain_info) in enumerate(self.DOMAINS.items(), 1):
            print(f"\n[{i}/{len(self.DOMAINS)}] {domain_name.replace('_', ' ').title()}")
            
            key_chars = domain_info['key_chars']
            typical_values = domain_info['typical_values']
            
            prompt = f"""You are generating training data for a network intent translation system.

TASK: Generate {scenarios_per_domain} realistic network requirements from a {domain_name.replace('_', ' ')} industry stakeholder.

DOMAIN: {domain_info['description']}
KEY CHARACTERISTICS: {', '.join(key_chars)}
TYPICAL VALUES: {json.dumps(typical_values)}

REQUIREMENTS:
1. Sound like real business requests from this industry
2. Combine 2-4 characteristics naturally in each scenario
3. Use actual numeric values (not just "low" or "high")
4. Vary specificity: some exact values, some qualitative
5. Include context about WHY the requirement matters
6. DO NOT use templated formats - use natural conversational speech

OUTPUT: Return ONLY a valid JSON array:
[
  {{
    "natural_language": "the requirement in plain English with context",
    "characteristics": [
      {{"name": "exact GST characteristic name", "value": "value", "unit": "unit"}}
    ],
    "difficulty": "easy|medium|hard"
  }}
]"""

            try:
                response = self.client.generate(
                    prompt=prompt,
                    temperature=0.85,
                    max_tokens=2000
                )
                
                json_data = self.client.extract_json(response['response'])
                
                if json_data and isinstance(json_data, list):
                    for item in json_data[:scenarios_per_domain]:
                        chars = item.get('characteristics', [])
                        if not chars:
                            # Try to infer from key_chars
                            chars = [{"name": key_chars[0], "value": "inferred", "unit": ""}]
                        
                        scenario = GeneratedScenario(
                            natural_language=item.get('natural_language', ''),
                            characteristics=chars,
                            difficulty=item.get('difficulty', 'medium'),
                            tier='tier2',
                            domain=domain_name
                        )
                        all_scenarios.append(scenario)
                    print(f"  [OK] Generated {len(json_data)} scenarios")
                else:
                    print(f"  [FAIL] Could not parse response")
                    
            except Exception as e:
                print(f"  [ERROR] {e}")
            
            time.sleep(0.5)
        
        print(f"\n[TIER 2 COMPLETE] Generated {len(all_scenarios)} scenarios")
        return all_scenarios
    
    def generate_tier3_scenarios(self, num_scenarios: int = 30) -> List[GeneratedScenario]:
        """Generate hard/implicit scenarios."""
        print(f"\n{'='*60}")
        print("TIER 3: Complexity-Driven Generation")
        print(f"{'='*60}")
        print(f"Generating {num_scenarios} hard scenarios...")
        
        all_scenarios = []
        
        # Generate in batches of 10
        batches = num_scenarios // 10
        
        for batch in range(batches):
            print(f"\n[Batch {batch+1}/{batches}]")
            
            prompt = """You are generating HARD training scenarios for a network intent translation system.

TASK: Generate 10 challenging network requirements that require deeper reasoning.

SCENARIO TYPES TO INCLUDE:
1. IMPLICIT: Requirements that imply characteristics without stating them
   Example: "We need a gaming network" implies low latency, low jitter
2. RELATIVE: Requirements with relative values
   Example: "We need faster than our current 50ms latency"
3. QUALITATIVE: Requirements using descriptive terms
   Example: "Ultra-reliable connection for mission-critical operations"
4. INCOMPLETE: Requirements missing some expected details
   Example: "Video streaming service" without specifying bitrate
5. DOMAIN-SPECIFIC: Industry jargon requiring domain knowledge
   Example: "URLLC-grade service for factory automation"

REQUIREMENTS:
1. Each scenario should be genuinely challenging to parse
2. Include the ground truth characteristics that SHOULD be inferred
3. Use natural, conversational language
4. Cover different difficulty aspects

OUTPUT: Return ONLY a valid JSON array:
[
  {
    "natural_language": "the challenging requirement",
    "characteristics": [
      {"name": "exact GST characteristic", "value": "inferred value", "unit": "unit"}
    ],
    "difficulty": "hard",
    "reasoning": "why this is hard to parse"
  }
]"""

            try:
                response = self.client.generate(
                    prompt=prompt,
                    temperature=0.9,
                    max_tokens=2500
                )
                
                json_data = self.client.extract_json(response['response'])
                
                if json_data and isinstance(json_data, list):
                    for item in json_data:
                        scenario = GeneratedScenario(
                            natural_language=item.get('natural_language', ''),
                            characteristics=item.get('characteristics', []),
                            difficulty='hard',
                            tier='tier3'
                        )
                        all_scenarios.append(scenario)
                    print(f"  [OK] Generated {len(json_data)} scenarios")
                else:
                    print(f"  [FAIL] Could not parse response")
                    
            except Exception as e:
                print(f"  [ERROR] {e}")
            
            time.sleep(0.5)
        
        print(f"\n[TIER 3 COMPLETE] Generated {len(all_scenarios)} scenarios")
        return all_scenarios
    
    def save_scenarios(self, scenarios: List[GeneratedScenario], output_path: str):
        """Save scenarios to JSON file."""
        data = [s.to_dict() for s in scenarios]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVED] {len(scenarios)} scenarios to {output_path}")
    
    def extract_simple_scenarios(self, scenarios: List[GeneratedScenario]) -> List[str]:
        """Extract just the natural language for the main scenarios.json."""
        return [s.natural_language for s in scenarios if s.natural_language]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate TMF921 intent translation dataset")
    parser.add_argument("--tier", type=str, default="all", 
                        choices=["all", "tier1", "tier2", "tier3"],
                        help="Which tier to generate")
    parser.add_argument("--output", type=str, default="data/generated",
                        help="Output directory")
    parser.add_argument("--model", type=str, default="llama3:8b",
                        help="Ollama model to use")
    parser.add_argument("--tier1-per-char", type=int, default=3,
                        help="Scenarios per characteristic for Tier 1")
    parser.add_argument("--tier2-per-domain", type=int, default=5,
                        help="Scenarios per domain for Tier 2")
    parser.add_argument("--tier3-count", type=int, default=30,
                        help="Total scenarios for Tier 3")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    print("="*60)
    print("TMF921 Dataset Generator")
    print("="*60)
    generator = DatasetGenerator(model_name=args.model)
    
    all_scenarios = []
    
    # Generate Tier 1
    if args.tier in ["all", "tier1"]:
        tier1 = generator.generate_tier1_scenarios(args.tier1_per_char)
        generator.save_scenarios(tier1, str(output_dir / "tier1_characteristics.json"))
        all_scenarios.extend(tier1)
    
    # Generate Tier 2
    if args.tier in ["all", "tier2"]:
        tier2 = generator.generate_tier2_scenarios(args.tier2_per_domain)
        generator.save_scenarios(tier2, str(output_dir / "tier2_domains.json"))
        all_scenarios.extend(tier2)
    
    # Generate Tier 3
    if args.tier in ["all", "tier3"]:
        tier3 = generator.generate_tier3_scenarios(args.tier3_count)
        generator.save_scenarios(tier3, str(output_dir / "tier3_complexity.json"))
        all_scenarios.extend(tier3)
    
    # Save combined dataset with full metadata
    if all_scenarios:
        generator.save_scenarios(all_scenarios, str(output_dir / "combined_full.json"))
        
        # Also save simple format (just natural language strings)
        simple = generator.extract_simple_scenarios(all_scenarios)
        with open(output_dir / "scenarios_simple.json", 'w', encoding='utf-8') as f:
            json.dump(simple, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVED] {len(simple)} simple scenarios to {output_dir}/scenarios_simple.json")
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Total scenarios generated: {len(all_scenarios)}")
    
    # Difficulty distribution
    difficulties = {"easy": 0, "medium": 0, "hard": 0}
    for s in all_scenarios:
        difficulties[s.difficulty] = difficulties.get(s.difficulty, 0) + 1
    
    print(f"\nDifficulty distribution:")
    for d, count in difficulties.items():
        pct = (count / len(all_scenarios) * 100) if all_scenarios else 0
        print(f"  {d}: {count} ({pct:.1f}%)")
    
    print(f"\nOutput files in: {output_dir}/")


if __name__ == "__main__":
    main()
