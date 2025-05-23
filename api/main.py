"""API routes."""

from fastapi import APIRouter

from .health import router as health_router
from .routes.professors import router as professors_router
from .routes.courses import router as courses_router
from .routes.attendances import router as attendances_router
from .routes.groups import router as groups_router
from .routes.sessions import router as sessions_router
from .routes.students import router as students_router

router = APIRouter()

router.include_router(health_router)
router.include_router(professors_router)
router.include_router(courses_router)
router.include_router(attendances_router)
router.include_router(groups_router)
router.include_router(sessions_router)
router.include_router(students_router)