"""
FastAPI backend for the healthcare agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent.graph import run_agent
from neo4j import GraphDatabase
import config
import json


class PrettyJSONResponse(JSONResponse):
    """Custom JSON response with pretty formatting"""
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            separators=(", ", ": "),
        ).encode("utf-8")


app = FastAPI(
    title="Healthcare Agent API",
    description="Agentic AI system for healthcare knowledge graph queries",
    version="1.0.0",
    default_response_class=PrettyJSONResponse
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """Request model for /ask endpoint"""
    query: str


class QueryResponse(BaseModel):
    """Response model for /ask endpoint"""
    query: str
    answer: str


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Healthcare Agent API",
        "endpoints": {
            "/ask": "POST - Ask a question to the agent",
            "/graph-info": "GET - Get graph metadata"
        }
    }


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question to the healthcare agent
    
    The agent will use available tools to query the Neo4j knowledge graph
    and provide an informed answer.
    """
    try:
        answer = run_agent(request.query)
        return QueryResponse(query=request.query, answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph-info")
async def get_graph_info():
    """
    Get metadata about the knowledge graph
    
    Returns node counts, relationship counts, and basic statistics
    """
    driver = GraphDatabase.driver(
        config.NEO4J_URI,
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    )
    
    try:
        with driver.session() as session:
            # Get node counts
            node_count_query = """
                MATCH (n)
                RETURN labels(n)[0] as node_type, count(n) as count
                ORDER BY count DESC
            """
            node_counts = session.run(node_count_query)
            nodes = {record["node_type"]: record["count"] for record in node_counts}
            
            # Get relationship counts
            rel_count_query = """
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """
            rel_counts = session.run(rel_count_query)
            relationships = {record["relationship_type"]: record["count"] for record in rel_counts}
            
            # Get total counts
            total_nodes = sum(nodes.values())
            total_relationships = sum(relationships.values())
            
            return {
                "graph_name": "Healthcare Knowledge Graph",
                "total_nodes": total_nodes,
                "total_relationships": total_relationships,
                "node_types": nodes,
                "relationship_types": relationships,
                "neo4j_uri": config.NEO4J_URI
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        driver.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
