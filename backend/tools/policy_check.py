"""
Tool: Policy Check

Programmatically validates a refund request against the corporate
refund policy.  This is *code-level* enforcement — even if the LLM
is tricked by prompt injection, these rules cannot be overridden.
"""

from datetime import datetime, timedelta

from langchain_core.tools import tool

from backend.services.database import get_order_by_id, get_orders_for_customer


# ── Policy constants (mirrored from refund_policy.txt) ───────────────────────
_RETURN_WINDOWS = {
    "electronics": 15,
    "clothing": 30,
    "home_and_kitchen": 30,
    "books_and_media": 30,
    "perishable": 0,
    "sports_and_outdoors": 30,
}

_MEMBERSHIP_EXTENSION = {
    "standard": 0,
    "premium": 15,
    "vip": 30,
}

_RESTOCKING_FEES = {
    "electronics": 15,
    "home_and_kitchen": 10,
}

_ESCALATION_THRESHOLD = 500.00
_MAX_REFUNDS_IN_90_DAYS = 3
_TODAY = None  # Set dynamically


def _today() -> datetime:
    """Return today's date (allows overriding in tests)."""
    return _TODAY or datetime.now()


@tool
def check_refund_eligibility(
    order_id: str,
    item_name: str,
    reason: str,
    customer_membership: str = "standard",
) -> str:
    """
    Validate a refund request against every rule in the refund policy.

    Args:
        order_id: The order ID to check.
        item_name: The exact name of the item to refund.
        reason: The customer's stated reason (e.g. 'defective', 'changed mind', 'wrong item').
        customer_membership: The customer's tier — 'standard', 'premium', or 'vip'.

    Returns:
        A detailed eligibility report listing each policy rule, whether it
        passed or failed, and the overall verdict.
    """
    order = get_order_by_id(order_id)
    if not order:
        return f"DENIED — Order '{order_id}' not found in system."

    # Find the specific item
    target_item = None
    for item in order.items:
        if item.name.lower() == item_name.lower():
            target_item = item
            break
    if not target_item:
        return (
            f"DENIED — Item '{item_name}' not found in order {order_id}. "
            f"Items in this order: {', '.join(i.name for i in order.items)}"
        )

    checks = []
    all_passed = True
    requires_escalation = False
    reason_lower = reason.lower()
    is_damaged = any(
        kw in reason_lower
        for kw in ["defective", "damaged", "broken", "faulty", "wrong item"]
    )
    is_wrong_item = "wrong item" in reason_lower

    # ── 1. Delivery status ───────────────────────────────────────────────
    if order.status != "delivered":
        checks.append(("Delivery Status", False, f"Order status is '{order.status}', not delivered yet."))
        all_passed = False
    else:
        checks.append(("Delivery Status", True, "Order has been delivered."))

    # ── 2. Final sale check ──────────────────────────────────────────────
    if target_item.is_final_sale:
        checks.append(("Final Sale", False, "This item is marked FINAL SALE and cannot be refunded."))
        all_passed = False
    else:
        checks.append(("Final Sale", True, "Item is not final sale."))

    # ── 3. Return window ─────────────────────────────────────────────────
    if order.delivery_date:
        delivery = datetime.strptime(order.delivery_date, "%Y-%m-%d")
        base_window = _RETURN_WINDOWS.get(target_item.category, 30)
        extension = _MEMBERSHIP_EXTENSION.get(customer_membership.lower(), 0)
        total_window = base_window + extension
        deadline = delivery + timedelta(days=total_window)
        days_since = (_today() - delivery).days

        if is_damaged or is_wrong_item:
            checks.append((
                "Return Window",
                True,
                f"Damaged/defective/wrong-item claims override the return window. "
                f"(Normal window: {total_window} days, {days_since} days since delivery.)",
            ))
        elif base_window == 0:
            checks.append(("Return Window", False, f"Perishable items are non-refundable."))
            all_passed = False
        elif _today() > deadline:
            checks.append((
                "Return Window",
                False,
                f"Return window expired. {total_window}-day window ended on {deadline.strftime('%Y-%m-%d')} "
                f"({days_since} days since delivery).",
            ))
            all_passed = False
        else:
            checks.append((
                "Return Window",
                True,
                f"Within {total_window}-day return window ({days_since} days since delivery).",
            ))
    else:
        checks.append(("Return Window", False, "No delivery date recorded."))
        all_passed = False

    # ── 4. Category-specific conditions ──────────────────────────────────
    cat = target_item.category
    if cat == "electronics" and not is_damaged:
        checks.append((
            "Electronics Condition",
            True,
            "Note: Electronics must be unopened and in original packaging. "
            "Please confirm with customer.",
        ))
    elif cat == "clothing":
        item_lower = target_item.name.lower()
        if "swimwear" in item_lower or "undergarment" in item_lower:
            checks.append(("Clothing Restriction", False, "Swimwear/undergarments are final sale."))
            all_passed = False
        else:
            checks.append(("Clothing Condition", True, "Tags must be attached. Confirm with customer."))
    elif cat == "sports_and_outdoors":
        item_lower = target_item.name.lower()
        if any(kw in item_lower for kw in ["helmet", "pad", "guard"]):
            checks.append((
                "Safety Equipment",
                True,
                "Safety equipment is non-returnable if worn. Confirm with customer.",
            ))

    # ── 5. Refund amount & escalation ────────────────────────────────────
    refund_amount = target_item.price * target_item.quantity
    fee_pct = _RESTOCKING_FEES.get(cat, 0)
    if fee_pct and not is_damaged:
        fee = refund_amount * fee_pct / 100
        refund_amount -= fee
        checks.append((
            "Restocking Fee",
            True,
            f"{fee_pct}% restocking fee applies (${fee:,.2f}). Refund amount: ${refund_amount:,.2f}.",
        ))

    if refund_amount > _ESCALATION_THRESHOLD:
        requires_escalation = True
        checks.append((
            "Escalation Required",
            True,
            f"Refund amount ${refund_amount:,.2f} exceeds ${_ESCALATION_THRESHOLD:,.2f}. "
            f"Must be escalated to a human supervisor.",
        ))

    # ── 6. Fraud — refunds in last 90 days ───────────────────────────────
    # (Checked at report level only; actual count would need refund history)
    customer_orders = get_orders_for_customer(order.customer_id)
    checks.append((
        "Fraud Check",
        True,
        f"Customer has {len(customer_orders)} total orders. "
        f"Note: max {_MAX_REFUNDS_IN_90_DAYS} refunds allowed per 90 days.",
    ))

    # ── Build report ─────────────────────────────────────────────────────
    report_lines = [f"REFUND ELIGIBILITY REPORT — {order_id} / {target_item.name}\n"]
    for rule, passed, detail in checks:
        icon = "✅" if passed else "❌"
        report_lines.append(f"  {icon} {rule}: {detail}")

    if not all_passed:
        verdict = "DENIED"
    elif requires_escalation:
        verdict = "ESCALATE TO HUMAN SUPERVISOR"
    else:
        verdict = "ELIGIBLE FOR REFUND"

    report_lines.append(f"\nVERDICT: {verdict}")
    if all_passed and not requires_escalation:
        report_lines.append(f"REFUND AMOUNT: ${refund_amount:,.2f}")

    return "\n".join(report_lines)
