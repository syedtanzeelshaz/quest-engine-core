from fastapi import APIRouter
from app.util.logger import log

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "quest-engine-core"}
