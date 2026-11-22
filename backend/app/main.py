"""Stats Lab API entry point.

Each module lives in its own router (app/routers) and service (app/services),
so team members can work in parallel without touching the same files.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import ci, clt, distributions, normal, sampling, verify

app = FastAPI(
    title="Stats Lab API",
    description="Advanced Statistics & Probability: calculators with solution steps and simulations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


for module in (normal, distributions, sampling, ci, clt, verify):
    app.include_router(module.router)
