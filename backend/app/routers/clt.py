# Owner: Issue 5 - CLT Simulator & CI Coverage Demo
from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import clt_service as service
from app.services.clt_service import CICoverageRequest, CLTSimulateRequest

router = APIRouter(prefix="/clt", tags=["CLT Simulator"])


@router.post("/simulate", response_model=SolutionResponse)
def simulate(payload: CLTSimulateRequest) -> SolutionResponse:
    """Simulate sample means from a chosen population."""
    return service.simulate(payload)


@router.post("/coverage", response_model=SolutionResponse)
def coverage(payload: CICoverageRequest) -> SolutionResponse:
    """Simulate Z confidence intervals and measure empirical coverage of mu."""
    return service.coverage(payload)