# GraphRAG Setup

This directory contains utilities for setting up the GraphRAG infrastructure.

## Files

- **`vector_embedding_tool.py`**: Utility class for generating and managing vector embeddings
- **`setup_graphrag.py`**: Setup script to initialize embeddings and vector indexes

## Usage

From the project root:

```bash
cd graphrag_setup
python setup_graphrag.py
```

This will:
1. Load the sentence-transformers model (all-MiniLM-L6-v2)
2. Generate embeddings for all medical entities
3. Create Neo4j vector indexes
4. Enable semantic search capabilities

**Note**: This is a one-time setup process, not used by the agent during queries.
