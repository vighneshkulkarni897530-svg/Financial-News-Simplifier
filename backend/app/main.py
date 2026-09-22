"""FastAPI application entrypoint for FinNews AI."""

from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.news import router as news_router
from app.api.simplify import router as simplify_router
from app.core.config import settings
from app.core.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown event lifecycle."""
    logger.info("============================================================")
    logger.info("Starting FinNews AI API Backend...")
    safe_config = settings.log_safe_status()
    for key, val in safe_config.items():
        logger.info(f"   * {key}: {val}")
    logger.info("============================================================")
    yield
    logger.info("🛑 Shutting down FinNews AI API...")


app = FastAPI(
    title="FinNews AI API",
    description="AI-powered financial news simplification API using Groq LLaMA 3.3 70B and NewsAPI.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
origins = settings.cors_origins
logger.info(f"Configuring CORS with origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTPExceptions and ensure uniform error JSON."""
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.detail.get("code", "HTTP_ERROR"),
                "message": exc.detail.get("message", "An error occurred."),
                "details": exc.detail.get("details"),
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle incoming request validation errors cleanly."""
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append({"field": loc, "message": err.get("msg")})

    logger.warning(f"Validation error on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "code": "INVALID_REQUEST",
            "message": "Invalid request parameters or payload.",
            "details": errors,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for uncaught exceptions to prevent leaking internal traces."""
    logger.exception(f"Unhandled internal server error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred. Please try again later.",
            "details": None,
        },
    )


# Root Endpoint
@app.get(
    "/",
    summary="Root Endpoint",
    description="Returns service identity and running status.",
    response_model=Dict[str, str],
    tags=["Root"],
)
async def root():
    """Root metadata endpoint."""
    return {
        "name": "FinNews AI",
        "description": "AI-powered financial news simplification platform",
        "version": "1.0.0",
        "status": "running",
    }


# Include Routers
app.include_router(health_router)
app.include_router(news_router)
app.include_router(simplify_router)
