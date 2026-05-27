"""
Admin router — exposes agent reasoning logs and refund history.
"""

from fastapi import APIRouter

from backend.services.logger import (
    get_all_sessions,
    get_refund_history,
    get_session_log,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/logs")
async def list_all_logs():
    """Return reasoning logs for every session."""
    return get_all_sessions()


@router.get("/logs/{session_id}")
async def get_logs(session_id: str):
    """Return reasoning logs for a specific session."""
    logs = get_session_log(session_id)
    if not logs:
        return {"detail": "No logs found for this session."}
    return logs


@router.get("/refunds")
async def list_refund_history():
    """Return all refund decisions made by the agent."""
    return get_refund_history()
