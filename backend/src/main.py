from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.db.database import init_db
from src.api.routes import auth, hcps, interactions, materials, samples, follow_ups


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="HCP CRM API",
    description="AI-Powered CRM for Healthcare Professional Interactions",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(hcps.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(samples.router, prefix="/api")
app.include_router(follow_ups.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "HCP CRM API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
