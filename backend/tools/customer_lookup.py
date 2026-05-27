"""
Tool: Customer Lookup

Allows the agent to find a customer by ID, email, or name.
"""

from langchain_core.tools import tool

from backend.services.database import (
    get_customer_by_email,
    get_customer_by_id,
    search_customer_by_name,
)


@tool
def lookup_customer(identifier: str) -> str:
    """
    Look up a customer by their ID, email address, or name.

    Args:
        identifier: Customer ID (e.g. 'CUST001'), email, or full/partial name.

    Returns:
        Customer details as a formatted string, or an error message if not found.
    """
    # Try ID first
    customer = get_customer_by_id(identifier)
    if customer:
        return _format_customer(customer)

    # Try email
    if "@" in identifier:
        customer = get_customer_by_email(identifier)
        if customer:
            return _format_customer(customer)

    # Try name search
    matches = search_customer_by_name(identifier)
    if matches:
        if len(matches) == 1:
            return _format_customer(matches[0])
        results = [f"- {c.id}: {c.name} ({c.email})" for c in matches]
        return (
            f"Found {len(matches)} customers matching '{identifier}':\n"
            + "\n".join(results)
            + "\nPlease ask the customer to confirm their exact name or provide their ID/email."
        )

    return f"No customer found matching '{identifier}'. Please verify the information and try again."


def _format_customer(c) -> str:
    """Format a Customer object into a readable string."""
    return (
        f"Customer Found:\n"
        f"  ID: {c.id}\n"
        f"  Name: {c.name}\n"
        f"  Email: {c.email}\n"
        f"  Phone: {c.phone}\n"
        f"  Membership: {c.membership_tier.upper()}\n"
        f"  Account Since: {c.account_created}\n"
        f"  Total Orders: {c.total_orders}\n"
        f"  Total Spent: ${c.total_spent:,.2f}"
    )
