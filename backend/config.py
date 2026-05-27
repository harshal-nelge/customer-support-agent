"""
Application configuration.

Loads environment variables via python-dotenv and exposes
typed settings for the rest of the application.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Load .env from project root ──────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class Settings:
    """Centralised application settings."""

    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = "openai/gpt-oss-120b"
    SAFEGUARD_MODEL: str = "openai/gpt-oss-safeguard-20b"
    LLM_TEMPERATURE: float = "0.1"

    # Paths
    DATA_DIR: Path = _PROJECT_ROOT / "data"
    CUSTOMERS_FILE: Path = DATA_DIR / "customers.json"
    ORDERS_FILE: Path = DATA_DIR / "orders.json"
    POLICY_FILE: Path = DATA_DIR / "refund_policy.txt"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Frontend
    FRONTEND_DIR: Path = _PROJECT_ROOT / "frontend"


settings = Settings()
