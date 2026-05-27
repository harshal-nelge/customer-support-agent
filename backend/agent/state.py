"""
Agent state definition for the LangGraph workflow.
"""

from typing import Annotated, List

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    State schema that flows through the LangGraph agent.

    Attributes
    ----------
    messages : list
        The conversation history (HumanMessage / AIMessage / ToolMessage).
        Uses the LangGraph `add_messages` reducer so new messages are
        appended rather than overwritten.
    session_id : str
        Unique identifier for this conversation session.
    """

    messages: Annotated[List, add_messages]
    session_id: str
