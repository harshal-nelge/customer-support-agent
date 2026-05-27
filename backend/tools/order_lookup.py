"""
Tool: Order Lookup

Allows the agent to retrieve order details by order ID
or list all orders for a given customer.
"""

from langchain_core.tools import tool

from backend.services.database import get_order_by_id, get_orders_for_customer


@tool
def lookup_order(order_id: str) -> str:
    """
    Look up a specific order by its order ID.

    Args:
        order_id: The order identifier (e.g. 'ORD-2024-001').

    Returns:
        Order details as a formatted string, or error if not found.
    """
    order = get_order_by_id(order_id)
    if not order:
        return f"No order found with ID '{order_id}'. Please verify the order number."
    return _format_order(order)


@tool
def get_customer_orders(customer_id: str) -> str:
    """
    Retrieve all orders for a given customer.

    Args:
        customer_id: The customer ID (e.g. 'CUST001').

    Returns:
        A list of all orders for that customer, or a message if none found.
    """
    orders = get_orders_for_customer(customer_id)
    if not orders:
        return f"No orders found for customer '{customer_id}'."

    lines = [f"Orders for {customer_id} ({len(orders)} total):\n"]
    for o in orders:
        item_names = ", ".join(i.name for i in o.items)
        lines.append(
            f"  {o.order_id} | {o.order_date} | ${o.total_amount:,.2f} | "
            f"{o.status} | Items: {item_names}"
        )
    return "\n".join(lines)


def _format_order(o) -> str:
    """Format an Order object into a readable string."""
    items_str = ""
    for item in o.items:
        final_tag = " [FINAL SALE]" if item.is_final_sale else ""
        items_str += (
            f"\n    - {item.name} ({item.category}) "
            f"x{item.quantity} @ ${item.price:,.2f}{final_tag}"
        )

    return (
        f"Order Details:\n"
        f"  Order ID: {o.order_id}\n"
        f"  Customer ID: {o.customer_id}\n"
        f"  Order Date: {o.order_date}\n"
        f"  Delivery Date: {o.delivery_date or 'Not yet delivered'}\n"
        f"  Status: {o.status}\n"
        f"  Items:{items_str}\n"
        f"  Shipping Cost: ${o.shipping_cost:,.2f}\n"
        f"  Total Amount: ${o.total_amount:,.2f}\n"
        f"  Payment Method: {o.payment_method}"
    )
