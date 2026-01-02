"""
LangGraph agent workflow for healthcare query processing
"""
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools.neo4j_tool import Neo4jQueryTool
from agent.tools.analytics_tool import GraphAnalyticsTool
from agent.tools.vector_search_tool import VectorSearchTool
from agent.tools.graph_traversal_tool import GraphTraversalTool
from agent.tools.graphrag_tool import GraphRAGTool
import config


def get_llm():
    """Get the configured LLM"""
    try:
        if config.LLM_PROVIDER == "groq":
            return ChatGroq(
                api_key=config.GROQ_API_KEY,
                model_name=config.LLM_MODEL,
                temperature=config.TEMPERATURE
            )
    except Exception as e:
        raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}") from e


tools = [
    Neo4jQueryTool(), 
    GraphAnalyticsTool(),
    VectorSearchTool(),
    GraphTraversalTool(),
    GraphRAGTool()
]
tool_node = ToolNode(tools)
 
llm = get_llm()
llm_with_tools = llm.bind_tools(tools)


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Determine if we should continue to tools or end"""
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "end"
    return "tools"


def call_model(state: AgentState):
    """Call the LLM with the current state"""
    messages = state["messages"]
    
    # System message with instructions
    system_message = SystemMessage(content="""
    You are a helpful healthcare data assistant with access to a Neo4j knowledge graph.
    
    Your capabilities:
    1. Query patient medical histories using the neo4j_query tool
    2. Look up information about conditions and medications
    3. Compute statistics and analytics using the graph_analytics tool
    4. Perform semantic search using vector_similarity_search (find medically similar concepts)
    5. Execute complex graph traversals using graph_traversal (multi-hop relationships, patterns)
    6. Use GraphRAG hybrid retrieval with graphrag_retrieval (combines semantic + graph traversal)
    
    When answering questions:
    - Use the appropriate tool(s) to gather information from the graph
    - For semantic queries ("similar to", "related to"), use vector_similarity_search
    - For complex relationship queries, use graph_traversal or graphrag_retrieval
    - For comprehensive analysis, combine multiple tools
    - Provide clear, accurate answers based on the data
    - If you don't have enough information, ask clarifying questions
    - Format your responses in a user-friendly way
    
    Available query types for neo4j_query:
    - patient_history: Full medical history (needs patient_id)
    - medication_info: Medication details and what they treat
    - condition_lookup: Find patients with specific conditions
    - encounter_details: Details about specific medical encounters
    
    Vector similarity search supports:
    - condition, medication, procedure, observation, encounter, careplan nodes
    - Natural language queries for semantic matching
    
    Graph traversal types:
    - patient_journey: Complete medical timeline
    - condition_treatment_path: Treatment patterns for conditions
    - medication_interactions: Co-prescribed medications
    - similar_patient_cohort: Patients with similar histories
    - temporal_patterns: Sequential medical events
    
    GraphRAG retrieval modes:
    - semantic_then_traverse: Find similar entities, then explore graph
    - traverse_then_semantic: Graph exploration with semantic ranking
    - hybrid_combined: Simultaneous semantic + graph approach
    """)
    
    all_messages = [system_message] + list(messages)
    response = llm_with_tools.invoke(all_messages)
    
    return {"messages": [response]}


def create_agent():
    """Create and compile the LangGraph agent"""
    workflow = StateGraph(AgentState)
    
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    
    workflow.set_entry_point("agent")
    
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


agent = create_agent()


def run_agent(query: str) -> str:
    """Run the agent with a user query"""
    inputs = {
        "messages": [HumanMessage(content=query)]
    }
    
    result = agent.invoke(inputs)
    final_message = result["messages"][-1]
    return final_message.content
