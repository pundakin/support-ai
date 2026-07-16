from fastapi import FastAPI
from sqlalchemy import select
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import tickets
from app.db.session import get_engine


# Lifespan context manager for initialization/cleanup on startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialization on startup
    settings = get_settings()
    engine = get_engine()

    # Database connection check (optional, for early problem detection)
    async with engine.connect() as conn:
        await conn.execute(select(1))

    yield

    # Cleanup on shutdown
    await engine.dispose()


# Create application with lifespan
app = FastAPI(
    title="SupportAI API",
    description="API for automatic ticket processing system",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware to allow requests from the frontend
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routes
app.include_router(tickets.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple endpoint for checking service availability."""
    return {"status": "ok"}


# Root endpoint with documentation links
@app.get("/")
async def root():
    """Root endpoint with links to documentation."""
    return {
        "message": "SupportAI API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }