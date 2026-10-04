from fastapi import APIRouter
from .agents import router as agents_router
from .payments import router as payments_router
from .stats import router as stats_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(agents_router, prefix="/agents", tags=["Agents"])
api_v1_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_v1_router.include_router(stats_router, prefix="/stats", tags=["Statistics & Overview"])
