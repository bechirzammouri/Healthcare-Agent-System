"""
Graph Analytics Tool - Compute statistics and patterns from the healthcare graph
"""
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from neo4j import GraphDatabase
import config


class AnalyticsInput(BaseModel):
    """Input schema for analytics tool"""
    analysis_type: str = Field(description="Type of analysis: 'node_counts', 'top_conditions', 'top_medications', 'patient_demographics', 'encounter_stats'")
    limit: int = Field(default=10, description="Number of results to return for rankings")


class GraphAnalyticsTool(BaseTool):
    """Tool for computing statistics and analytics from the graph"""
    
    name: str = "graph_analytics"
    description: str = """
    Compute statistics and analytics from the healthcare knowledge graph.
    Available analysis types:
    - node_counts: Count of each node type in the graph
    - top_conditions: Most common medical conditions
    - top_medications: Most frequently prescribed medications
    - patient_demographics: Age and gender distribution
    - encounter_stats: Encounter frequency and types
    """
    args_schema: Type[BaseModel] = AnalyticsInput
    
    def _run(self, analysis_type: str, limit: int = 10) -> str:
        """Execute the analytics query"""
        
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        try:
            with driver.session() as session:
                queries = {
                    "node_counts": """
                        MATCH (n)
                        RETURN labels(n)[0] as node_type, count(n) as count
                        ORDER BY count DESC
                    """,
                    
                    "top_conditions": """
                        MATCH (c:Condition)<-[:DIAGNOSED]-(e:Encounter)
                        RETURN c.description as condition, count(e) as diagnosis_count
                        ORDER BY diagnosis_count DESC
                        LIMIT $limit
                    """,
                    
                    "top_medications": """
                        MATCH (m:Medication)<-[:PRESCRIBED_MEDICATION]-(e:Encounter)
                        RETURN m.description as medication, count(e) as prescription_count
                        ORDER BY prescription_count DESC
                        LIMIT $limit
                    """,
                    
                    "patient_demographics": """
                        MATCH (p:Patient)
                        RETURN p.gender as gender,
                               count(p) as count,
                               avg(duration.between(p.birthDate, COALESCE(p.deathDate, date())).years) as avg_age
                        ORDER BY count DESC
                    """,
                    
                    "encounter_stats": """
                        MATCH (e:Encounter)
                        RETURN e.description as encounter_type,
                               count(e) as count
                        ORDER BY count DESC
                        LIMIT $limit
                    """
                }
                
                if analysis_type not in queries:
                    return f"Error: Unknown analysis type '{analysis_type}'"
                
                result = session.run(queries[analysis_type], {"limit": limit})
                records = list(result)
                
                if not records:
                    return "No data found for analysis."
                
                # Format results
                formatted_results = []
                for record in records:
                    formatted_results.append(dict(record))
                
                return str(formatted_results)
                
        except Exception as e:
            return f"Error executing analytics query: {str(e)}"
        
        finally:
            driver.close()
