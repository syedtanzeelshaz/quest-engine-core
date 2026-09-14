from fastapi import FastAPI

app = FastAPI(title="Quest Engine Core Service")

@app.get("/")
def read_root():
    return {"message": "Welcome to Quest Engine Core API"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "quest-engine-core"}