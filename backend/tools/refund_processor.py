"""
Tool: Refund Processor

Mock-processes a refund after the policy check has passed.
Records the decision in the reasoning logger.
"""

import uuid

from langchain_core.tools import tool

from backend.services import logger


@tool
def process_refund(
    order_id: str,
    item_name: str,
    refund_amount: float,
    customer_id: str,
    reason: str,
    status: str = "approved",
) -> str:
    """
    Process (or deny/escalate) a refund and record the decision.

    Args:
        order_id: The order ID.
        item_name: Name of the item being refunded.
        refund_amount: Dollar amount to refund.
        customer_id: The customer's ID.
        reason: Reason for refund/denial/escalation.
        status: One of 'approved', 'denied', or 'escalated'.

    Returns:
        A confirmation message with the refund ID and details.
    """
    refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"

    decision = {
        "refund_id": refund_id,
        "order_id": order_id,
        "customer_id": customer_id,
        "item_name": item_name,
        "amount": refund_amount,
        "status": status,
        "reason": reason,
    }
    logger.record_refund_decision(decision)

    if status == "approved":
        return (
            f"✅ Refund APPROVED\n"
            f"  Refund ID: {refund_id}\n"
            f"  Order: {order_id}\n"
            f"  Item: {item_name}\n"
            f"  Amount: ${refund_amount:,.2f}\n"
            f"  Refund will be credited to the original payment method "
            f"within 5–10 business days."
        )
    elif status == "escalated":
        return (
            f"⚠️ Refund ESCALATED to human supervisor\n"
            f"  Reference: {refund_id}\n"
            f"  Order: {order_id}\n"
            f"  Item: {item_name}\n"
            f"  Amount: ${refund_amount:,.2f}\n"
            f"  Reason: {reason}\n"
            f"  A supervisor will review and respond within 24–48 hours."
        )
    else:
        return (
            f"❌ Refund DENIED\n"
            f"  Reference: {refund_id}\n"
            f"  Order: {order_id}\n"
            f"  Item: {item_name}\n"
            f"  Reason: {reason}"
        )
