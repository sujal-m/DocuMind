from fastapi import APIRouter
from backend.app.api.v1.documents import router as documents_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(documents_router)

