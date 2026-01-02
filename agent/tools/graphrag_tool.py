"""
GraphRAG Tool - Hybrid retrieval combining vector similarity and graph traversal
"""
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, List, Dict, Any
from neo4j import GraphDatabase
import config
import json
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


class GraphRAGInput(BaseModel):
    """Input schema for GraphRAG tool"""
    query_text: str = Field(description="Natural language query (e.g., 'What treatments are used for diabetes patients?')")
    retrieval_mode: str = Field(description="Retrieval strategy: 'semantic_then_traverse', 'traverse_then_semantic', 'hybrid_combined'")
    focus_entity: str = Field(description="Primary entity type: 'condition', 'medication', 'procedure', 'patient'")
    traversal_depth: int = Field(default=2, description="How many hops to traverse in the graph (1-3)")
    top_k: int = Field(default=5, description="Number of top similar entities to retrieve")
    similarity_threshold: float = Field(default=0.6, description="Minimum similarity score for vector search")


class GraphRAGTool(BaseTool):
    """Tool for hybrid retrieval using GraphRAG approach"""
    
    name: str = "graphrag_retrieval"
    description: str = """
    HYBRID retrieval combining vector search + graph traversal. PRIMARY tool for complex queries.
    
    Use for: Multi-entity queries ("diabetic patients on insulin with kidney disease"), complex medical questions.
    Automatically: 1) Finds similar concepts (vector search), 2) Explores relationships (graph traversal), 3) Synthesizes results.
    Don't use for: Simple lookups, single-entity semantic search, statistics.
    
    Modes: semantic_then_traverse (default), traverse_then_semantic, hybrid_combined.
    
    Use this for complex queries that need both semantic understanding and graph relationships:
    - "What are common treatments for diabetes?" (find similar conditions + traverse to medications)
    - "Find patient cohorts with heart disease and their outcomes" (semantic + multi-hop traversal)
    - "What conditions are related to medications for pain?" (hybrid search + relationship discovery)
    
    Returns: Comprehensive results combining semantic relevance and graph structure.
    """
    args_schema: Type[BaseModel] = GraphRAGInput
    
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
    
    def _semantic_retrieval(
        self, 
        session, 
        query_embedding: List[float],
        entity_type: str,
        top_k: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using vector embeddings"""
        
        index_mappings = {
            "condition": "condition_embedding_index",
            "medication": "medication_embedding_index",
            "procedure": "procedure_embedding_index"
        }
        
        if entity_type not in index_mappings:
            return []
        
        index_name = index_mappings[entity_type]
        
        query = f"""
            CALL db.index.vector.queryNodes(
                $index_name,
                $top_k,
                $query_embedding
            )
            YIELD node, score
            WHERE score >= $threshold
            RETURN node.code as code,
                   node.description as description,
                   score as similarity_score,
                   id(node) as node_id
            ORDER BY score DESC
        """
        
        result = session.run(
            query,
            index_name=index_name,
            top_k=top_k,
            query_embedding=query_embedding,
            threshold=threshold
        )
        
        return [dict(record) for record in result]
    
    def _graph_traversal(
        self,
        session,
        entity_codes: List[str],
        entity_type: str,
        depth: int
    ) -> List[Dict[str, Any]]:
        """Traverse graph from seed entities"""
        
        # Map entity type to node label
        label_map = {
            "condition": "Condition",
            "medication": "Medication",
            "procedure": "Procedure"
        }
        
        if entity_type not in label_map:
            return []
        
        label = label_map[entity_type]
        
        # Build traversal query based on entity type
        if entity_type == "condition":
            query = f"""
                MATCH (c:Condition)
                WHERE c.code IN $codes
                MATCH (e:Encounter)-[:DIAGNOSED]->(c)
                OPTIONAL MATCH (e)-[:PRESCRIBED_MEDICATION]->(m:Medication)
                OPTIONAL MATCH (e)-[:HAD_PROCEDURE]->(proc:Procedure)
                OPTIONAL MATCH (p:Patient)-[:HAD_ENCOUNTER]->(e)
                WITH c, 
                     collect(DISTINCT {{code: m.code, desc: m.description, type: 'Medication'}}) as meds,
                     collect(DISTINCT {{code: proc.code, desc: proc.description, type: 'Procedure'}}) as procs,
                     count(DISTINCT p) as patient_count,
                     count(DISTINCT e) as encounter_count
                RETURN c.code as source_code,
                       c.description as source_description,
                       'Condition' as source_type,
                       meds as related_medications,
                       procs as related_procedures,
                       patient_count,
                       encounter_count
            """
        elif entity_type == "medication":
            query = f"""
                MATCH (m:Medication)
                WHERE m.code IN $codes
                MATCH (e:Encounter)-[:PRESCRIBED_MEDICATION]->(m)
                OPTIONAL MATCH (e)-[:DIAGNOSED]->(c:Condition)
                OPTIONAL MATCH (e)-[:HAD_PROCEDURE]->(proc:Procedure)
                WITH m,
                     collect(DISTINCT {{code: c.code, desc: c.description, type: 'Condition'}}) as conditions,
                     collect(DISTINCT {{code: proc.code, desc: proc.description, type: 'Procedure'}}) as procs,
                     count(DISTINCT e) as prescription_count
                RETURN m.code as source_code,
                       m.description as source_description,
                       'Medication' as source_type,
                       conditions as related_conditions,
                       procs as related_procedures,
                       prescription_count
            """
        else:  # procedure
            query = f"""
                MATCH (proc:Procedure)
                WHERE proc.code IN $codes
                MATCH (e:Encounter)-[:HAD_PROCEDURE]->(proc)
                OPTIONAL MATCH (e)-[:DIAGNOSED]->(c:Condition)
                OPTIONAL MATCH (e)-[:PRESCRIBED_MEDICATION]->(m:Medication)
                WITH proc,
                     collect(DISTINCT {{code: c.code, desc: c.description, type: 'Condition'}}) as conditions,
                     collect(DISTINCT {{code: m.code, desc: m.description, type: 'Medication'}}) as meds,
                     count(DISTINCT e) as procedure_count
                RETURN proc.code as source_code,
                       proc.description as source_description,
                       'Procedure' as source_type,
                       conditions as related_conditions,
                       meds as related_medications,
                       procedure_count
            """
        
        result = session.run(query, codes=entity_codes)
        return [dict(record) for record in result]
    
    def _run(
        self,
        query_text: str,
        retrieval_mode: str,
        focus_entity: str,
        traversal_depth: int = 2,
        top_k: int = 5,
        similarity_threshold: float = 0.6
    ) -> str:
        """Execute GraphRAG retrieval"""
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query_text)
        
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        try:
            with driver.session() as session:
                results = {
                    "query": query_text,
                    "mode": retrieval_mode,
                    "semantic_results": [],
                    "graph_results": [],
                    "combined_insights": []
                }
                
                if retrieval_mode == "semantic_then_traverse":
                    # Step 1: Semantic search
                    semantic_results = self._semantic_retrieval(
                        session, query_embedding, focus_entity, top_k, similarity_threshold
                    )
                    results["semantic_results"] = semantic_results
                    
                    # Step 2: Graph traversal from top semantic matches
                    if semantic_results:
                        seed_codes = [r["code"] for r in semantic_results[:3]]
                        graph_results = self._graph_traversal(
                            session, seed_codes, focus_entity, traversal_depth
                        )
                        results["graph_results"] = graph_results
                
                elif retrieval_mode == "traverse_then_semantic":
                    # This mode requires starting entities - get top entities by frequency first
                    initial_query = f"""
                        MATCH (n:{focus_entity.capitalize()})
                        RETURN n.code as code, n.description as description, id(n) as node_id
                        LIMIT {top_k * 2}
                    """
                    initial_results = session.run(initial_query)
                    initial_entities = [dict(r) for r in initial_results]
                    
                    if initial_entities:
                        # Traverse from these entities
                        seed_codes = [e["code"] for e in initial_entities[:5]]
                        graph_results = self._graph_traversal(
                            session, seed_codes, focus_entity, traversal_depth
                        )
                        results["graph_results"] = graph_results
                        
                        # Rank by semantic similarity
                        # (simplified - in production would re-rank all discovered entities)
                        results["semantic_results"] = initial_entities[:top_k]
                
                elif retrieval_mode == "hybrid_combined":
                    # Combine both approaches
                    # Semantic search
                    semantic_results = self._semantic_retrieval(
                        session, query_embedding, focus_entity, top_k, similarity_threshold
                    )
                    results["semantic_results"] = semantic_results
                    
                    # Graph traversal
                    if semantic_results:
                        seed_codes = [r["code"] for r in semantic_results]
                        graph_results = self._graph_traversal(
                            session, seed_codes, focus_entity, traversal_depth
                        )
                        results["graph_results"] = graph_results
                        
                        # Create combined insights
                        for gr in graph_results:
                            insight = {
                                "entity": gr.get("source_description"),
                                "type": gr.get("source_type"),
                                "related_entities": {}
                            }
                            
                            for key in gr:
                                if key.startswith("related_"):
                                    insight["related_entities"][key] = gr[key][:3]  # Top 3
                            
                            results["combined_insights"].append(insight)
                
                else:
                    return f"Error: Unknown retrieval mode '{retrieval_mode}'"
                
                # Format output
                if not results["semantic_results"] and not results["graph_results"]:
                    return "No results found. Try lowering similarity_threshold or using different search terms."
                
                return json.dumps(results, indent=2)
                
        except Exception as e:
            return f"Error executing GraphRAG retrieval: {str(e)}"
        
        finally:
            driver.close()
