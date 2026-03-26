from fastapi import FastAPI
from app.api.v1.endpoints import services, auth

app = FastAPI(title="SPA Salon API", version="1.0.0")

app.include_router(services.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "SPA Salon API", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy"}