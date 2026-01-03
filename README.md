# Healthcare Agent System - GenAI Assessment

LangGraph-based agentic AI system for querying a Neo4j healthcare knowledge graph.

## 📁 Project Structure

```
GenAI-assesment/
├── agent/                          # Agent system (LangGraph workflow + tools)
│   ├── __init__.py
│   ├── graph.py                   # LangGraph workflow & agent logic
│   ├── state.py                   # Agent state schema
│   └── tools/                     # Custom tools for graph queries
│       ├── __init__.py
│       ├── neo4j_tool.py         # Cypher query execution
│       ├── analytics_tool.py     # Graph statistics & analytics
│       ├── vector_search_tool.py # Semantic similarity search
│       ├── graph_traversal_tool.py # Multi-hop graph navigation
│       ├── graphrag_tool.py      # Hybrid retrieval (GraphRAG)
│       └── vector_embedding_tool.py # Embedding generation & management
│
├── api/                           # FastAPI backend
│   └── main.py                   # REST API endpoints
│
├── dataset/                       # Data & Neo4j documentation
│   ├── NEO4J_ARCHITECTURE.md     # Graph schema documentation
│   ├── DATA Overview.md          # Dataset overview
│   ├── cypher_test_queries.md    # Example Cypher queries
│   ├── data_exploring.ipynb      # Data exploration notebook
│   ├── data_sampling(suite).ipynb # Data sampling notebook
│   ├── explorations.ipynb        # Additional explorations
│   ├── sampled_data/             # CSV samples for Neo4j import
│   │   ├── sampled_patients.csv
│   │   ├── sampled_encounters.csv
│   │   ├── sampled_conditions.csv
│   │   ├── sampled_medications.csv
│   │   ├── sampled_procedures.csv
│   │   ├── sampled_observations.csv
│   │   ├── sampled_immunizations.csv
│   │   └── sampled_careplans.csv
│   └── SyntheticMass_Data/       # Original dataset
│
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
├── setup_graphrag.py             # GraphRAG setup script
├── test_graphrag.py              # GraphRAG tests
├── test_agent.py                 # Agent tests
├── test_agent_graphrag.py        # Agent + GraphRAG tests
├── test_neo4j_connection.py      # Neo4j connection test
├── test_llm_api.py               # LLM API test
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Create Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your API key
```

**Required in `.env`:**
```bash
GROQ_API_KEY=your_groq_api_key_here
NEO4J_PASSWORD=your_neo4j_password
```

**Get free Groq API key:** https://console.groq.com/

### 4. Run the Server

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: http://localhost:8000

## 🧪 Test the Agent

**API Docs:** http://localhost:8000/docs

**CLI Test:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top 5 most common conditions?"}'
```

**Python Test:**
```python
from agent import run_agent
print(run_agent("How many patients are in the database?"))
```

## 🛠️ Key Components

### Custom Tools
- **Neo4j Query Tool**: Patient history, medication info, condition lookup
- **Analytics Tool**: Statistics, demographics, top conditions/medications

### API Endpoints
- `POST /ask` - Query the agent
- `GET /graph-info` - Graph metadata
- `GET /health` - Health check

## 📊 Example Queries

```bash
# Top medications
"What are the most prescribed medications?"

# Patient history
"Show medical history for patient {patient_id}"

# Statistics
"How many patients have diabetes?"
```

## ✅ Tasks Completed

- [x] Task 1: Agentic AI with LangGraph + 5 custom tools
- [x] Task 2: Neo4j knowledge graph
- [x] Task 3: GraphRAG pipeline with vector search + graph traversal
- [x] Task 5: FastAPI with `/ask` and `/graph-info`

## 🔍 GraphRAG Features (Task 3)

This project implements a comprehensive **GraphRAG (Graph Retrieval-Augmented Generation)** pipeline:

### ⚙️ Current Implementation Status

**Important Note**: The current repository uses **hash-based embeddings** for vector storage due to storage and API cost limitations. This means:
- ✅ GraphRAG infrastructure is fully implemented and functional
- ✅ Vector indexes and retrieval pipeline are complete
- ⚠️ **Semantic similarity search is not yet available** (hash-based embeddings lack semantic understanding)
- 🔄 To enable true semantic search, run `setup_graphrag.py` with OpenAI API key or sentence-transformers

The system will work with basic graph queries and analytics, but semantic/similarity-based queries will have limited effectiveness until proper embeddings are generated.


### Vector Similarity Search
- Infrastructure for semantic search using embeddings
- Neo4j vector indexes created and ready
- ⚠️ **Currently using hash-based embeddings** (no semantic capability until proper embeddings generated)
- Supports conditions, medications, procedures, observations

### Graph Traversal
- Multi-hop relationship navigation ✅ (Fully functional)
- Pattern discovery (treatment paths, medication interactions) ✅
- Temporal analysis (disease progression sequences) ✅
- Patient cohort identification ✅

### Hybrid Retrieval
- GraphRAG infrastructure fully implemented ✅
- Multiple retrieval strategies (semantic-first, graph-first, hybrid)
- ⚠️ **Semantic component inactive** until embeddings are generated with `setup_graphrag.py`
- Graph traversal component fully operational

### Setup GraphRAG (Enable Semantic Search)

```bash
# Current state: Hash-based embeddings (no semantics)
# To enable true semantic search, run one of the following:

# Option 1: Free sentence-transformers (Recommended)
pip install sentence-transformers
python setup_graphrag.py  # Select 'y' when prompted

# Option 2: OpenAI embeddings (Best quality, requires API key)
# Add OPENAI_API_KEY to .env, then:
python setup_graphrag.py

# Test the pipeline
python test_graphrag.py
```

## 📚 More Info

- **Graph Schema**: `dataset/NEO4J_ARCHITECTURE.md`
- **Agent Details**: `agent/README.md`

