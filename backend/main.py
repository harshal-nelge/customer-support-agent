"""
FastAPI application entry point.

- Mounts API routers for chat, customers, and admin
- Serves the frontend as static files
- Configures CORS for local development
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.routers import admin, chat, customers

app = FastAPI(
    title="ShopSmart AI Customer Support Agent",
    description="AI-powered refund processing agent with LangGraph",
    version="1.0.0",
)

# ── CORS (allow frontend during development) ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ──────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(customers.router)
app.include_router(admin.router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "ShopSmart AI Support Agent"}


# ── Serve frontend static files ─────────────────────────────────────────────
app.mount("/", StaticFiles(directory=str(settings.FRONTEND_DIR), html=True), name="frontend")
