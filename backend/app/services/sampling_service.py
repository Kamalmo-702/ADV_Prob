# Owner: Issue 3 - Sampling Distributions
"""Business logic for Sampling Distributions (Lectures 2 and 3). Routers call these functions."""
from __future__ import annotations

import math
from typing import Any, Callable, Optional

import numpy as np
from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator
from scipy import stats

from app.core.schemas import SolutionResponse
from app.core.steps import StepsBuilder

ISSUE = 3
MODULE = "Sampling Distributions"


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class MeanRequest(BaseModel):
    mu: float = Field(..., description="Population mean")
    n: int = Field(..., ge=1, le=100000, description="Sample size")
    a: float = Field(..., description="Value a in P(X̄<a), P(X̄>a)")
    b: Optional[float] = Field(default=None, description="Optional upper value for P(a<X̄<b)")
    sigma: Optional[float] = Field(default=None, gt=0, description="Population SD (if known)")
    sigma2: Optional[float] = Field(default=None, gt=0, description="Population variance (if known)")
    s: Optional[float] = Field(default=None, gt=0, description="Sample SD")
    s2: Optional[float] = Field(default=None, gt=0, description="Sample variance")
    population_normal: bool = Field(default=True, description="Is the population (approximately) normal?")

    @model_validator(mode="after")
    def _derive_sd(self) -> "MeanRequest":
        if self.sigma is None and self.sigma2 is not None:
            self.sigma = math.sqrt(self.sigma2)
        if self.s is None and self.s2 is not None:
            self.s = math.sqrt(self.s2)
        return self


class VarianceRequest(BaseModel):
    n: int = Field(..., ge=2, le=100000, description="Sample size (n >= 2)")
    sigma2: float = Field(..., gt=0, description="Population variance")
    a: float = Field(..., ge=0, description="Value a in P(s²<a), P(s²>a)")
    b: Optional[float] = Field(default=None, description="Optional upper value for P(a<s²<b)")


class ProportionRequest(BaseModel):
    n: int = Field(..., ge=1, le=100000, description="Sample size")
    a: float = Field(..., description="Value a in P(p̂<a), P(p̂>a)")
    b: Optional[float] = Field(default=None, description="Optional upper value for P(a<p̂<b)")
    p: Optional[float] = Field(default=None, gt=0, lt=1, description="Population proportion")
    population_size: Optional[int] = Field(default=None, ge=1, description="N (alternative to p)")
    population_successes: Optional[int] = Field(default=None, ge=0, description="X (alternative to p)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _require(condition: bool, msg: str) -> None:
    if not condition:
        raise HTTPException(status_code=422, detail=msg)


def _num(x: float, d: int = 4) -> str:
    s = f"{x:.{d}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _region(fx: Callable[[np.ndarray], np.ndarray], lo: float, hi: float,
            x_min: float, x_max: float) -> Optional[dict]:
    """Points of the density between lo and hi (clipped to the plotted range) for shading."""
    lo, hi = max(lo, x_min), min(hi, x_max)
    if hi <= lo:
        return None
    xs = np.linspace(lo, hi, 80)
    return {"x": xs.tolist(), "y": fx(xs).tolist()}


def _build_plot(fx: Callable[[np.ndarray], np.ndarray], x_min: float, x_max: float, a: float,
                b: Optional[float], mean: float, x_label: str, statistic: str,
                se_label: str, se_fn: Callable[[int], float], n: int) -> dict:
    xs = np.linspace(x_min, x_max, 240)
    top = max(60, 2 * n)
    ns = list(range(2, top + 1))
    return {
        "x_label": x_label,
        "statistic": statistic,
        "curve": {"x": xs.tolist(), "y": fx(xs).tolist()},
        "regions": {
            "less": _region(fx, x_min, a, x_min, x_max),
            "greater": _region(fx, a, x_max, x_min, x_max),
            "between": _region(fx, a, b, x_min, x_max) if b is not None else None,
        },
        "a": a, "b": b, "mean": mean,
        "se_vs_n": {
            "label": se_label,
            "n": ns,
            "se": [se_fn(k) for k in ns],
            "current": {"n": n, "se": se_fn(n)},
        },
    }


def _check_ab(a: float, b: Optional[float]) -> None:
    _require(b is None or b > a, "b must be greater than a.")


def _coerce(model: type[BaseModel], payload: Any) -> Any:
    if isinstance(payload, model):
        return payload
    try:
        return model.model_validate(payload)
    except Exception as exc:  # pydantic ValidationError -> 422 like the other modules
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /sampling/mean
# ---------------------------------------------------------------------------
def mean(payload: MeanRequest | dict[str, Any]) -> SolutionResponse:
    """Sampling distribution of the mean; auto-selects Z or T ("Very Important Remark", Lecture 2)."""
    req = _coerce(MeanRequest, payload)
    _check_ab(req.a, req.b)
    _require(req.sigma is not None or req.s is not None, "Provide sigma (population SD) or s (sample SD).")

    n, notes = req.n, []
    if req.sigma is not None:
        spread, sym, stat, case = req.sigma, r"\sigma", "Z", "Z_sigma_known"
        reason = "σ is known and n ≥ 30 → Z with σ" if n >= 30 else (
            "σ is known and the population is normal → Z with σ" if req.population_normal
            else "σ is known → Z with σ")
        if not req.population_normal and n < 30:
            notes.append("Population is not normal and n < 30: the Z result may not be reliable.")
    elif n >= 30:
        spread, sym, stat, case = req.s, "s", "Z", "Z_s_large_n"
        reason = "σ is unknown and n ≥ 30 → Z with s"
    else:
        _require(n >= 2, "n must be at least 2 when σ is unknown (df = n − 1).")
        spread, sym, stat, case = req.s, "s", "T", "T_df"
        reason = f"σ is unknown and n < 30 → T with df = n − 1 = {n - 1}"
        if not req.population_normal:
            notes.append("T requires an approximately normal population.")

    df = n - 1
    dist = stats.t(df) if stat == "T" else stats.norm()
    se = spread / math.sqrt(n)
    za = (req.a - req.mu) / se
    zb = (req.b - req.mu) / se if req.b is not None else None
    p_less, p_greater = float(dist.cdf(za)), float(dist.sf(za))
    p_between = float(dist.cdf(zb) - dist.cdf(za)) if zb is not None else None

    S = r"\bar{X}"
    dist_tex = rf"T_{{({df})}}" if stat == "T" else r"N(0,1)"
    steps = StepsBuilder()
    steps.add(rf"\mu = {_num(req.mu)},\quad {sym} = {_num(spread)},\quad n = {n}")
    steps.add(rf"\text{{Case chosen: {reason}}}")
    steps.add(rf"\sigma_{{\bar{{x}}}} = \frac{{{sym}}}{{\sqrt{{n}}}} = \frac{{{_num(spread)}}}{{\sqrt{{{n}}}}} = {_num(se)}")
    steps.add(rf"{stat} = \frac{{{S} - \mu}}{{{sym}/\sqrt{{n}}}} \sim {dist_tex}")
    steps.add(rf"P({S} < {_num(req.a)}) = P\left({stat} < \frac{{{_num(req.a)} - {_num(req.mu)}}}{{{_num(se)}}}\right) = P({stat} < {_num(za, 2)}) = {_num(p_less)}")
    steps.add(rf"P({S} > {_num(req.a)}) = P({stat} > {_num(za, 2)}) = 1 - {_num(p_less)} = {_num(p_greater)}")
    if req.b is not None:
        steps.add(rf"P({_num(req.a)} < {S} < {_num(req.b)}) = P({_num(za, 2)} < {stat} < {_num(zb, 2)}) = {_num(p_between)}")

    x_min, x_max = req.mu - 4.5 * se, req.mu + 4.5 * se
    fx = lambda x: dist.pdf((x - req.mu) / se) / se  # noqa: E731
    plot = _build_plot(fx, x_min, x_max, req.a, req.b, req.mu, "x̄", stat,
                       f"{'σ' if req.sigma is not None else 's'}/√n",
                       lambda k: spread / math.sqrt(k), n)

    return SolutionResponse(
        result={
            "case": case, "statistic": stat, "reason": reason,
            "df": df if stat == "T" else None,
            "mean_of_xbar": req.mu, "standard_error": se,
            "z_a": za, "z_b": zb,
            "p_less": p_less, "p_greater": p_greater, "p_between": p_between,
        },
        steps=steps.build(), plot=plot, notes=notes,
    )


# ---------------------------------------------------------------------------
# POST /sampling/variance
# ---------------------------------------------------------------------------
def variance(payload: VarianceRequest | dict[str, Any]) -> SolutionResponse:
    """Sampling distribution of s²: chi² = (n-1)s²/σ² with df = n-1 (normal population)."""
    req = _coerce(VarianceRequest, payload)
    _check_ab(req.a, req.b)
    n, df = req.n, req.n - 1
    dist = stats.chi2(df)
    k = df / req.sigma2
    ca = req.a * k
    cb = req.b * k if req.b is not None else None
    p_less, p_greater = float(dist.cdf(ca)), float(dist.sf(ca))
    p_between = float(dist.cdf(cb) - dist.cdf(ca)) if cb is not None else None
    e_s2 = req.sigma2
    v_s2 = 2 * req.sigma2 ** 2 / df

    steps = StepsBuilder()
    steps.add(rf"n = {n},\quad \sigma^2 = {_num(req.sigma2)}")
    steps.add(rf"\chi^2 = \frac{{(n-1)s^2}}{{\sigma^2}} \sim \chi^2_{{({df})}}")
    steps.add(rf"P(s^2 > {_num(req.a)}) = P\left(\chi^2 > \frac{{{_num(req.a)}({n}-1)}}{{{_num(req.sigma2)}}}\right) = P(\chi^2 > {_num(ca)}) = {_num(p_greater)}")
    steps.add(rf"P(s^2 < {_num(req.a)}) = 1 - {_num(p_greater)} = {_num(p_less)}")
    if req.b is not None:
        steps.add(rf"P({_num(req.a)} < s^2 < {_num(req.b)}) = P({_num(ca)} < \chi^2 < {_num(cb)}) = P(\chi^2 > {_num(ca)}) - P(\chi^2 > {_num(cb)}) = {_num(p_between)}")
    steps.add(rf"E(s^2) = \sigma^2 = {_num(e_s2)}")
    steps.add(rf"V(s^2) = \frac{{2\sigma^4}}{{n-1}} = \frac{{2({_num(req.sigma2)})^2}}{{{df}}} = {_num(v_s2)}")

    x_min, x_max = 0.0, float(dist.ppf(0.9995)) / k
    fx = lambda x: dist.pdf(x * k) * k  # noqa: E731
    plot = _build_plot(fx, x_min, x_max, req.a, req.b, e_s2, "s²", "χ²",
                       "SD(s²) = σ²·√(2/(n−1))",
                       lambda m: req.sigma2 * math.sqrt(2 / (m - 1)), n)

    return SolutionResponse(
        result={
            "case": "chi_square", "statistic": "χ²", "df": df,
            "reason": f"Variance statistic → χ² with df = n − 1 = {df}",
            "chi2_a": ca, "chi2_b": cb,
            "p_less": p_less, "p_greater": p_greater, "p_between": p_between,
            "e_s2": e_s2, "v_s2": v_s2,
        },
        steps=steps.build(), plot=plot,
        notes=["Assumes the population is normal (required for the χ² result)."],
    )


# ---------------------------------------------------------------------------
# POST /sampling/proportion
# ---------------------------------------------------------------------------
def proportion(payload: ProportionRequest | dict[str, Any]) -> SolutionResponse:
    """Sampling distribution of p̂ using the normal approximation (warns if np<5 or n(1-p)<5)."""
    req = _coerce(ProportionRequest, payload)
    _check_ab(req.a, req.b)
    p = req.p
    if p is None:
        _require(req.population_size is not None and req.population_successes is not None,
                 "Provide p, or population_size (N) and population_successes (X).")
        _require(req.population_successes <= req.population_size, "X cannot be greater than N.")
        p = req.population_successes / req.population_size
        _require(0 < p < 1, "P = X/N must be strictly between 0 and 1.")

    n = req.n
    var = p * (1 - p) / n
    se = math.sqrt(var)
    za = (req.a - p) / se
    zb = (req.b - p) / se if req.b is not None else None
    dist = stats.norm()
    p_less, p_greater = float(dist.cdf(za)), float(dist.sf(za))
    p_between = float(dist.cdf(zb) - dist.cdf(za)) if zb is not None else None

    notes = []
    if n * p < 5 or n * (1 - p) < 5:
        notes.append(
            f"Warning: normal approximation may be poor: np = {n * p:.2f}, n(1−p) = {n * (1 - p):.2f} "
            "(both should be ≥ 5).")

    steps = StepsBuilder()
    if req.p is None:
        steps.add(rf"N = {req.population_size},\; X = {req.population_successes} \Rightarrow P = \frac{{{req.population_successes}}}{{{req.population_size}}} = {_num(p)},\quad n = {n}")
    else:
        steps.add(rf"P = {_num(p)},\quad n = {n}")
    steps.add(rf"E(\hat{{P}}) = P = {_num(p)},\quad \sigma_{{\hat{{P}}}} = \sqrt{{\frac{{P(1-P)}}{{n}}}} = \sqrt{{\frac{{{_num(p)}(1-{_num(p)})}}{{{n}}}}} = {_num(se)}")
    steps.add(rf"np = {_num(n * p, 2)},\quad n(1-p) = {_num(n * (1 - p), 2)}\quad (\text{{both }} \geq 5 \text{{ needed}})")
    steps.add(r"Z = \frac{\hat{P} - P}{\sqrt{P(1-P)/n}} \sim N(0,1)")
    steps.add(rf"P(\hat{{P}} < {_num(req.a)}) = P(Z < {_num(za, 2)}) = {_num(p_less)}")
    steps.add(rf"P(\hat{{P}} > {_num(req.a)}) = P(Z > {_num(za, 2)}) = {_num(p_greater)}")
    if req.b is not None:
        steps.add(rf"P({_num(req.a)} < \hat{{P}} < {_num(req.b)}) = P({_num(za, 2)} < Z < {_num(zb, 2)}) = {_num(p_between)}")

    x_min, x_max = max(0.0, p - 4.5 * se), min(1.0, p + 4.5 * se)
    fx = lambda x: dist.pdf((x - p) / se) / se  # noqa: E731
    plot = _build_plot(fx, x_min, x_max, req.a, req.b, p, "p̂", "Z",
                       "√(P(1−P)/n)", lambda k: math.sqrt(p * (1 - p) / k), n)

    return SolutionResponse(
        result={
            "case": "Z_proportion", "statistic": "Z",
            "reason": "Proportion → Z (normal approximation)",
            "p": p, "mean": p, "variance": var, "standard_error": se,
            "z_a": za, "z_b": zb, "np": n * p, "n_one_minus_p": n * (1 - p),
            "p_less": p_less, "p_greater": p_greater, "p_between": p_between,
        },
        steps=steps.build(), plot=plot, notes=notes,
    )
