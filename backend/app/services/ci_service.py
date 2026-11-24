# Owner: Issue 4 - Confidence Intervals & Sample Size
"""Business logic for Confidence Intervals & Sample Size. Routers call these functions; keep logic here."""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
from fastapi import HTTPException
from scipy import stats

from app.core.schemas import SolutionResponse
from app.core.stats_utils import z_critical, t_critical
from app.core.steps import StepsBuilder

ISSUE = 4
MODULE = "Confidence Intervals & Sample Size"


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def _require(condition: bool, msg: str) -> None:
    if not condition:
        raise HTTPException(status_code=422, detail=msg)


def _validate_confidence(confidence) -> float:
    _require(confidence is not None, "confidence is required and must be in (0, 1).")
    c = float(confidence)
    _require(0 < c < 1, "confidence must be strictly between 0 and 1, got {}.".format(c))
    return c


# ---------------------------------------------------------------------------
# POST /ci/mean
# ---------------------------------------------------------------------------

def mean(payload: dict) -> SolutionResponse:
    """Confidence interval for the mean (3 input modes, auto-select case)."""
    mode = payload.get("mode", "summary")
    _require(mode in ("summary", "raw", "sums"),
             "mode must be 'summary', 'raw', or 'sums'.")

    confidence = _validate_confidence(payload.get("confidence"))
    alpha = 1.0 - confidence

    population_normal: bool = bool(payload.get("population_normal", False))

    # ---- Parse input by mode ------------------------------------------------
    sigma: Optional[float] = None
    s: Optional[float] = None
    x_bar: float
    n: int

    if mode == "summary":
        raw_n = payload.get("n")
        raw_xbar = payload.get("x_bar")
        _require(raw_n is not None, "n is required in summary mode.")
        _require(raw_xbar is not None, "x_bar is required in summary mode.")
        n = int(raw_n)
        x_bar = float(raw_xbar)
        _require(n >= 1, "n must be at least 1.")

        raw_sigma = payload.get("sigma")
        raw_s = payload.get("s")
        _require(raw_sigma is not None or raw_s is not None,
                 "Provide either sigma (population std dev) or s (sample std dev) in summary mode.")
        if raw_sigma is not None:
            sigma = float(raw_sigma)
            _require(sigma > 0, "sigma must be positive.")
        if raw_s is not None:
            s = float(raw_s)
            _require(s > 0, "s must be positive.")

    elif mode == "raw":
        data_raw = payload.get("data")
        _require(data_raw is not None and len(data_raw) >= 2,
                 "data must be a list of at least 2 numbers in raw mode.")
        data_arr = np.asarray(data_raw, dtype=float)
        n = len(data_arr)
        x_bar = float(np.mean(data_arr))
        s = float(np.std(data_arr, ddof=1))
        # sigma stays None in raw mode

    else:  # sums
        raw_n = payload.get("n")
        raw_sum_x = payload.get("sum_x")
        raw_sum_x2 = payload.get("sum_x2")
        _require(raw_n is not None, "n is required in sums mode.")
        _require(raw_sum_x is not None, "sum_x is required in sums mode.")
        _require(raw_sum_x2 is not None, "sum_x2 is required in sums mode.")
        n = int(raw_n)
        _require(n >= 2, "n must be at least 2 in sums mode (need ddof=1).")
        sum_x = float(raw_sum_x)
        sum_x2 = float(raw_sum_x2)
        x_bar = sum_x / n
        s_sq = (sum_x2 - sum_x ** 2 / n) / (n - 1)
        _require(s_sq >= 0, "Computed sample variance is negative — check your sums.")
        s = math.sqrt(s_sq)

    # ---- Case selection (lecture's "Very Important Remark") -----------------
    #  Case A: sigma known AND (population normal OR n >= 30)  -> Z with sigma
    #  Case B: sigma unknown AND n >= 30                       -> Z with s
    #  Case C: sigma unknown AND population approx. normal AND n < 30 -> T with n-1 df
    #  Otherwise: 422

    use_sigma: Optional[float] = None
    use_s: Optional[float] = None

    if sigma is not None:
        # sigma known branch
        if population_normal or n >= 30:
            case = "Z with sigma"
            cv = z_critical(alpha)
            margin = cv * sigma / math.sqrt(n)
            use_sigma = sigma
        else:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Cannot build a valid interval: sigma is known but the population is not "
                    "stated as normal and n < 30. Either supply s instead of sigma, assert "
                    "population normality, or collect n >= 30 observations."
                ),
            )
    else:
        # sigma unknown branch — s is available
        assert s is not None  # guaranteed by earlier parsing
        if n >= 30:
            case = "Z with s"
            cv = z_critical(alpha)
            margin = cv * s / math.sqrt(n)
            use_s = s
        elif population_normal:
            case = "T with s"
            df = n - 1
            cv = t_critical(alpha, df)
            margin = cv * s / math.sqrt(n)
            use_s = s
        else:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Cannot build a valid interval: sigma is unknown, n < 30, and normality "
                    "is not assumed. Either collect n >= 30 observations or assert that the "
                    "population is approximately normal."
                ),
            )

    lower = x_bar - margin
    upper = x_bar + margin

    # ---- Build steps (LaTeX strings) ----------------------------------------
    sb = StepsBuilder()
    sb.add(
        r"1 - \alpha = " + str(confidence)
        + r" \Rightarrow \alpha = " + str(round(alpha, 6))
        + r", \quad \alpha/2 = " + str(round(alpha / 2, 6))
    )

    if case == "T with s":
        df_val = n - 1
        sb.add(
            r"\text{Case: } \sigma \text{ unknown},\ n = " + str(n)
            + r" < 30,\ \text{population approx. normal}"
            + r" \Rightarrow t\text{-distribution with } df = " + str(df_val)
        )
        sb.add(
            r"t_{\alpha/2,\," + str(df_val) + r"} = t_{"
            + str(round(alpha / 2, 4)) + r",\," + str(df_val)
            + r"} = " + str(round(cv, 4))
        )
        sb.add(
            r"E = t_{\alpha/2} \cdot \dfrac{s}{\sqrt{n}} = "
            + str(round(cv, 4))
            + r" \times \dfrac{" + str(round(use_s, 4))
            + r"}{\sqrt{" + str(n) + r"}} = " + str(round(margin, 4))
        )
    elif case == "Z with sigma":
        cond_lbl = r"n \geq 30" if n >= 30 else r"\text{population normal}"
        sb.add(
            r"\text{Case: } \sigma \text{ known},\ "
            + cond_lbl
            + r" \Rightarrow Z\text{-distribution}"
        )
        sb.add(
            r"z_{\alpha/2} = z_{" + str(round(alpha / 2, 4))
            + r"} = " + str(round(cv, 4))
        )
        sb.add(
            r"E = z_{\alpha/2} \cdot \dfrac{\sigma}{\sqrt{n}} = "
            + str(round(cv, 4))
            + r" \times \dfrac{" + str(round(use_sigma, 4))
            + r"}{\sqrt{" + str(n) + r"}} = " + str(round(margin, 4))
        )
    else:  # Z with s
        sb.add(
            r"\text{Case: } \sigma \text{ unknown},\ n = " + str(n)
            + r" \geq 30 \Rightarrow Z\text{-distribution with } s"
        )
        sb.add(
            r"z_{\alpha/2} = z_{" + str(round(alpha / 2, 4))
            + r"} = " + str(round(cv, 4))
        )
        sb.add(
            r"E = z_{\alpha/2} \cdot \dfrac{s}{\sqrt{n}} = "
            + str(round(cv, 4))
            + r" \times \dfrac{" + str(round(use_s, 4))
            + r"}{\sqrt{" + str(n) + r"}} = " + str(round(margin, 4))
        )

    sb.add(
        r"\bar{x} \pm E = " + str(round(x_bar, 4))
        + r" \pm " + str(round(margin, 4))
    )
    sb.add(
        r"\text{Confidence Interval: }\left(" + str(round(lower, 4))
        + r",\ " + str(round(upper, 4)) + r"\right)"
    )

    # ---- Notes --------------------------------------------------------------
    notes: list = [
        "Point estimate: a single value (x\u0304) used as the best guess for \u03bc. "
        "Interval estimate: a range (x\u0304 \u00b1 E) that captures \u03bc with the stated confidence."
    ]
    if sigma is None and n < 30:
        notes.append(
            "Warning: n < 30 and normality is assumed (population_normal = true). "
            "Verify that the population is approximately normal before relying on this interval."
        )

    # ---- Result dict --------------------------------------------------------
    result: dict = {
        "lower": round(lower, 4),
        "upper": round(upper, 4),
        "margin": round(margin, 4),
        "x_bar": round(x_bar, 4),
        "critical_value": round(cv, 4),
        "case": case,
        "alpha": round(alpha, 6),
        "confidence": confidence,
    }
    if use_s is not None:
        result["s"] = round(use_s, 4)
    if use_sigma is not None:
        result["sigma"] = round(use_sigma, 4)
    if mode == "sums" and s is not None:
        result["s"] = round(s, 4)  # always expose s computed from sums

    # ---- Plot data (number line) --------------------------------------------
    span = max(upper - lower, 0.001)
    pad = span * 0.5
    plot = {
        "type": "interval",
        "lower": round(lower, 4),
        "upper": round(upper, 4),
        "x_bar": round(x_bar, 4),
        "plot_min": round(lower - pad, 4),
        "plot_max": round(upper + pad, 4),
    }

    return SolutionResponse(
        result=result,
        steps=sb.build(),
        plot=plot,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# POST /ci/sample-size
# ---------------------------------------------------------------------------

def sample_size(payload: dict) -> SolutionResponse:
    """Required sample size for a given margin of error."""
    confidence = _validate_confidence(payload.get("confidence"))
    alpha = 1.0 - confidence

    raw_sigma = payload.get("sigma") if payload.get("sigma") is not None else payload.get("s")
    raw_margin = payload.get("margin")

    _require(raw_sigma is not None, "sigma (or s) is required.")
    _require(raw_margin is not None, "margin is required.")

    sigma_val = float(raw_sigma)
    margin_val = float(raw_margin)

    _require(sigma_val > 0, "sigma (or s) must be positive.")
    _require(margin_val > 0, "margin must be positive.")

    cv = z_critical(alpha)
    n_exact = (cv * sigma_val / margin_val) ** 2
    n_ceil = math.ceil(n_exact)

    # Build steps
    sb = StepsBuilder()
    sb.add(
        r"1 - \alpha = " + str(confidence)
        + r" \Rightarrow \alpha = " + str(round(alpha, 6))
        + r", \quad \alpha/2 = " + str(round(alpha / 2, 6))
    )
    sb.add(
        r"z_{\alpha/2} = " + str(round(cv, 4))
    )
    sb.add(
        r"n = \left(\frac{z_{\alpha/2} \cdot \sigma}{E}\right)^2 = "
        + r"\left(\frac{" + str(round(cv, 4)) + r" \times " + str(sigma_val)
        + r"}{" + str(margin_val) + r"}\right)^2 = " + str(round(n_exact, 4))
    )
    sb.add(
        r"n = \lceil " + str(round(n_exact, 4)) + r" \rceil = "
        + str(n_ceil) + r" \quad \text{(always round UP)}"
    )

    # Chart data: n vs margin for a range of margins
    margins = [margin_val * (0.5 + 0.1 * i) for i in range(21)]
    ns = [math.ceil((cv * sigma_val / m) ** 2) for m in margins]

    plot = {
        "type": "n_vs_margin",
        "margins": [round(m, 6) for m in margins],
        "ns": ns,
        "highlighted_margin": margin_val,
        "highlighted_n": n_ceil,
    }

    result = {
        "n_exact": round(n_exact, 4),
        "n": n_ceil,
        "z": round(cv, 4),
        "alpha": round(alpha, 6),
        "confidence": confidence,
        "sigma": sigma_val,
        "margin": margin_val,
    }

    notes: list = [
        "Always round UP (ceiling) when computing required sample size \u2014 "
        "rounding down would give a margin of error larger than requested."
    ]

    return SolutionResponse(
        result=result,
        steps=sb.build(),
        plot=plot,
        notes=notes,
    )
