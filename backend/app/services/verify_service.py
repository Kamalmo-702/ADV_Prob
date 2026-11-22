# Owner: Issue 5 - Check the Slides
"""Business logic for Check the Slides. Routers call these functions; keep logic here."""
from app.core.schemas import SolutionResponse
from app.core.steps import placeholder_response

ISSUE = 5
MODULE = "Check the Slides"


def slides(payload: dict) -> SolutionResponse:
    """TODO (Issue 5): Slide answers vs exact scipy answers."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "slides"})
