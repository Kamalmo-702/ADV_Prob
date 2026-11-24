# Owner: Issue 3 - Sampling Distributions
from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import sampling_service as service
from app.services.sampling_service import MeanRequest, ProportionRequest, VarianceRequest

router = APIRouter(prefix="/sampling", tags=["Sampling Distributions"])


@router.post("/mean", response_model=SolutionResponse)
def mean(payload: MeanRequest) -> SolutionResponse:
    """Sampling distribution of the mean (auto-select Z or T)."""
    return service.mean(payload)


@router.post("/variance", response_model=SolutionResponse)
def variance(payload: VarianceRequest) -> SolutionResponse:
    """Sampling distribution of the variance (chi-square)."""
    return service.variance(payload)


@router.post("/proportion", response_model=SolutionResponse)
def proportion(payload: ProportionRequest) -> SolutionResponse:
    """Sampling distribution of the proportion."""
    return service.proportion(payload)
