# Owner: Issue 2 - t / Chi-square / F Explorer
from typing import Any

from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import distributions_service as service

router = APIRouter(prefix="/dist", tags=["t / Chi-square / F Explorer"])


@router.post("/t", response_model=SolutionResponse)
def t_distribution(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Student t: pdf curve, P(T>t), critical values."""
    return service.t_distribution(payload or {})


@router.post("/chi2", response_model=SolutionResponse)
def chi2_distribution(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Chi-square: pdf curve, probabilities, critical values."""
    return service.chi2_distribution(payload or {})


@router.post("/f", response_model=SolutionResponse)
def f_distribution(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """F distribution: pdf curve, probabilities, critical values."""
    return service.f_distribution(payload or {})
