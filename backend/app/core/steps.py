"""Helpers for building the `steps` list (LaTeX strings) of a SolutionResponse."""
from app.core.schemas import SolutionResponse


class StepsBuilder:
    r"""Collect solution steps one by one.

    Example:
        steps = StepsBuilder()
        steps.add(r"1-\alpha = 0.95 \Rightarrow \alpha = 0.05")
        steps.add(r"z_{\alpha/2} = 1.96")
        response = SolutionResponse(result=..., steps=steps.build())
    """

    def __init__(self) -> None:
        self._steps: list[str] = []

    def add(self, latex: str) -> "StepsBuilder":
        self._steps.append(latex)
        return self

    def build(self) -> list[str]:
        return list(self._steps)


def placeholder_response(issue: int, module: str, extra: dict | None = None) -> SolutionResponse:
    """Dummy response used until a module is implemented."""
    return SolutionResponse(
        result={"status": "placeholder", "module": module, **(extra or {})},
        steps=[rf"\text{{TODO: implemented by Issue {issue} ({module})}}"],
        plot=None,
        notes=["Placeholder response: this endpoint is not implemented yet."],
    )
