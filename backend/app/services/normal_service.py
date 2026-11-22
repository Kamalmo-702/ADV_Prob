# Owner: Issue 2 - Normal Distribution
"""Business logic for Normal Distribution. Routers call these functions; keep logic here."""
from app.core.schemas import SolutionResponse
from app.core.steps import placeholder_response

ISSUE = 2
MODULE = "Normal Distribution"


def probability(payload: dict) -> SolutionResponse:
    """TODO (Issue 2): P(X<a), P(X>a), P(a<X<b) with standardization steps."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "probability"})


def inverse(payload: dict) -> SolutionResponse:
    """TODO (Issue 2): Find k such that P(X<k)=p or P(X>k)=p."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "inverse"})
