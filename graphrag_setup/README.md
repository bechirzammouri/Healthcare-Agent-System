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


## Test Queries

### Semantic-Then-Traverse Query
```bash
curl -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -d '{"query": "Find conditions similar to chronic kidney disease and show what medications are typically prescribed for them"}'
```

### Multi-Entity Complex Query
```bash
curl -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the common treatment pathways for heart-related conditions including medications and procedures?"}'
```

### Patient Cohort Discovery Query
```bash
curl -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -d '{"query": "Find patients with diabetes-like conditions who are on insulin treatments and show their common complications"}'
```
