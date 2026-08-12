"""
Aggregated API v1 router — includes all endpoint groups.

Keeping this in a separate file makes it easy to add API v2 later
without touching main.py.
"""

from fastapi import APIRouter

from app.api.v1 import auth, complaints, users, dashboard

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
