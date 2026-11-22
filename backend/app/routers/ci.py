# Owner: Issue 4 - Confidence Intervals & Sample Size
from typing import Any

from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import ci_service as service

router = APIRouter(prefix="/ci", tags=["Confidence Intervals & Sample Size"])


@router.post("/mean", response_model=SolutionResponse)
def mean(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Confidence interval for the mean (3 input modes, auto-select case)."""
    return service.mean(payload or {})


@router.post("/sample-size", response_model=SolutionResponse)
def sample_size(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Required sample size for a given margin of error."""
    return service.sample_size(payload or {})
