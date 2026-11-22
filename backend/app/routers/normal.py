# Owner: Issue 2 - Normal Distribution
from typing import Any

from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import normal_service as service

router = APIRouter(prefix="/normal", tags=["Normal Distribution"])


@router.post("/probability", response_model=SolutionResponse)
def probability(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """P(X<a), P(X>a), P(a<X<b) with standardization steps."""
    return service.probability(payload or {})


@router.post("/inverse", response_model=SolutionResponse)
def inverse(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Find k such that P(X<k)=p or P(X>k)=p."""
    return service.inverse(payload or {})
