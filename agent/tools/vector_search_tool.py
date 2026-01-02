"""
Vector Search Tool - Semantic similarity search using vector embeddings
"""
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, List, Union
from neo4j import GraphDatabase
import config
import os

# Try OpenAI embeddings first, fall back to sentence-transformers
_embeddings_instance = None
_using_sentence_transformers = False

def get_embeddings():
    """Get or create the embeddings instance with fallback"""
    global _embeddings_instance, _using_sentence_transformers
    
    if _embeddings_instance is None:
        # Try OpenAI first
        api_key = os.getenv("OPENAI_API_KEY") or config.OPENAI_API_KEY
        if api_key:
            try:
                from langchain_openai import OpenAIEmbeddings
                _embeddings_instance = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    openai_api_key=api_key
                )
                print("Using OpenAI embeddings")
            except Exception as e:
                print(f"OpenAI embeddings failed: {e}. Falling back to sentence-transformers.")
        
        # Fallback to sentence-transformers
        if _embeddings_instance is None:
            try:
                from sentence_transformers import SentenceTransformer
                _embeddings_instance = SentenceTransformer('all-MiniLM-L6-v2')
                _using_sentence_transformers = True
                print("Using sentence-transformers (fallback mode)")
            except Exception as e:
                print(f"Failed to load sentence-transformers: {e}")
                
    return _embeddings_instance


class VectorSearchInput(BaseModel):
    """Input schema for vector search tool"""
    query_text: str = Field(description="Natural language description to search for (e.g., 'diabetes', 'heart disease', 'pain medication')")
    node_type: str = Field(description="Type of node to search: 'condition', 'medication', 'procedure', 'observation'")
    limit: int = Field(default=5, description="Maximum number of similar results to return")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity score (0-1, higher is more similar)")


class VectorSearchTool(BaseTool):
    """Tool for semantic similarity search in the healthcare graph"""
    
    name: str = "vector_similarity_search"
    description: str = """
    Find medical concepts semantically similar to a query using vector embeddings.
    
    Use for: Fuzzy concept matching ("conditions like diabetes", "pain relievers").
    Don't use for: Specific IDs, complex multi-entity queries (use graphrag_retrieval), statistics.
    
    Node types: 'condition', 'medication', 'procedure', 'observation'.
    Returns: Similar items with scores.
    """
    args_schema: Type[BaseModel] = VectorSearchInput
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text"""
        embeddings = get_embeddings()
        if embeddings:
            if _using_sentence_transformers:
                # sentence-transformers returns numpy array
                import numpy as np
                embedding = embeddings.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            else:
                # OpenAI/LangChain embeddings
                return embeddings.embed_query(text)
        else:
            # Last resort fallback: simple hash-based embedding
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Create 384-dim vector from hash (matching all-MiniLM-L6-v2)
            vector = []
            for i in range(12):  # 12 * 32 = 384
                hash_obj = hashlib.sha256(f"{text}_{i}".encode())
                hash_bytes = hash_obj.digest()
                for byte in hash_bytes:
                    if len(vector) < 384:
                        vector.append((byte / 255.0) * 2 - 1)
            return vector[:384]
    
    def _run(
        self,
        query_text: str,
        node_type: str,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> str:
        """Execute vector similarity search"""
        
        # Generate embedding for query
        query_embedding = self._generate_embedding(query_text)
        
        # Map node type to label and index
        node_mappings = {
            "condition": ("Condition", "condition_embedding_index"),
            "medication": ("Medication", "medication_embedding_index"),
            "procedure": ("Procedure", "procedure_embedding_index"),
            "observation": ("Observation", "observation_embedding_index")
        }
        
        if node_type.lower() not in node_mappings:
            return f"Error: Unknown node type '{node_type}'. Use: condition, medication, procedure, or observation"
        
        label, index_name = node_mappings[node_type.lower()]
        
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        try:
            with driver.session() as session:
                # Vector similarity search query
                query = f"""
                    CALL db.index.vector.queryNodes(
                        $index_name,
                        $limit,
                        $query_embedding
                    )
                    YIELD node, score
                    WHERE score >= $threshold
                    RETURN node.code as code,
                           node.description as description,
                           score as similarity_score
                    ORDER BY score DESC
                """
                
                result = session.run(
                    query,
                    index_name=index_name,
                    limit=limit,
                    query_embedding=query_embedding,
                    threshold=similarity_threshold
                )
                
                records = list(result)
                
                if not records:
                    return f"No {node_type}s found with similarity >= {similarity_threshold}. Try lowering the threshold or using different search terms."
                
                # Format results
                formatted_results = []
                for record in records:
                    formatted_results.append({
                        "code": record["code"],
                        "description": record["description"],
                        "similarity_score": round(record["similarity_score"], 3)
                    })
                
                return str(formatted_results)
                
        except Exception as e:
            return f"Error executing vector search: {str(e)}"
        
        finally:
            driver.close()
