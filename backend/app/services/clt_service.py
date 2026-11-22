# Owner: Issue 5 - CLT Simulator
"""Business logic for CLT Simulator. Routers call these functions; keep logic here."""
from app.core.schemas import SolutionResponse
from app.core.steps import placeholder_response

ISSUE = 5
MODULE = "CLT Simulator"


def simulate(payload: dict) -> SolutionResponse:
    """TODO (Issue 5): Simulate sample means from a chosen population."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "simulate"})
