# Owner: Issue 4 - Confidence Intervals & Sample Size
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.schemas import SolutionResponse
from app.services import ci_service as service

router = APIRouter(prefix="/ci", tags=["Confidence Intervals & Sample Size"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class MeanRequest(BaseModel):
    mode: str = Field("summary", pattern="^(summary|raw|sums)$")
    confidence: float = Field(..., gt=0, lt=1)
    population_normal: bool = False

    # summary mode
    x_bar: float | None = None
    n: int | None = Field(None, ge=1)
    sigma: float | None = Field(None, gt=0)
    s: float | None = Field(None, gt=0)

    # raw mode
    data: list[float] | None = None

    # sums mode
    sum_x: float | None = None
    sum_x2: float | None = None


class SampleSizeRequest(BaseModel):
    confidence: float = Field(..., gt=0, lt=1)
    sigma: float | None = Field(None, gt=0)
    s: float | None = Field(None, gt=0)
    margin: float = Field(..., gt=0)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/mean", response_model=SolutionResponse)
def mean(payload: MeanRequest) -> SolutionResponse:
    """Confidence interval for the mean (3 input modes, auto-select case)."""
    return service.mean(payload.model_dump())


@router.post("/sample-size", response_model=SolutionResponse)
def sample_size(payload: SampleSizeRequest) -> SolutionResponse:
    """Required sample size for a given margin of error."""
    return service.sample_size(payload.model_dump())
