# Owner: Issue 5 - Check the Slides
"""Business logic for Check the Slides. Computes exact SciPy values to compare against lecture slides."""
import math
from typing import Any

from scipy import stats

from app.core.schemas import SolutionResponse
from app.core.stats_utils import t_critical, z_critical
from app.core.steps import StepsBuilder


def _build_slide_checks() -> list[dict[str, Any]]:
    """Compute exact SciPy values in code and compare against stored slide answers."""
    # L1 remark (iii): Verify with SciPy that Phi(b) - Phi(a) != 0 on (-1, 1)
    l1_remark_exact = float(stats.norm.cdf(1.0) - stats.norm.cdf(-1.0))

    # L1 clinic: X ~ N(mu=12, sigma^2=16 => sigma=4)
    l1_clinic_gt10 = float(stats.norm.sf(10.0, loc=12.0, scale=4.0))
    l1_clinic_between = float(
        stats.norm.cdf(14.0, loc=12.0, scale=4.0) - stats.norm.cdf(8.0, loc=12.0, scale=4.0)
    )

    # L1 N(12, 9): P(X > k) = 0.25 => k = 12 + z_{0.75} * 3
    l1_inv_k = float(stats.norm.isf(0.25, loc=12.0, scale=3.0))

    # L1 rounding example: N(16, 0.81), P(X <= 14)
    l1_round_prob = float(stats.norm.cdf(14.0, loc=16.0, scale=0.9))

    # L2 F table, row 27 (df2 = 27, alpha = 0.05, columns df1 = 9 and 10)
    l2_f_9_27 = float(stats.f.ppf(0.95, dfn=9, dfd=27))
    l2_f_10_27 = float(stats.f.ppf(0.95, dfn=10, dfd=27))

    # L3 tablets: n=12, sigma^2=16, P(s^2 > 25) => P(chi2_11 > 11*25/16)
    l3_tablets_prob = float(stats.chi2.sf(11.0 * 25.0 / 16.0, df=11))

    # L3 smokers: p=0.20, n=36, P(phat > 0.10)
    se_smokers = math.sqrt(0.20 * 0.80 / 36.0)
    l3_smokers_prob = float(stats.norm.sf(0.10, loc=0.20, scale=se_smokers))

    # L3 Kansas: p=0.35, n=15, P(phat < 0.20)
    se_kansas = math.sqrt(0.35 * 0.65 / 15.0)
    l3_kansas_prob = float(stats.norm.cdf(0.20, loc=0.35, scale=se_kansas))

    # L3 dogs: p=0.19, n=80, P(0.15 < phat < 0.20)
    se_dogs = math.sqrt(0.19 * 0.81 / 80.0)
    l3_dogs_prob = float(
        stats.norm.cdf(0.20, loc=0.19, scale=se_dogs)
        - stats.norm.cdf(0.15, loc=0.19, scale=se_dogs)
    )

    # L3 rounding example: standard error for p=0.37, n=125
    l3_round_se = math.sqrt(0.37 * 0.63 / 125.0)

    # L4 seniors: xbar=2.6, s=4, n=36, 95% CI
    z_95 = z_critical(0.05)
    m_seniors = z_95 * 4.0 / math.sqrt(36.0)
    l4_seniors_low = 2.6 - m_seniors
    l4_seniors_high = 2.6 + m_seniors

    # L4 cotton threads: n=12, xbar=7.38, s=1.24, 95% CI
    t_11 = t_critical(0.05, 11)
    m_cotton = t_11 * 1.24 / math.sqrt(12.0)
    l4_cotton_low = 7.38 - m_cotton
    l4_cotton_high = 7.38 + m_cotton

    # L4 sample of 20: n=20, xbar=32.8, s=4.51, 95% CI
    t_19 = t_critical(0.05, 19)
    m_sample20 = t_19 * 4.51 / math.sqrt(20.0)
    l4_s20_low = 32.8 - m_sample20
    l4_s20_high = 32.8 + m_sample20

    # L4 sample size: s=0.3, margin=0.05, 95% confidence
    n_exact_l4 = (z_95 * 0.3 / 0.05) ** 2
    l4_sample_size = math.ceil(n_exact_l4)

    # L4 rounding example: sigma=4, n=25, xbar=15, 95% CI (z=1.96 gives 13.4320, 16.5680)
    m_round_ci = z_95 * 4.0 / math.sqrt(25.0)
    l4_round_low = 15.0 - m_round_ci
    l4_round_high = 15.0 + m_round_ci

    items: list[dict[str, Any]] = [
        {
            "id": "l1-remark-iii",
            "lecture": "Lecture 1",
            "topic": "Remark (iii): Interval probability formula",
            "slide_answer": "phi(b) - phi(b)",
            "exact_answer": f"phi(b) - phi(a) (e.g., on [-1, 1]: {l1_remark_exact:.4f})",
            "exact_value": round(l1_remark_exact, 4),
            "category": "error",
            "differs": True,
            "explanation": "Typographical error on the slide: subtracting Phi(b) from itself always gives 0. The lower bound must use Phi(a).",
        },
        {
            "id": "l1-clinic-gt10",
            "lecture": "Lecture 1",
            "topic": "Clinic example: P(X > 10) for N(12, 16)",
            "slide_answer": "0.5987",
            "exact_answer": f"{l1_clinic_gt10:.4f}",
            "exact_value": round(l1_clinic_gt10, 4),
            "category": "error",
            "differs": True,
            "explanation": "z = (10 - 12)/4 = -0.50, so P(Z > -0.50) = Phi(0.50) = 0.6915. The slide misread the Z-table as Phi(0.25) = 0.5987.",
        },
        {
            "id": "l1-clinic-between",
            "lecture": "Lecture 1",
            "topic": "Clinic example: P(8 < X < 14) for N(12, 16)",
            "slide_answer": "0.2426",
            "exact_answer": f"{l1_clinic_between:.4f}",
            "exact_value": round(l1_clinic_between, 4),
            "category": "error",
            "differs": True,
            "explanation": "z_1 = (8 - 12)/4 = -1.0 and z_2 = (14 - 12)/4 = 0.50, giving Phi(0.50) - Phi(-1.0) = 0.6915 - 0.1587 = 0.5328.",
        },
        {
            "id": "l1-inverse-k",
            "lecture": "Lecture 1",
            "topic": "Inverse normal: N(12, 9), P(X > k) = 0.25",
            "slide_answer": "k = 10.025",
            "exact_answer": f"k = {l1_inv_k:.2f}",
            "exact_value": round(l1_inv_k, 2),
            "category": "error",
            "differs": True,
            "explanation": "Right tail P(X > k) = 0.25 means Phi(z) = 0.75 (z = +0.6745 > 0), so k = 12 + 0.6745(3) = 14.02, not below the mean.",
        },
        {
            "id": "l1-rounding-p14",
            "lecture": "Lecture 1",
            "topic": "Normal CDF: P(X <= 14) for N(16, 0.81)",
            "slide_answer": "0.0132",
            "exact_answer": f"{l1_round_prob:.4f}",
            "exact_value": round(l1_round_prob, 4),
            "category": "rounding",
            "differs": True,
            "explanation": "Rounding z = -2.2222... to 2 decimal places (-2.22) in the printed Z-table gives 0.0132 instead of 0.0131.",
        },
        {
            "id": "l2-f-table-row27",
            "lecture": "Lecture 2",
            "topic": "F table, row 27 (df2 = 27, alpha = 0.05, df1 = 9 and 10)",
            "slide_answer": "1.7306 and 1.6717",
            "exact_answer": f"{l2_f_9_27:.4f} and {l2_f_10_27:.4f}",
            "exact_value": [round(l2_f_9_27, 4), round(l2_f_10_27, 4)],
            "category": "error",
            "differs": True,
            "explanation": f"Row 27 (columns 9 and 10) in the slide's F table is out of sequence; scipy.stats.f.ppf(0.95, 9, 27) = {l2_f_9_27:.4f} and f.ppf(0.95, 10, 27) = {l2_f_10_27:.4f}.",
        },
        {
            "id": "l3-tablets-var",
            "lecture": "Lecture 3",
            "topic": "Tablets variance: P(s^2 > 25) with n = 12, sigma^2 = 16",
            "slide_answer": "0.25",
            "exact_answer": f"{l3_tablets_prob:.4f}",
            "exact_value": round(l3_tablets_prob, 4),
            "category": "error",
            "differs": True,
            "explanation": "chi^2 = (11)(25)/16 = 17.1875 with df = 11 gives upper-tail probability P(chi^2_11 > 17.1875) = 0.1025, not 0.25.",
        },
        {
            "id": "l3-smokers-prop",
            "lecture": "Lecture 3",
            "topic": "Smokers proportion: P(phat > 0.10) with p = 0.20, n = 36",
            "slide_answer": "0.9251",
            "exact_answer": f"{l3_smokers_prob:.4f}",
            "exact_value": round(l3_smokers_prob, 4),
            "category": "error",
            "differs": True,
            "explanation": "SE = sqrt(0.20 * 0.80 / 36) = 0.0667 gives z = -1.50, so P(Z > -1.50) = 0.9332 (slide used z = -1.44 -> 0.9251).",
        },
        {
            "id": "l3-kansas-prop",
            "lecture": "Lecture 3",
            "topic": "Kansas proportion: P(phat < 0.20) with p = 0.35, n = 15",
            "slide_answer": "0.8888",
            "exact_answer": f"{l3_kansas_prob:.4f}",
            "exact_value": round(l3_kansas_prob, 4),
            "category": "error",
            "differs": True,
            "explanation": "Because 0.20 < p = 0.35, z = -1.218 is negative and P(phat < 0.20) = 0.1116. The slide reported the upper tail 1 - 0.1112 = 0.8888.",
        },
        {
            "id": "l3-dogs-prop",
            "lecture": "Lecture 3",
            "topic": "Dogs proportion: P(0.15 < phat < 0.20) with p = 0.19, n = 80",
            "slide_answer": "0.9887",
            "exact_answer": f"{l3_dogs_prob:.4f}",
            "exact_value": round(l3_dogs_prob, 4),
            "category": "error",
            "differs": True,
            "explanation": "Phi(z_2) - Phi(z_1) = 0.5902 - 0.1809 = 0.4093. The slide mistakenly added the two cumulative probabilities instead of subtracting.",
        },
        {
            "id": "l3-rounding-se",
            "lecture": "Lecture 3",
            "topic": "Proportion standard error: p = 0.37, n = 125",
            "slide_answer": "0.0436",
            "exact_answer": f"{l3_round_se:.4f}",
            "exact_value": round(l3_round_se, 4),
            "category": "rounding",
            "differs": True,
            "explanation": "Intermediate rounding in sqrt(0.37 * 0.63 / 125) yielded 0.0436 on the slide; exact evaluation is 0.04318 -> 0.0432.",
        },
        {
            "id": "l4-seniors-ci",
            "lecture": "Lecture 4",
            "topic": "Seniors 95% CI: xbar = 2.6, s = 4, n = 36",
            "slide_answer": "(2.5, 2.7)",
            "exact_answer": f"({l4_seniors_low:.2f}, {l4_seniors_high:.2f})",
            "exact_value": [round(l4_seniors_low, 2), round(l4_seniors_high, 2)],
            "category": "error",
            "differs": True,
            "explanation": "With n = 36 >= 30, margin = 1.96 * (4 / sqrt(36)) = 1.3067, giving 2.6 +/- 1.31 = (1.29, 3.91), not (2.5, 2.7).",
        },
        {
            "id": "l4-cotton-threads",
            "lecture": "Lecture 4",
            "topic": "Cotton threads 95% CI: n = 12, xbar = 7.38, s = 1.24",
            "slide_answer": "t = 2.431, (6.51, 8.25)",
            "exact_answer": f"t = {t_11:.3f}, ({l4_cotton_low:.2f}, {l4_cotton_high:.2f})",
            "exact_value": {
                "t": round(t_11, 3),
                "lower": round(l4_cotton_low, 2),
                "upper": round(l4_cotton_high, 2),
            },
            "category": "error",
            "differs": True,
            "explanation": "For df = n - 1 = 11 and alpha = 0.05 (two-sided), t_{0.025, 11} = 2.201 (not 2.431), yielding (6.59, 8.17).",
        },
        {
            "id": "l4-sample-20",
            "lecture": "Lecture 4",
            "topic": "Sample of 20 95% CI: n = 20, xbar = 32.8, s = 4.51",
            "slide_answer": "t = 3.031, (29.74, 35.86)",
            "exact_answer": f"t = {t_19:.3f}, ({l4_s20_low:.2f}, {l4_s20_high:.2f})",
            "exact_value": {
                "t": round(t_19, 3),
                "lower": round(l4_s20_low, 2),
                "upper": round(l4_s20_high, 2),
            },
            "category": "error",
            "differs": True,
            "explanation": "For df = n - 1 = 19 and alpha = 0.05 (two-sided), t_{0.025, 19} = 2.093 (not 3.031), yielding (30.69, 34.91).",
        },
        {
            "id": "l4-sample-size",
            "lecture": "Lecture 4",
            "topic": "Sample size for 95% CI: s = 0.3, margin = 0.05",
            "slide_answer": "132",
            "exact_answer": f"{l4_sample_size}",
            "exact_value": l4_sample_size,
            "category": "error",
            "differs": True,
            "explanation": "n = ceil((1.96 * 0.3 / 0.05)^2) = ceil(138.29) = 139, not 132.",
        },
        {
            "id": "l4-rounding-ci",
            "lecture": "Lecture 4",
            "topic": "Known-sigma 95% CI: sigma = 4, n = 25, xbar = 15",
            "slide_answer": "(13.4320, 16.5680) using z = 1.96",
            "exact_answer": f"({l4_round_low:.4f}, {l4_round_high:.4f}) (2-dec: ({l4_round_low:.2f}, {l4_round_high:.2f}))",
            "exact_value": [round(l4_round_low, 4), round(l4_round_high, 4)],
            "category": "rounding",
            "differs": True,
            "explanation": "Using table-rounded z = 1.96 vs exact z_{0.025} = 1.959964 differs by 0.00003 at 4 decimal places; both round to (13.43, 16.57).",
        },
    ]
    return items


def slides(payload: dict[str, Any] | None = None) -> SolutionResponse:
    """Return lecture slide answers compared against exact SciPy computations."""
    items = _build_slide_checks()
    error_count = sum(1 for item in items if item["category"] == "error")
    rounding_count = sum(1 for item in items if item["category"] == "rounding")

    steps = StepsBuilder()
    steps.add(
        r"\text{Re-evaluate each lecture example directly with } \texttt{scipy.stats} \text{ (never printed tables).}"
    )
    steps.add(
        rf"\text{{Total audited items: }} {len(items)} \quad (\text{{Errors: }} {error_count},\ \text{{Rounding differences: }} {rounding_count})"
    )

    notes = [
        f"Found {error_count} substantive slide errors and {rounding_count} minor rounding differences compared to exact SciPy values."
    ]

    return SolutionResponse(
        result={
            "items": items,
            "total": len(items),
            "error_count": error_count,
            "rounding_count": rounding_count,
        },
        steps=steps.build(),
        plot=None,
        notes=notes,
    )