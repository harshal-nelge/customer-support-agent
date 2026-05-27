"""
Customers router — exposes customer and order data for the admin dashboard.
"""

from fastapi import APIRouter

from backend.services.database import get_all_customers, get_all_orders

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
async def list_customers():
    """Return all customer profiles."""
    return [c.model_dump() for c in get_all_customers()]


@router.get("/orders")
async def list_orders():
    """Return all orders."""
    return [o.model_dump() for o in get_all_orders()]
