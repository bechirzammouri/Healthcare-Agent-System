# Tool Testing Guide

This guide provides test queries for each tool in the agent system and the corresponding API commands to execute them.

## Prerequisites

1. Start the API server:
```bash
python api/main.py
# or
uvicorn api.main:app --reload --port 8000
```

2. Ensure Neo4j is running and populated with data
3. Verify `.env` file contains valid API keys and Neo4j credentials

---

## Test Queries by Tool

### 1. Neo4j Tool (`neo4j_tool.py`)
**Purpose:** Direct Cypher query execution against Neo4j database

**Test Query:** "Give me information about medication relevant to this id : 834060"

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Give me information about medication relevant to this id : 834060"}'
```

**Expected Behavior:** Agent should use Neo4j tool with medication_info query type

---

### 2. Analytics Tool (`analytics_tool.py`)
**Purpose:** Statistical analysis and aggregation queries

**Test Query:** "What are the top 5 most common diagnoses?"

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top 5 most common diagnoses?"}'
```

**Expected Behavior:** Agent should use Analytics tool for aggregation and ranking

---

### 3. Vector Search Tool (`vector_search_tool.py`)
**Purpose:** Semantic similarity search using embeddings

**Test Query:** "Find patients with symptoms similar to chest pain"

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find patients with symptoms similar to chest pain"}'
```

**Expected Behavior:** Agent should use Vector Search tool for semantic matching

---

### 4. Graph Traversal Tool (`graph_traversal_tool.py`)
**Purpose:** Relationship traversal and path finding

**Test Query:** "Show me the treatment path for patient with id : < id > "

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the treatment path for patient with id abf03ea9-2d1b-414e-8b07-5087c44bac8a"}'
```

**Expected Behavior:** Agent should use Graph Traversal tool to find connected nodes

---

### 5. GraphRAG Tool (`graphrag_tool.py`)
**Purpose:** Retrieval-augmented generation combining graph context with LLM reasoning

**Test Query:** "What medications are typically prescribed for hypertension based on our patient records?"

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What medications are typically prescribed for hypertension based on our patient records?"}'
```

**Expected Behavior:** Agent should use GraphRAG tool for context retrieval and synthesis

---

## Using Python Requests

```python
import requests

url = "http://localhost:8000/ask"

# Test Neo4j Tool
response = requests.post(url, json={
    "query": "How many patients are in the database?"
})
print(f"Response: {response.json()}")

# Test Analytics Tool
response = requests.post(url, json={
    "query": "What are the top 5 most common diagnoses?"
})
print(f"Response: {response.json()}")

# Test Vector Search Tool
response = requests.post(url, json={
    "query": "Find patients with symptoms similar to chest pain and shortness of breath"
})
print(f"Response: {response.json()}")

# Test Graph Traversal Tool
response = requests.post(url, json={
    "query": "Show me the treatment path for patient John Doe"
})
print(f"Response: {response.json()}")

# Test GraphRAG Tool
response = requests.post(url, json={
    "query": "What medications are typically prescribed for hypertension based on our patient records?"
})
print(f"Response: {response.json()}")
```

---

## Monitoring Tool Selection

To see which tool the agent selects for each query, you need to add logging in the agent orchestration layer. Modify [`agent/graph.py`](agent/graph.py) to log tool invocations.

Example logging addition:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In your agent execution loop:
logger.info(f"Agent selected tool: {tool_name}")
```

---

## Additional Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Graph Info
```bash
curl http://localhost:8000/graph-info
```

### API Documentation
Open browser: `http://localhost:8000/docs`
