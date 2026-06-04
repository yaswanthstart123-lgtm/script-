"""
SecureHub — FastAPI Application Entry Point
Sets up the app, middleware, routes, and lifecycle events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.mongodb import connect_mongo, close_mongo
from app.redis_client import connect_redis, close_redis
from app.middleware.activity_logger import ActivityLoggerMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.routes import auth, students, quiz

settings = get_settings()


# ── Lifecycle Events ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle manager."""
    # ── Startup ──
    # Create all database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Connect to Redis
    await connect_redis()

    # Connect to MongoDB
    await connect_mongo()

    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started successfully!")

    yield

    # ── Shutdown ──
    await close_redis()
    await close_mongo()
    await engine.dispose()
    print(f"👋 {settings.APP_NAME} shut down gracefully.")


# ── FastAPI App ──────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SecureHub — Secure Quiz Management Platform with JWT Auth, PostgreSQL, Redis & MongoDB",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Custom Middleware ────────────────────────────
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(ActivityLoggerMiddleware)

# ── API Routes ───────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])


# ── Health Check ─────────────────────────────────
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
