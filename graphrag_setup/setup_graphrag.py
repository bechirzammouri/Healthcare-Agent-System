"""
Setup script for GraphRAG pipeline
Generates embeddings and creates vector indexes using sentence-transformers
"""
import sys
from vector_embedding_tool import VectorEmbeddingManager


def main():
    """Setup GraphRAG infrastructure"""
    print("\n" + "="*70)
    print("GRAPHRAG SETUP - Generating Vector Embeddings")
    print("="*70)
    print("\nThis script will:")
    print("1. Generate vector embeddings for Conditions, Medications, Procedures, Observations, Encounter, CarePlan")
    print("2. Create vector indexes in Neo4j for similarity search")
    print("3. Enable semantic search capabilities")
    print("\nEmbedding Strategy:")
    print("- Primary: sentence-transformers (all-MiniLM-L6-v2) - NO API KEY REQUIRED")
    print("- Fallback: Hash-based embeddings if sentence-transformers unavailable")
    print("- Note: Tools will also fall back to sentence-transformers if OpenAI API missing")
    print("\nNote: This may take several minutes depending on data size.\n")
    
    proceed = input("Continue? (y/n): ")
    if proceed.lower() != 'y':
        print("Setup cancelled.")
        return 0
    
    try:
        # Initialize with sentence-transformers (no API key needed)
        manager = VectorEmbeddingManager(model_name="all-MiniLM-L6-v2")
        
        # Delete existing embeddings first
        print("\n⚠️  Deleting existing hash-based embeddings...")
        manager.delete_existing_embeddings()
        
        # Generate new embeddings with sentence-transformers
        manager.embed_all_nodes()
        manager.close()
        
        print("\n" + "="*70)
        print("✅ GraphRAG Setup Complete!")
        print("="*70)
        print("\nYou can now use:")
        print("- vector_similarity_search tool for semantic queries")
        print("- graph_traversal tool for complex graph navigation")
        print("- graphrag_retrieval tool for hybrid retrieval")
        print("\nRun 'python test_graphrag.py' to test the pipeline.")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nMake sure:")
        print("1. Neo4j is running and accessible")
        print("2. The database has been loaded with data")
        print("3. Required packages are installed (run: pip install -r requirements.txt)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
