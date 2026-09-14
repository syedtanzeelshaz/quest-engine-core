from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db

app = FastAPI(title="Quest Engine Core Service")

@app.get("/")
def read_root():
    return {"message": "Welcome to Quest Engine Core API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "quest-engine-core"}

@app.get("/health/db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Run a quick raw query to test database responsiveness
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "healthy",
            "db_response": result
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}