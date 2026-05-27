"""
JSON and text-backed data access layer.

Loads customer, order, and policy data from files at module
initialisation and exposes query helpers used by agent tools.
"""

import json
from typing import Dict, List, Optional

from backend.config import settings
from backend.models.customer import Customer
from backend.models.order import Order


def _load_json(path) -> list | dict:
    """Load and parse a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_text(path) -> str:
    """Load a plain-text file."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# ── Eager load at import time ────────────────────────────────────────────────
_customers_raw: List[dict] = _load_json(settings.CUSTOMERS_FILE)
_orders_raw: List[dict] = _load_json(settings.ORDERS_FILE)

CUSTOMERS: List[Customer] = [Customer(**c) for c in _customers_raw]
ORDERS: List[Order] = [Order(**o) for o in _orders_raw]
POLICY_TEXT: str = _load_text(settings.POLICY_FILE)

# ── Lookup indices ───────────────────────────────────────────────────────────
_customer_by_id: Dict[str, Customer] = {c.id: c for c in CUSTOMERS}
_customer_by_email: Dict[str, Customer] = {c.email.lower(): c for c in CUSTOMERS}
_orders_by_customer: Dict[str, List[Order]] = {}
_order_by_id: Dict[str, Order] = {}

for order in ORDERS:
    _order_by_id[order.order_id] = order
    _orders_by_customer.setdefault(order.customer_id, []).append(order)


# ── Public query functions ───────────────────────────────────────────────────

def get_customer_by_id(customer_id: str) -> Optional[Customer]:
    """Look up a customer by their exact ID."""
    return _customer_by_id.get(customer_id.upper())


def get_customer_by_email(email: str) -> Optional[Customer]:
    """Look up a customer by email (case-insensitive)."""
    return _customer_by_email.get(email.lower())


def search_customer_by_name(name: str) -> List[Customer]:
    """Fuzzy-search customers by name substring (case-insensitive)."""
    needle = name.lower()
    return [c for c in CUSTOMERS if needle in c.name.lower()]


def get_order_by_id(order_id: str) -> Optional[Order]:
    """Look up a single order by order ID."""
    return _order_by_id.get(order_id.upper())


def get_orders_for_customer(customer_id: str) -> List[Order]:
    """Return all orders belonging to a customer."""
    return _orders_by_customer.get(customer_id.upper(), [])


def get_policy_text() -> str:
    """Return the full refund policy as plain text."""
    return POLICY_TEXT


def get_all_customers() -> List[Customer]:
    """Return every customer in the CRM."""
    return CUSTOMERS


def get_all_orders() -> List[Order]:
    """Return every order in the database."""
    return ORDERS
