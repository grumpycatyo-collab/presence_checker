"""API routes."""

from fastapi import APIRouter

from .health import router as health_router
from .routes.professors import router as professors_router
from .routes.courses import router as courses_router

router = APIRouter()

router.include_router(health_router)
router.include_router(professors_router)
router.include_router(courses_router)