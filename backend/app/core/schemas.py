"""Shared response schema. EVERY endpoint in EVERY module returns SolutionResponse."""
from pydantic import BaseModel, Field


class SolutionResponse(BaseModel):
    result: dict | float | list | None = None  # the final answer(s)
    steps: list[str] = Field(default_factory=list)  # solution steps, each one a LaTeX string
    plot: dict | None = None  # plot data for the frontend (x, y arrays, shaded regions...)
    notes: list[str] = Field(default_factory=list)  # warnings, e.g. "np < 5: approximation may be poor"
