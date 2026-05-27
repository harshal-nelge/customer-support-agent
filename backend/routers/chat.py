"""
Chat router — handles customer conversations with the agent.
"""

import uuid
from typing import Optional

from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from backend.agent.graph import agent_graph
from backend.services import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])

# ── In-memory session store (message history per session) ────────────────────
_sessions: dict[str, list] = {}


class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""

    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Agent's reply sent back to the frontend."""

    reply: str
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a user message through the LangGraph agent.

    If no session_id is provided, a new session is created.
    The agent's full message history is maintained per session.
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Retrieve or initialise session history
    history = _sessions.setdefault(session_id, [])

    # Log the incoming user message
    logger.log_step(session_id, "user_message", {
        "content": request.message,
    })

    # Append the new user message
    history.append(HumanMessage(content=request.message))

    # Run the agent graph
    result = agent_graph.invoke({
        "messages": history,
        "session_id": session_id,
    })

    # Update the session history with the full result
    _sessions[session_id] = result["messages"]

    # Extract the agent's final text reply
    agent_reply = result["messages"][-1].content

    logger.log_step(session_id, "final_response", {
        "content": agent_reply[:500],
    })

    return ChatResponse(reply=agent_reply, session_id=session_id)
