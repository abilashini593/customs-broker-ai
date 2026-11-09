from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_data import seed_database
from app.api.shipments import router as shipments_router
from app.api.cross_check import router as cross_check_router
from app.api.documents import router as documents_router
from app.api.export import router as export_router
from app.api.audit_logs import router as audit_logs_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    # Seed database with realistic sample shipments
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Customs Broker AI Document Extraction & Deterministic Cross-Check Engine",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(shipments_router, prefix=settings.API_V1_STR)
app.include_router(cross_check_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(export_router, prefix=settings.API_V1_STR)
app.include_router(audit_logs_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "customs-broker-ai"}
