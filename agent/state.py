"""
State schema for the LangGraph agent
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """State of the agent workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    query_type: str
    tool_calls: list
    intermediate_results: dict
    final_answer: str
