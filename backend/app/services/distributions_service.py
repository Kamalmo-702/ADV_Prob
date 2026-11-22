# Owner: Issue 2 - t / Chi-square / F Explorer
"""Business logic for t / Chi-square / F Explorer. Routers call these functions; keep logic here."""
from app.core.schemas import SolutionResponse
from app.core.steps import placeholder_response

ISSUE = 2
MODULE = "t / Chi-square / F Explorer"


def t_distribution(payload: dict) -> SolutionResponse:
    """TODO (Issue 2): Student t: pdf curve, P(T>t), critical values."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "t_distribution"})


def chi2_distribution(payload: dict) -> SolutionResponse:
    """TODO (Issue 2): Chi-square: pdf curve, probabilities, critical values."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "chi2_distribution"})


def f_distribution(payload: dict) -> SolutionResponse:
    """TODO (Issue 2): F distribution: pdf curve, probabilities, critical values."""
    return placeholder_response(ISSUE, MODULE, {"endpoint": "f_distribution"})
