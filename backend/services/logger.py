"""
Agent reasoning logger.

Stores per-session reasoning traces so the admin dashboard
can display the agent's internal decision-making process.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


# ── In-memory store ──────────────────────────────────────────────────────────
# Keyed by session_id → list of log entries
_session_logs: Dict[str, List[Dict[str, Any]]] = {}

# Chronological list of all refund decisions (for admin overview)
_refund_history: List[Dict[str, Any]] = []


def log_step(
    session_id: str,
    step_type: str,
    detail: Any,
) -> None:
    """
    Append a reasoning step to the session log.

    Parameters
    ----------
    session_id : str
        Conversation session identifier.
    step_type : str
        Category such as "tool_call", "llm_response", "policy_check", "decision".
    detail : Any
        Arbitrary data (will be serialised to JSON by the API layer).
    """
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step_type": step_type,
        "detail": detail,
    }
    _session_logs.setdefault(session_id, []).append(entry)


def get_session_log(session_id: str) -> List[Dict[str, Any]]:
    """Return the full reasoning trace for a session."""
    return _session_logs.get(session_id, [])


def get_all_sessions() -> Dict[str, List[Dict[str, Any]]]:
    """Return logs for every session (admin overview)."""
    return dict(_session_logs)


def record_refund_decision(decision: Dict[str, Any]) -> None:
    """Persist a refund decision to the global history."""
    decision["timestamp"] = datetime.now(timezone.utc).isoformat()
    _refund_history.append(decision)


def get_refund_history() -> List[Dict[str, Any]]:
    """Return all refund decisions made so far."""
    return list(_refund_history)


def clear_session(session_id: str) -> None:
    """Remove logs for a specific session."""
    _session_logs.pop(session_id, None)
