from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base
import app.database.models  # Crucial: Import models before create_all
from app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, description="Emotion, Humor and Culture Preserving Regional Movie Dubbing System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "app": settings.APP_NAME, "mode": "advanced" if settings.ENABLE_ADVANCED_MODELS else "mvp"}

from app.api.routes_jobs import router as jobs_router
from app.api.routes_review import router as review_router
from app.api.routes_artifacts import router as artifacts_router

app.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
app.include_router(review_router, prefix="/review", tags=["Review"])
app.include_router(artifacts_router, prefix="/artifacts", tags=["Artifacts"])
