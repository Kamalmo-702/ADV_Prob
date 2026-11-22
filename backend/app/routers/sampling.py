# Owner: Issue 3 - Sampling Distributions
from typing import Any

from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import sampling_service as service

router = APIRouter(prefix="/sampling", tags=["Sampling Distributions"])


@router.post("/mean", response_model=SolutionResponse)
def mean(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Sampling distribution of the mean (auto-select Z or T)."""
    return service.mean(payload or {})


@router.post("/variance", response_model=SolutionResponse)
def variance(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Sampling distribution of the variance (chi-square)."""
    return service.variance(payload or {})


@router.post("/proportion", response_model=SolutionResponse)
def proportion(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Sampling distribution of the proportion."""
    return service.proportion(payload or {})
