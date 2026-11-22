# Owner: Issue 3 - Sampling Distributions
"""Business logic for Sampling Distributions. Routers call these functions; keep logic here."""
from app.core.schemas import SolutionResponse
from app.core.steps import placeholder_response

ISSUE = 3
MODULE = "Sampling Distributions"


def mean(payload: dict) -> SolutionResponse:
    """TODO (Issue 3): Sampling distribution of the mean (auto-select Z or T)."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "mean"})


def variance(payload: dict) -> SolutionResponse:
    """TODO (Issue 3): Sampling distribution of the variance (chi-square)."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "variance"})


def proportion(payload: dict) -> SolutionResponse:
    """TODO (Issue 3): Sampling distribution of the proportion."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "proportion"})
