from fastapi import APIRouter

from app.api.v1.endpoints import (
    exercises,
    glossary,
    health,
    history,
    parse,
    solve,
    vision,
    worksheets,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(solve.router)
api_router.include_router(parse.router)
api_router.include_router(vision.router)
api_router.include_router(history.router)
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(worksheets.router)
api_router.include_router(glossary.router)
