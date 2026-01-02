"""
Neo4j Query Tool - Execute Cypher queries on the healthcare graph
"""
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from neo4j import GraphDatabase
import config


class Neo4jQueryInput(BaseModel):
    """Input schema for Neo4j query tool"""
    query_type: str = Field(description="Type of query: 'patient_history', 'medication_info', 'condition_lookup', 'encounter_details', 'custom'")
    patient_id: Optional[str] = Field(default=None, description="Patient ID (UUID) for patient-specific queries. Leave empty for random patient.")
    condition_code: Optional[str] = Field(default=None, description="Condition code or description keyword (e.g., 'diabetes', 'hypertension')")
    medication_code: Optional[str] = Field(default=None, description="Medication code or description keyword")
    encounter_id: Optional[str] = Field(default=None, description="Encounter ID to query")
    custom_cypher: Optional[str] = Field(default=None, description="Custom Cypher query (for advanced use)")
    limit: int = Field(default=10, description="Maximum number of results to return")


class Neo4jQueryTool(BaseTool):
    """Tool for querying the Neo4j healthcare knowledge graph"""
    
    name: str = "neo4j_query"
    description: str = """
    Query the healthcare knowledge graph using predefined query types or custom Cypher.
    Available query types:
    - patient_history: Get complete medical history for a patient. Can omit patient_id to get random patient.
    - medication_info: Get information about medications. Use medication_code for partial name match (e.g., 'insulin').
    - condition_lookup: Find patients with specific conditions. Use condition_code for keyword search (e.g., 'diabetes').
    - encounter_details: Get details about a specific medical encounter (requires encounter_id).
    - custom: Execute a custom Cypher query (requires custom_cypher).
    
    Note: Graph uses HAD_ENCOUNTER, DIAGNOSED, PRESCRIBED_MEDICATION relationships.
    """
    args_schema: Type[BaseModel] = Neo4jQueryInput
    
    def _run(
        self,
        query_type: str,
        patient_id: Optional[str] = None,
        condition_code: Optional[str] = None,
        medication_code: Optional[str] = None,
        encounter_id: Optional[str] = None,
        custom_cypher: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """Execute the Neo4j query"""
        
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        try:
            with driver.session() as session:
                # Query templates
                queries = {
                    "patient_history": """
                        MATCH (p:Patient)-[he:HAD_ENCOUNTER]->(e:Encounter)
                        WHERE $patient_id IS NULL OR p.id = $patient_id
                        OPTIONAL MATCH (e)-[r]->(n)
                        WHERE NOT n:Patient AND NOT n:Reason
                        RETURN p.id as patient_id,
                               p.firstName + ' ' + p.lastName as patient_name,
                               p.birthDate as birth_date,
                               e.date as encounter_date,
                               e.description as encounter_type,
                               type(r) as event_type,
                               labels(n)[0] as node_type,
                               n.description as event_description
                        ORDER BY e.date DESC
                        LIMIT $limit
                    """,
                    
                    "medication_info": """
                        MATCH (m:Medication)
                        WHERE $medication_code IS NULL OR m.code = $medication_code OR m.description CONTAINS $medication_code
                        OPTIONAL MATCH (e:Encounter)-[:PRESCRIBED_MEDICATION]->(m)
                        OPTIONAL MATCH (e)-[:DIAGNOSED]->(c:Condition)
                        WITH m, collect(DISTINCT c.description) as conditions
                        RETURN m.code as medication_code,
                               m.description as medication_name,
                               conditions as treats_conditions,
                               size(conditions) as condition_count
                        LIMIT $limit
                    """,
                    
                    "condition_lookup": """
                        MATCH (c:Condition)
                        WHERE c.code = $condition_code OR c.description CONTAINS $condition_code
                        MATCH (e:Encounter)-[:DIAGNOSED]->(c)
                        MATCH (p:Patient)-[:HAD_ENCOUNTER]->(e)
                        RETURN c.code as condition_code,
                               c.description as condition_name,
                               count(DISTINCT p) as patient_count,
                               collect(DISTINCT p.id)[0..$limit] as sample_patient_ids
                    """,
                    
                    "encounter_details": """
                        MATCH (e:Encounter {id: $encounter_id})
                        OPTIONAL MATCH (p:Patient)-[:HAD_ENCOUNTER]->(e)
                        OPTIONAL MATCH (e)-[r]->(n)
                        WHERE NOT n:Patient
                        RETURN p.firstName + ' ' + p.lastName as patient_name,
                               e.date as encounter_date,
                               e.description as encounter_type,
                               type(r) as relationship_type,
                               labels(n)[0] as related_node_type,
                               n.description as related_description
                    """,
                    
                    "custom": custom_cypher
                }
                
                # Select and execute query
                if query_type not in queries:
                    return f"Error: Unknown query type '{query_type}'"
                
                cypher_query = queries[query_type]
                params = {
                    "patient_id": patient_id,
                    "condition_code": condition_code,
                    "medication_code": medication_code,
                    "encounter_id": encounter_id,
                    "limit": limit
                }
                
                result = session.run(cypher_query, params)
                records = list(result)
                
                if not records:
                    return "No results found for the given query."
                
                # Format results
                formatted_results = []
                for record in records:
                    formatted_results.append(dict(record))
                
                return str(formatted_results)
                
        except Exception as e:
            return f"Error executing Neo4j query: {str(e)}"
        
        finally:
            driver.close()
