# Owner: Issue 5 - Check the Slides
from fastapi import APIRouter

from app.core.schemas import SolutionResponse
from app.services import verify_service as service

router = APIRouter(prefix="/verify", tags=["Check the Slides"])


@router.get("/slides", response_model=SolutionResponse)
def slides() -> SolutionResponse:
    """Slide answers vs exact scipy answers."""
    return service.slides({})