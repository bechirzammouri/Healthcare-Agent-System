# Healthcare Agent API

FastAPI backend for the healthcare knowledge graph agent system.

## 🚀 Start the Application

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Start the Server

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or from the project root:

```bash
cd /home/bechir/GenAI-assesment
python -m uvicorn api.main:app --reload
```

The server will start at: **http://localhost:8000**

## 📡 API Endpoints

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/graph-info` | Graph metadata |
| POST | `/ask` | Query the agent |

## 🧪 Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Root Endpoint
```bash
curl http://localhost:8000/
```

### Graph Information
```bash
curl http://localhost:8000/graph-info
```

### Ask a Question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How many patients are in the database?"}'
```

### More Query Examples
```bash
# Top conditions
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top 5 most common conditions?"}'

# Top medications
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the most prescribed medications?"}'

# Patient demographics
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me patient demographics"}'
```

## ⚙️ Configuration

Ensure your `.env` file contains:

```env
GROQ_API_KEY=your_groq_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=healthcare123
```

## 🛑 Stop the Server

Press `CTRL+C` in the terminal running uvicorn.

## 📝 Response Format

### POST /ask Response
```json
{
  "query": "How many patients are in the database?",
  "answer": "There are 1000 patients in the database."
}
```

### GET /graph-info Response
```json
{
  "graph_name": "Healthcare Knowledge Graph",
  "total_nodes": 25000,
  "total_relationships": 50000,
  "node_types": {
    "Patient": 1000,
    "Encounter": 5000,
    ...
  },
  "relationship_types": {
    "HAD_ENCOUNTER": 5000,
    ...
  }
}
```
