"""
CueNote Core - Routers
"""
from .vault import router as vault_router
from .todos import router as todos_router
from .ai import router as ai_router

__all__ = ["vault_router", "todos_router", "ai_router"]
