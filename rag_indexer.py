"""
RAG Indexer - Create vector database for TMF921 GST characteristics.

Indexes all 87 service characteristics with semantic embeddings for retrieval.
"""

import json
from pathlib import Path
import chromadb
from chromadb.config import Settings


class GSTIndexer:
    """Index GST characteristics into vector database."""
    
    def __init__(self, gst_path: str = "gst.json", db_path: str = "chroma_db"):
        """
        Initialize indexer.
        
        Args:
            gst_path: Path to GST specification JSON
            db_path: Path to store ChromaDB database
        """
        self.gst_path = gst_path
        self.db_path = Path(db_path)
        
        # Load GST specification
        with open(gst_path, 'r', encoding='utf-8') as f:
            self.gst_spec = json.load(f)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
    def create_index(self, collection_name: str = "gst_characteristics"):
        """
        Create vector index for GST characteristics.
        
        Args:
            collection_name: Name for the ChromaDB collection
        """
        print(f"\n[1/3] Creating ChromaDB collection: {collection_name}")
        
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(collection_name)
            print("  [OK] Deleted existing collection")
        except:
            pass
        
        # Create new collection
        collection = self.client.create_collection(
            name=collection_name,
            metadata={"description": "TMF921 GST service characteristics"}
        )
        
        print(f"\n[2/3] Indexing characteristics...")
        
        # Prepare data for indexing
        characteristics = self.gst_spec.get('serviceSpecCharacteristic', [])
        
        documents = []
        metadatas = []
        ids = []
        
        for i, char in enumerate(characteristics):
            # Create rich document for embedding
            name = char.get('name', '')
            description = char.get('description', '')
            value_type = char.get('valueType', 'Unknown')
            
            # Combine name and description for better semantic search
            document = f"{name}. {description}"
            
            # Store full metadata
            metadata = {
                'name': name,
                'description': description,
                'valueType': value_type,
                'index': i
            }
            
            documents.append(document)
            metadatas.append(metadata)
            ids.append(f"char_{i}")
        
        # Add to collection (ChromaDB auto-generates embeddings)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"  [OK] Indexed {len(documents)} characteristics")
        
        print(f"\n[3/3] Validating index...")
        
        # Test query
        test_results = collection.query(
            query_texts=["network latency requirements"],
            n_results=3
        )
        
        print(f"  [OK] Test query successful")
        print(f"  Top result: {test_results['metadatas'][0][0]['name']}")
        
        print(f"\n[SUCCESS] Index created at: {self.db_path}/")
        
        return collection
    
    def get_stats(self):
        """Get indexing statistics."""
        chars = self.gst_spec.get('serviceSpecCharacteristic', [])
        
        value_types = {}
        for char in chars:
            vtype = char.get('valueType', 'Unknown')
            value_types[vtype] = value_types.get(vtype, 0) + 1
        
        return {
            'total_characteristics': len(chars),
            'value_types': value_types,
            'has_descriptions': sum(1 for c in chars if c.get('description')),
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TMF921 GST Characteristic Indexer - RAG Setup")
    print("="*80 + "\n")
    
    # Create indexer
    indexer = GSTIndexer()
    
    # Show statistics
    stats = indexer.get_stats()
    print("GST Specification:")
    print(f"  Total characteristics: {stats['total_characteristics']}")
    print(f"  With descriptions: {stats['has_descriptions']}")
    print(f"  Value types: {stats['value_types']}")
    
    # Create index
    collection = indexer.create_index()
    
    # Test retrieval
    print("\n" + "="*80)
    print("Testing Retrieval")
    print("="*80 + "\n")
    
    test_queries = [
        "latency requirements for real-time applications",
        "bandwidth and throughput for video streaming",
        "availability and reliability for mission critical",
        "coverage area for rural deployment"
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        print(f"Query: {query}")
        print(f"  Top results:")
        for i, (name, distance) in enumerate(zip(
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            similarity = 1 - distance  # Convert distance to similarity
            print(f"    {i}. {name['name']} (similarity: {similarity:.3f})")
        print()
    
    print("="*80)
    print("\n[SUCCESS] RAG index ready for use!")
    print("="*80 + "\n")
