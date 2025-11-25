"""Test RAG retriever with actual scenarios from checkpoint."""
from rag_retriever import GSTRetriever
import json

retriever = GSTRetriever()

# Test scenarios from checkpoint_10
test_scenarios = [
    "Set up virtual court proceedings: 20 Mbps per courtroom, 50ms latency, secure encrypted recording.",
    "Configure connected sports venue concessions: 50 Mbps per venue, 100ms latency, food sales.",
    "Configure connected food supplier network: 100 Mbps backbone, 500ms latency tolerance, ordering.",
]

print("\n" + "="*80)
print("RAG RETRIEVAL DEBUG TEST")
print("="*80 + "\n")

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\nScenario {i}: {scenario[:60]}...")
    print("-" * 80)
    
    # Test with different n_results and thresholds
    for n in [5, 8, 10]:
        chars = retriever.retrieve_for_scenario(scenario, n_results=n)
        print(f"  n_results={n}: Retrieved {len(chars)} characteristics")
        if chars:
            print(f"    Top 3:")
            for char in chars[:3]:
                print(f"      - {char['name']} (sim: {char['similarity']:.3f})")
    
    # Test with lower similarity threshold
    print(f"\n  Testing with different thresholds:")
    for threshold in [0.0, -0.5, -1.0]:
        chars = retriever.retrieve(
            f"network slice requirements: {scenario}",
            n_results=8,
            min_similarity=threshold
        )
        print(f"    threshold={threshold}: {len(chars)} results")

print("\n" + "="*80 + "\n")
