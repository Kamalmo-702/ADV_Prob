# Owner: Issue 5 - CLT Simulator
from typing import Any

from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import clt_service as service

router = APIRouter(prefix="/clt", tags=["CLT Simulator"])


@router.post("/simulate", response_model=SolutionResponse)
def simulate(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Simulate sample means from a chosen population."""
    return service.simulate(payload or {})
