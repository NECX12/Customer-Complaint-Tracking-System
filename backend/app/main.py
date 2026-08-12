"""
FastAPI application entry point.

Configures:
- CORS middleware (allows requests from the frontend URL)
- API v1 router
- Health check endpoint
- OpenAPI documentation at /docs and /redoc

Design decision: CORS is configured to allow only the frontend URL, not "*".
This is a basic security measure that prevents random websites from making
authenticated API calls on behalf of users.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Customer Complaint Tracking System — Mikano Technical Assessment.\n\n"
        "Supports three roles: **Customer**, **Agent**, and **Admin** with "
        "JWT-based authentication and role-based access control."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for monitoring and Docker health checks."""
    return {"status": "healthy", "service": settings.APP_NAME}
