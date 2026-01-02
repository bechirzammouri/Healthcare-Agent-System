"""
Graph Traversal Tool - Advanced graph navigation using complex Cypher queries
"""
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from neo4j import GraphDatabase
import config


class GraphTraversalInput(BaseModel):
    """Input schema for graph traversal tool"""
    traversal_type: str = Field(description="Type of traversal: 'patient_journey', 'condition_treatment_path', 'medication_interactions', 'similar_patient_cohort', 'temporal_patterns', 'custom'")
    patient_id: Optional[str] = Field(default=None, description="Patient ID for patient-specific traversals")
    condition_code: Optional[str] = Field(default=None, description="Condition code or description")
    medication_code: Optional[str] = Field(default=None, description="Medication code or description")
    max_hops: int = Field(default=3, description="Maximum relationship hops for graph traversal (1-5)")
    limit: int = Field(default=10, description="Maximum number of results")
    custom_cypher: Optional[str] = Field(default=None, description="Custom Cypher query for advanced traversals")


class GraphTraversalTool(BaseTool):
    """Tool for complex graph traversal and path finding in the healthcare graph"""
    
    name: str = "graph_traversal"
    description: str = """
    Navigate graph relationships to discover patterns and connections.
    
    Use for: Multi-hop navigation from known nodes ("patient X's medications", "treatment patterns for condition Y").
    Don't use for: Semantic search (use vector_similarity_search), complex queries needing both (use graphrag_retrieval).
    
    Traversal types: patient_journey, condition_treatment_path, medication_interactions, similar_patient_cohort, temporal_patterns, custom.
    """
    args_schema: Type[BaseModel] = GraphTraversalInput
    
    def _run(
        self,
        traversal_type: str,
        patient_id: Optional[str] = None,
        condition_code: Optional[str] = None,
        medication_code: Optional[str] = None,
        max_hops: int = 3,
        limit: int = 10,
        custom_cypher: Optional[str] = None
    ) -> str:
        """Execute graph traversal"""
        
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        try:
            with driver.session() as session:
                # Traversal query templates
                queries = {
                    "patient_journey": """
                        MATCH path = (p:Patient {id: $patient_id})-[:HAD_ENCOUNTER]->(e:Encounter)-[r*0..2]->(n)
                        WHERE NOT n:Patient
                        WITH p, e, 
                             [node IN nodes(path) WHERE NOT node:Patient AND NOT node:Encounter | 
                              {type: labels(node)[0], description: node.description, code: node.code}] as events,
                             e.date as encounter_date
                        RETURN p.firstName + ' ' + p.lastName as patient_name,
                               e.date as date,
                               e.description as encounter,
                               events
                        ORDER BY e.date DESC
                        LIMIT $limit
                    """,
                    
                    "condition_treatment_path": """
                        MATCH (c:Condition)
                        WHERE c.code = $condition_code OR c.description CONTAINS $condition_code
                        MATCH (e:Encounter)-[:DIAGNOSED]->(c)
                        OPTIONAL MATCH (e)-[:PRESCRIBED_MEDICATION]->(m:Medication)
                        OPTIONAL MATCH (e)-[:HAD_PROCEDURE]->(proc:Procedure)
                        WITH c, 
                             collect(DISTINCT {code: m.code, name: m.description}) as medications,
                             collect(DISTINCT {code: proc.code, name: proc.description}) as procedures
                        RETURN c.description as condition,
                               medications[0..10] as common_medications,
                               procedures[0..10] as common_procedures,
                               size(medications) as total_medication_count,
                               size(procedures) as total_procedure_count
                    """,
                    
                    "medication_interactions": """
                        MATCH (m1:Medication)
                        WHERE m1.code = $medication_code OR m1.description CONTAINS $medication_code
                        MATCH (e:Encounter)-[:PRESCRIBED_MEDICATION]->(m1)
                        MATCH (e)-[:PRESCRIBED_MEDICATION]->(m2:Medication)
                        WHERE m1 <> m2
                        WITH m1, m2, count(e) as co_prescription_count
                        ORDER BY co_prescription_count DESC
                        LIMIT $limit
                        MATCH (e2:Encounter)-[:PRESCRIBED_MEDICATION]->(m2)
                        MATCH (e2)-[:DIAGNOSED]->(c:Condition)
                        WITH m1, m2, co_prescription_count, 
                             collect(DISTINCT c.description)[0..5] as common_conditions
                        RETURN m1.description as medication,
                               m2.description as co_prescribed_medication,
                               co_prescription_count as times_prescribed_together,
                               common_conditions as conditions_treated_together
                    """,
                    
                    "similar_patient_cohort": """
                        MATCH (p1:Patient {id: $patient_id})-[:HAD_ENCOUNTER]->(e1:Encounter)-[:DIAGNOSED]->(c:Condition)
                        WITH p1, collect(DISTINCT c.code) as p1_conditions
                        MATCH (p2:Patient)-[:HAD_ENCOUNTER]->(e2:Encounter)-[:DIAGNOSED]->(c2:Condition)
                        WHERE p1 <> p2 AND c2.code IN p1_conditions
                        WITH p1, p2, 
                             collect(DISTINCT c2.description) as shared_conditions,
                             count(DISTINCT c2) as shared_condition_count
                        WHERE shared_condition_count >= 2
                        MATCH (p2)-[:HAD_ENCOUNTER]->(e3:Encounter)-[:PRESCRIBED_MEDICATION]->(m:Medication)
                        WITH p1, p2, shared_conditions, shared_condition_count,
                             collect(DISTINCT m.description)[0..5] as medications
                        RETURN p2.id as similar_patient_id,
                               p2.firstName + ' ' + p2.lastName as patient_name,
                               p2.birthDate as birth_date,
                               p2.gender as gender,
                               shared_condition_count as shared_conditions_count,
                               shared_conditions[0..5] as sample_shared_conditions,
                               medications as their_medications
                        ORDER BY shared_condition_count DESC
                        LIMIT $limit
                    """,
                    
                    "temporal_patterns": """
                        MATCH (p:Patient)-[:HAD_ENCOUNTER]->(e1:Encounter)-[:DIAGNOSED]->(c1:Condition)
                        MATCH (p)-[:HAD_ENCOUNTER]->(e2:Encounter)-[:DIAGNOSED]->(c2:Condition)
                        WHERE e1.date < e2.date AND c1 <> c2
                        WITH c1, c2, 
                             count(*) as sequence_count,
                             avg(duration.inDays(e1.date, e2.date).days) as avg_days_between
                        WHERE sequence_count >= 3
                        RETURN c1.description as initial_condition,
                               c2.description as subsequent_condition,
                               sequence_count as times_observed,
                               round(avg_days_between) as avg_days_between
                        ORDER BY sequence_count DESC
                        LIMIT $limit
                    """
                }
                
                # Select and execute query
                if traversal_type not in queries:
                    return f"Error: Unknown traversal type '{traversal_type}'"
                
                cypher_query = queries[traversal_type]
                if not cypher_query:
                    return "Error: custom traversal requires custom_cypher parameter"
                
                params = {
                    "patient_id": patient_id,
                    "condition_code": condition_code,
                    "medication_code": medication_code,
                    "max_hops": min(max_hops, 5),  # Cap at 5 to prevent performance issues
                    "limit": limit
                }
                
                result = session.run(cypher_query, params)
                records = list(result)
                
                if not records:
                    return f"No results found for {traversal_type} traversal with given parameters."
                
                # Format results
                formatted_results = []
                for record in records:
                    formatted_results.append(dict(record))
                
                return str(formatted_results)
                
        except Exception as e:
            return f"Error executing graph traversal: {str(e)}"
        
        finally:
            driver.close()
