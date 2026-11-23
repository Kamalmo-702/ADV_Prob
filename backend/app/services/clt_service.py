# Owner: Issue 5 - CLT Simulator & CI Coverage Demo
"""Business logic for CLT Simulator and Confidence Interval Coverage Demo."""
import math
from typing import Any, Literal

import numpy as np
from pydantic import BaseModel, Field
from scipy import stats

from app.core.schemas import SolutionResponse
from app.core.stats_utils import z_critical
from app.core.steps import StepsBuilder

PopulationType = Literal["uniform", "exponential", "skewed", "bimodal"]


class CLTSimulateRequest(BaseModel):
    population: PopulationType = Field(
        ...,
        description="Population distribution: uniform, exponential, skewed, or bimodal",
    )
    n: int = Field(..., ge=1, le=500, description="Sample size (1 to 500)")
    samples: int = Field(
        ..., ge=100, le=20000, description="Number of simulated samples (100 to 20000)"
    )
    seed: int | None = Field(default=None, description="Optional random seed")


class CICoverageRequest(BaseModel):
    mu: float = Field(..., description="True population mean")
    sigma: float = Field(..., gt=0, description="Known population standard deviation (sigma > 0)")
    n: int = Field(..., ge=1, le=10000, description="Sample size per interval (n >= 1)")
    confidence: float = Field(
        ..., gt=0, lt=1, description="Confidence level strictly between 0 and 1"
    )
    intervals: int = Field(
        default=100, ge=1, le=500, description="Number of confidence intervals to simulate"
    )
    seed: int | None = Field(default=None, description="Optional random seed")


def _draw_population(
    population: PopulationType,
    size: tuple[int, int],
    rng: np.random.Generator,
) -> tuple[np.ndarray, float, float, str]:
    """Draw samples from the selected population and return (data, pop_mean, pop_sd, latex_desc)."""
    if population == "uniform":
        data = rng.uniform(0.0, 1.0, size=size)
        pop_mean = float(stats.uniform.mean(loc=0.0, scale=1.0))
        pop_sd = float(stats.uniform.std(loc=0.0, scale=1.0))
        desc = r"X \sim \text{Uniform}(0, 1),\ \mu = 0.5,\ \sigma = \frac{1}{\sqrt{12}}"
    elif population == "exponential":
        data = rng.exponential(scale=1.0, size=size)
        pop_mean = float(stats.expon.mean(scale=1.0))
        pop_sd = float(stats.expon.std(scale=1.0))
        desc = r"X \sim \text{Exponential}(\lambda = 1),\ \mu = 1,\ \sigma = 1"
    elif population == "skewed":
        df = 3
        data = rng.chisquare(df=df, size=size)
        pop_mean = float(stats.chi2.mean(df=df))
        pop_sd = float(stats.chi2.std(df=df))
        desc = r"X \sim \chi^2(\nu = 3),\ \mu = 3,\ \sigma = \sqrt{6}"
    else:  # bimodal: 0.5 * N(-2, 0.7^2) + 0.5 * N(2, 0.7^2)
        sd_comp = 0.7
        centers = rng.choice(np.array([-2.0, 2.0]), size=size)
        data = centers + rng.normal(0.0, sd_comp, size=size)
        pop_mean = 0.0
        pop_sd = math.sqrt(sd_comp**2 + 2.0**2)
        desc = r"X \sim 0.5\,\mathcal{N}(-2, 0.7^2) + 0.5\,\mathcal{N}(2, 0.7^2),\ \mu = 0,\ \sigma = \sqrt{4.49}"

    return data, pop_mean, pop_sd, desc


def simulate(payload: CLTSimulateRequest | dict[str, Any]) -> SolutionResponse:
    """Simulate sample means from a chosen population and compare to the CLT normal limit."""
    req = payload if isinstance(payload, CLTSimulateRequest) else CLTSimulateRequest.model_validate(payload)
    rng = np.random.default_rng(req.seed)

    raw, pop_mean, pop_sd, pop_latex = _draw_population(
        req.population, (req.samples, req.n), rng
    )
    sample_means = raw.mean(axis=1)

    theoretical_se = pop_sd / math.sqrt(req.n)
    mean_of_means = float(np.mean(sample_means))
    sd_of_means = float(np.std(sample_means, ddof=1))

    # Pre-bin histograms on the backend to keep payloads compact and fast
    pop_counts, pop_edges = np.histogram(raw.ravel(), bins=35, density=True)
    pop_centers = 0.5 * (pop_edges[:-1] + pop_edges[1:])

    means_counts, means_edges = np.histogram(sample_means, bins=40, density=True)
    means_centers = 0.5 * (means_edges[:-1] + means_edges[1:])

    x_min = min(float(means_edges[0]), pop_mean - 4.0 * theoretical_se)
    x_max = max(float(means_edges[-1]), pop_mean + 4.0 * theoretical_se)
    curve_x = np.linspace(x_min, x_max, 200)
    curve_y = stats.norm.pdf(curve_x, loc=pop_mean, scale=theoretical_se)

    steps = StepsBuilder()
    steps.add(rf"\text{{Population: }} {pop_latex}")
    steps.add(rf"\mu = {pop_mean:.4f}, \quad \sigma = {pop_sd:.4f}, \quad n = {req.n}")
    steps.add(
        rf"\text{{Theoretical SE}} = \frac{{\sigma}}{{\sqrt{{n}}}} = \frac{{{pop_sd:.4f}}}{{\sqrt{{{req.n}}}}} = {theoretical_se:.4f}"
    )
    steps.add(
        rf"\text{{CLT Approximation: }} \bar{{X}} \stackrel{{\approx}}{{\sim}} \mathcal{{N}}\!\left({pop_mean:.4f},\ {theoretical_se:.4f}^2\right)"
    )
    steps.add(
        rf"\text{{Simulated ({req.samples} samples): }} \overline{{\bar{{x}}}} = {mean_of_means:.4f}, \quad s_{{\bar{{x}}}} = {sd_of_means:.4f}"
    )

    notes: list[str] = []
    if req.n < 30 and req.population in ("exponential", "skewed", "bimodal"):
        notes.append(
            f"n = {req.n} < 30 with a non-normal ({req.population}) population: the distribution of sample means may still look skewed or multimodal. Increase n >= 30 to observe normal convergence."
        )
    else:
        notes.append(
            f"With n = {req.n}, the empirical distribution of sample means closely matches N({pop_mean:.4f}, {theoretical_se:.4f}^2)."
        )

    return SolutionResponse(
        result={
            "population": req.population,
            "n": req.n,
            "samples": req.samples,
            "seed": req.seed,
            "pop_mean": pop_mean,
            "pop_sd": pop_sd,
            "theoretical_se": theoretical_se,
            "mean_of_means": mean_of_means,
            "sd_of_means": sd_of_means,
        },
        steps=steps.build(),
        plot={
            "population_hist": {
                "edges": pop_edges.tolist(),
                "centers": pop_centers.tolist(),
                "counts": pop_counts.tolist(),
                "widths": np.diff(pop_edges).tolist(),
            },
            "means_hist": {
                "edges": means_edges.tolist(),
                "centers": means_centers.tolist(),
                "counts": means_counts.tolist(),
                "widths": np.diff(means_edges).tolist(),
            },
            "normal_curve": {
                "x": curve_x.tolist(),
                "y": curve_y.tolist(),
            },
        },
        notes=notes,
    )


def coverage(payload: CICoverageRequest | dict[str, Any]) -> SolutionResponse:
    """Draw repeated samples from Normal(mu, sigma) and compute known-sigma Z confidence intervals."""
    req = payload if isinstance(payload, CICoverageRequest) else CICoverageRequest.model_validate(payload)
    alpha = 1.0 - req.confidence
    z = z_critical(alpha)
    se = req.sigma / math.sqrt(req.n)
    margin = z * se

    rng = np.random.default_rng(req.seed)
    samples_matrix = rng.normal(loc=req.mu, scale=req.sigma, size=(req.intervals, req.n))
    x_bars = samples_matrix.mean(axis=1)

    lowers = x_bars - margin
    uppers = x_bars + margin
    contains = (lowers <= req.mu) & (req.mu <= uppers)

    covered_count = int(np.sum(contains))
    coverage_rate = float(covered_count / req.intervals)

    interval_items = [
        {
            "index": idx + 1,
            "x_bar": float(x_bars[idx]),
            "lower": float(lowers[idx]),
            "upper": float(uppers[idx]),
            "contains_mu": bool(contains[idx]),
        }
        for idx in range(req.intervals)
    ]

    steps = StepsBuilder()
    steps.add(
        rf"1 - \alpha = {req.confidence:.4f} \Rightarrow \alpha = {alpha:.4f}, \quad \alpha/2 = {alpha / 2:.4f}"
    )
    steps.add(rf"z_{{\alpha/2}} = {z:.4f}")
    steps.add(
        rf"\text{{Margin of error: }} E = z_{{\alpha/2}} \cdot \frac{{\sigma}}{{\sqrt{{n}}}} = {z:.4f} \cdot \frac{{{req.sigma:.4f}}}{{\sqrt{{{req.n}}}}} = {margin:.4f}"
    )
    steps.add(rf"\text{{Each interval: }} \bar{{x}}_i \pm {margin:.4f}")
    steps.add(
        rf"\text{{Coverage: }} \frac{{{covered_count}}}{{{req.intervals}}} = {coverage_rate:.4f} \ ({coverage_rate * 100:.1f}\%)"
    )

    notes = [
        f"At {req.confidence * 100:.1f}% confidence, {covered_count} of {req.intervals} simulated intervals ({coverage_rate * 100:.1f}%) contain the true mean mu = {req.mu}."
    ]

    return SolutionResponse(
        result={
            "mu": req.mu,
            "sigma": req.sigma,
            "n": req.n,
            "confidence": req.confidence,
            "total_intervals": req.intervals,
            "covered_count": covered_count,
            "coverage_rate": coverage_rate,
            "z_critical": z,
            "margin": margin,
            "intervals": interval_items,
        },
        steps=steps.build(),
        plot={
            "mu": req.mu,
            "margin": margin,
            "intervals": interval_items,
        },
        notes=notes,
    )