import uvicorn
from app.core.config import settings

__version__ = "1.0.0"

def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )