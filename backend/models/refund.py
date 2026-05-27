"""Pydantic models for refund request/response payloads."""

from typing import List, Optional

from pydantic import BaseModel


class RefundEligibilityResult(BaseModel):
    """Result of a single policy-rule check."""

    rule: str
    passed: bool
    detail: str


class RefundCheckResponse(BaseModel):
    """Aggregated result of all policy checks for a refund request."""

    eligible: bool
    requires_escalation: bool
    checks: List[RefundEligibilityResult]
    summary: str


class RefundResult(BaseModel):
    """Outcome of processing (or denying) a refund."""

    refund_id: Optional[str] = None
    status: str  # approved | denied | escalated
    amount: float
    reason: str
    customer_id: str
    order_id: str
    item_name: str
