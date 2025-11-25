"""
Setup RAG by indexing GST characteristics.

Run this before using RAG experiments.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tmf921.rag import GSTIndexer


def main():
    """Index GST characteristics for RAG."""
    print("\n" + "="*80)
    print("TMF921 RAG Setup - Indexing GST Characteristics")
    print("="*80 + "\n")
    
    indexer = GSTIndexer()
    
    # Show stats
    stats = indexer.get_stats()
    print("GST Specification:")
    print(f"  Total characteristics: {stats['total_characteristics']}")
    print(f"  With descriptions: {stats['has_descriptions']}")
    print(f"  Value types: {stats['value_types']}")
    
    # Create index
    print("\nCreating vector database...")
    collection = indexer.create_index()
    
    print("\n" + "="*80)
    print("Setup complete! RAG is ready to use.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
