"""Pydantic models for customer data."""

from pydantic import BaseModel


class Customer(BaseModel):
    """Represents a customer in the CRM."""

    id: str
    name: str
    email: str
    phone: str
    membership_tier: str  # standard | premium | vip
    account_created: str
    total_orders: int
    total_spent: float
    address: str
