# Owner: Issue 4 - Confidence Intervals & Sample Size
"""Business logic for Confidence Intervals & Sample Size. Routers call these functions; keep logic here."""
from app.core.schemas import SolutionResponse
from app.core.steps import placeholder_response

ISSUE = 4
MODULE = "Confidence Intervals & Sample Size"


def mean(payload: dict) -> SolutionResponse:
    """TODO (Issue 4): Confidence interval for the mean (3 input modes, auto-select case)."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "mean"})


def sample_size(payload: dict) -> SolutionResponse:
    """TODO (Issue 4): Required sample size for a given margin of error."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "sample_size"})
