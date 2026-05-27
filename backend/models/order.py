"""Pydantic models for order data."""

from typing import List, Optional

from pydantic import BaseModel


class OrderItem(BaseModel):
    """A single line-item inside an order."""

    name: str
    category: str
    price: float
    quantity: int
    is_final_sale: bool


class Order(BaseModel):
    """Represents a customer order."""

    order_id: str
    customer_id: str
    items: List[OrderItem]
    order_date: str
    delivery_date: Optional[str] = None
    status: str  # delivered | in_transit | cancelled
    total_amount: float
    shipping_cost: float
    payment_method: str
