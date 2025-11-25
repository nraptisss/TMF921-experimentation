"""
RAG Retriever - Semantic search for relevant GST characteristics.
"""

import chromadb
from typing import List, Dict, Any


class GSTRetriever:
    """Retrieve relevant GST characteristics using semantic search."""
    
    def __init__(self, db_path: str = "chroma_db", collection_name: str = "gst_characteristics"):
        """
        Initialize retriever.
        
        Args:
            db_path: Path to ChromaDB database
            collection_name: Name of the collection
        """
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(collection_name)
        
    def retrieve(
        self, 
        query: str, 
        n_results: int = 5,
        min_similarity: float = -1.0  # Allow negative similarities (distance > 1)
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant characteristics.
        
        Args:
            query: Search query (typically the scenario text)
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold (accepts negative values)
            
        Returns:
            List of characteristic dicts with metadata and similarity scores
        """
        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        characteristics = []
        for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
            similarity = 1 - distance  # Convert distance to similarity
            
            if similarity >= min_similarity:
                characteristics.append({
                    'name': metadata['name'],
                    'description': metadata['description'],
                    'valueType': metadata['valueType'],
                    'similarity': similarity
                })
        
        return characteristics
    
    def retrieve_for_scenario(
        self, 
        scenario: str, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve characteristics relevant to a specific scenario.
        
        Args:
            scenario: Natural language scenario description
            n_results: Number of characteristics to retrieve
            
        Returns:
            List of relevant characteristics
        """
        # Enhance query for better retrieval
        query = f"network slice requirements: {scenario}"
        
        return self.retrieve(query, n_results=n_results)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RAG Retriever Test")
    print("="*80 + "\n")
    
    # Initialize retriever
    retriever = GSTRetriever()
    
    # Test scenarios
    test_scenarios = [
        "Create a gaming slice with sub-20ms ping, 50 Mbps guaranteed, and 99.95% uptime for 10,000 concurrent players.",
        "Deploy IoT agricultural network requiring 1 Mbps bandwidth, 50ms latency tolerance, and coverage across 10,000 hectares.",
        "Provision remote surgery network with ultra-low latency (1ms), 99.999% reliability, and 100 Mbps guaranteed bandwidth."
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Scenario {i}: {scenario[:60]}...")
        print("-" * 80)
        
        characteristics = retriever.retrieve_for_scenario(scenario, n_results=5)
        
        print(f"\nRetrieved {len(characteristics)} characteristics:\n")
        for j, char in enumerate(characteristics, 1):
            print(f"{j}. {char['name']}")
            print(f"   Type: {char['valueType']}, Similarity: {char['similarity']:.3f}")
            if char['description']:
                print(f"   Description: {char['description'][:80]}...")
            print()
        
        print("="*80 + "\n")
