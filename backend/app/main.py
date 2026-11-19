from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.database.session import engine, Base
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore
from backend.app.api.v1.api_router import api_v1_router

# Setup logging early
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing DocuMind backend...")
    logger.info("Creating database tables if not already present...")
    Base.metadata.create_all(bind=engine)

    logger.info("Pre-warming Embedding Service and FAISS Vector Store...")
    try:
        EmbeddingService()
        VectorStore()
    except Exception as e:
        logger.warning(f"Embedding or VectorStore pre-warm warning (will initialize on demand): {e}")

    logger.info("DocuMind backend initialization complete.")
    yield
    # Shutdown actions
    logger.info("Shutting down DocuMind backend...")

app = FastAPI(
    title="DocuMind API",
    description="AI-Powered Document Intelligence & Research Agent Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_v1_router)

@app.get("/health", tags=["System"])
def health_check():
    """Application health and status check."""
    return {
        "status": "healthy",
        "service": "DocuMind Backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

