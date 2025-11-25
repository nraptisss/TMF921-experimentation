"""
Test Ollama Cloud model (gpt-oss:20b-cloud).

Make sure you've signed into Ollama Cloud first:
    ollama signin
"""

from llm_client import OllamaClient
from prompt_templates import TMF921PromptBuilder, EXAMPLE_SCENARIOS
from data_processor import GSTSpecification
import time

print("\n" + "="*80)
print("Testing Ollama Cloud Model: gpt-oss:20b-cloud")
print("="*80 + "\n")

# Initialize
print("[1/4] Setting up components...")
gst = GSTSpecification("gst.json")
prompt_builder = TMF921PromptBuilder(gst.spec)

# Test with cloud model
print("\n[2/4] Initializing cloud model...")
print("Note: You must be signed into Ollama Cloud (run: ollama signin)")

client = OllamaClient(model="gpt-oss:20b-cloud")

if not client._check_connection():
    print("[ERROR] Cannot connect to Ollama")
    print("Make sure Ollama is running and you're signed in:")
    print("  ollama signin")
    exit(1)

print(f"[OK] Connected to Ollama with model: {client.model}")

# Test scenario
test_scenario = "Deploy IoT sensor network: 1 Mbps per device, 500ms latency tolerance, 99.9% availability, 10,000 sensors."

print(f"\n[3/4] Testing translation...")
print(f"Scenario: {test_scenario}")
print("-" * 80)

# Build prompt
system_prompt = prompt_builder.build_system_prompt()
user_prompt = prompt_builder.build_few_shot_prompt(
    test_scenario,
    EXAMPLE_SCENARIOS[:2],
    max_examples=2
)

# Time the generation
start = time.time()

try:
    response = client.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.1,
        max_tokens=2048
    )
    
    elapsed = time.time() - start
    
    print(f"\n[OK] Generation completed!")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Tokens: {response['tokens']}")
    print(f"  Tokens/sec: {response['tokens']/elapsed:.1f}")
    
    # Extract and display result
    intent_json = client.extract_json(response['response'])
    
    if intent_json:
        print(f"\n[SUCCESS] Generated TMF921 Intent:")
        print(f"  Name: {intent_json.get('name', 'N/A')}")
        print(f"  Characteristics: {len(intent_json.get('serviceSpecCharacteristic', []))}")
        for char in intent_json.get('serviceSpecCharacteristic', [])[:3]:
            print(f"    - {char['name']}: {char['value']['value']} {char['value'].get('unitOfMeasure', '')}")
    else:
        print(f"\n[WARN] Could not extract JSON")
        print(f"Response preview: {response['response'][:200]}...")

except Exception as e:
    print(f"\n[ERROR] Generation failed: {str(e)}")
    print("\nCommon issues:")
    print("  - Not signed into Ollama Cloud: run 'ollama signin'")
    print("  - Model not pulled: run 'ollama pull gpt-oss:20b-cloud'")
    print("  - Network issues: check internet connection")

print("\n[4/4] Comparison with local model:")
print("-" * 80)
print(f"  Cloud (gpt-oss:20b-cloud):  {elapsed:.1f}s")
print(f"  Local (llama3:latest):      ~90-100s")
print(f"  Speedup:                    ~{90/elapsed:.1f}x faster")

print("\n" + "="*80)
print("\nIf test succeeded, you can now use this model for experiments!")
print("Update validation scripts to use: OllamaClient(model='gpt-oss:20b-cloud')")
print("="*80 + "\n")
