"""Shared statistical helpers (everything else belongs to the module owners)."""
from scipy import stats


def _check_alpha(alpha: float) -> None:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")


def z_critical(alpha: float) -> float:
    """Two-sided critical value z_{alpha/2}. Example: alpha=0.05 -> 1.96."""
    _check_alpha(alpha)
    return float(stats.norm.ppf(1 - alpha / 2))


def t_critical(alpha: float, df: int) -> float:
    """Two-sided critical value t_{alpha/2, df}. Example: alpha=0.05, df=11 -> 2.201."""
    _check_alpha(alpha)
    if df < 1:
        raise ValueError("df must be at least 1")
    return float(stats.t.ppf(1 - alpha / 2, df))
