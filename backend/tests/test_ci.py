# Owner: Issue 4 - Confidence Intervals & Sample Size
"""Tests for /ci/mean and /ci/sample-size.

Reference values computed with SciPy; tolerance 1e-2 for bounds (issue says 1e-3
but the reference values are rounded to 2 dp, so 1e-2 is fair).
"""
import math
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TOL = 1e-2  # tolerance for interval bounds
TOL_EXACT = 1e-3  # tighter tolerance for critical values / n_exact


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ci_mean(body: dict):
    resp = client.post("/ci/mean", json=body)
    assert resp.status_code == 200, resp.text
    return resp.json()


def ci_ss(body: dict):
    resp = client.post("/ci/sample-size", json=body)
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Case A – Z with sigma (sigma known, n >= 30 OR population normal)
# ---------------------------------------------------------------------------

def test_z_sigma_n25_normal():
    """sigma=4, n=25, xbar=15, 95%, population_normal=True → (13.43, 16.57)."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": True,
        "x_bar": 15,
        "n": 25,
        "sigma": 4,
    }
    data = ci_mean(body)
    r = data["result"]
    assert r["case"] == "Z with sigma"
    assert abs(r["lower"] - 13.43) < TOL, r
    assert abs(r["upper"] - 16.57) < TOL, r


def test_z_sigma_n30():
    """sigma=40, n=30, xbar=780, 95% → (765.69, 794.31)."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": False,
        "x_bar": 780,
        "n": 30,
        "sigma": 40,
    }
    data = ci_mean(body)
    r = data["result"]
    assert r["case"] == "Z with sigma"
    assert abs(r["lower"] - 765.69) < TOL, r
    assert abs(r["upper"] - 794.31) < TOL, r


# ---------------------------------------------------------------------------
# Case B – Z with s (sigma unknown, n >= 30)
# ---------------------------------------------------------------------------

def test_z_s_n36():
    """s=4, n=36, xbar=2.6, 95% → (1.29, 3.91)."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": False,
        "x_bar": 2.6,
        "n": 36,
        "s": 4,
    }
    data = ci_mean(body)
    r = data["result"]
    assert r["case"] == "Z with s"
    assert abs(r["lower"] - 1.29) < TOL, r
    assert abs(r["upper"] - 3.91) < TOL, r


def test_sums_mode():
    """sums: n=40, sum_x=280, sum_x2=2100, 95% → xbar=7, s≈1.8947, (6.41, 7.59)."""
    body = {
        "mode": "sums",
        "confidence": 0.95,
        "population_normal": False,
        "n": 40,
        "sum_x": 280,
        "sum_x2": 2100,
    }
    data = ci_mean(body)
    r = data["result"]
    assert r["case"] == "Z with s"
    assert abs(r["x_bar"] - 7.0) < TOL_EXACT, r
    assert abs(r["s"] - 1.8947) < TOL, r
    assert abs(r["lower"] - 6.41) < TOL, r
    assert abs(r["upper"] - 7.59) < TOL, r


# ---------------------------------------------------------------------------
# Case C – T with s (sigma unknown, n < 30, population approx. normal)
# ---------------------------------------------------------------------------

def test_t_n12():
    """n=12, xbar=7.38, s=1.24, 95% → t=2.201, (6.59, 8.17)."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": True,
        "x_bar": 7.38,
        "n": 12,
        "s": 1.24,
    }
    data = ci_mean(body)
    r = data["result"]
    assert r["case"] == "T with s"
    assert abs(r["critical_value"] - 2.201) < TOL, r
    assert abs(r["lower"] - 6.59) < TOL, r
    assert abs(r["upper"] - 8.17) < TOL, r


def test_t_n20():
    """n=20, xbar=32.8, s=4.51, 95% → t=2.093, (30.69, 34.91)."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": True,
        "x_bar": 32.8,
        "n": 20,
        "s": 4.51,
    }
    data = ci_mean(body)
    r = data["result"]
    assert r["case"] == "T with s"
    assert abs(r["critical_value"] - 2.093) < TOL, r
    assert abs(r["lower"] - 30.69) < TOL, r
    assert abs(r["upper"] - 34.91) < TOL, r


# ---------------------------------------------------------------------------
# Raw mode
# ---------------------------------------------------------------------------

def test_raw_mode_basic():
    """Raw data with n>=30 should use Z with s."""
    import numpy as np
    rng = np.random.default_rng(42)
    data_list = rng.normal(loc=5.0, scale=2.0, size=50).tolist()
    body = {
        "mode": "raw",
        "confidence": 0.95,
        "population_normal": False,
        "data": data_list,
    }
    resp = ci_mean(body)
    r = resp["result"]
    assert r["case"] == "Z with s"
    # interval should contain the true mean roughly
    assert r["lower"] < r["x_bar"] < r["upper"]


# ---------------------------------------------------------------------------
# Sample size
# ---------------------------------------------------------------------------

def test_sample_size_basic():
    """s=0.3, margin=0.05, 95% → n_exact=138.29, n=139."""
    body = {"confidence": 0.95, "s": 0.3, "margin": 0.05}
    data = ci_ss(body)
    r = data["result"]
    assert abs(r["n_exact"] - 138.29) < TOL, r
    assert r["n"] == 139


# ---------------------------------------------------------------------------
# 422 / invalid input cases
# ---------------------------------------------------------------------------

def test_sigma_known_n_small_not_normal_raises_422():
    """sigma known, n<30, population NOT normal → 422."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": False,
        "x_bar": 15,
        "n": 10,
        "sigma": 4,
    }
    resp = client.post("/ci/mean", json=body)
    assert resp.status_code == 422, resp.text


def test_sigma_unknown_n_small_not_normal_raises_422():
    """sigma unknown, n<30, population NOT normal → 422."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": False,
        "x_bar": 7.38,
        "n": 12,
        "s": 1.24,
    }
    resp = client.post("/ci/mean", json=body)
    assert resp.status_code == 422, resp.text


def test_confidence_out_of_range_raises_422():
    """confidence outside (0,1) → 422."""
    body = {
        "mode": "summary",
        "confidence": 1.5,
        "population_normal": False,
        "x_bar": 15,
        "n": 36,
        "s": 4,
    }
    resp = client.post("/ci/mean", json=body)
    assert resp.status_code == 422, resp.text


def test_negative_sigma_raises_422():
    """Negative sigma → 422."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": True,
        "x_bar": 15,
        "n": 25,
        "sigma": -4,
    }
    resp = client.post("/ci/mean", json=body)
    assert resp.status_code == 422, resp.text


def test_sample_size_missing_sigma_raises_422():
    """Sample size without sigma/s → 422."""
    body = {"confidence": 0.95, "margin": 0.05}
    resp = client.post("/ci/sample-size", json=body)
    assert resp.status_code == 422, resp.text


def test_sample_size_zero_margin_raises_422():
    """Sample size with margin=0 → 422."""
    body = {"confidence": 0.95, "sigma": 0.3, "margin": 0}
    resp = client.post("/ci/sample-size", json=body)
    assert resp.status_code == 422, resp.text


# ---------------------------------------------------------------------------
# Response structure
# ---------------------------------------------------------------------------

def test_response_has_required_fields():
    """Every response includes result, steps, plot, notes."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": False,
        "x_bar": 2.6,
        "n": 36,
        "s": 4,
    }
    data = ci_mean(body)
    for key in ("result", "steps", "plot", "notes"):
        assert key in data, f"Missing key: {key}"
    assert len(data["steps"]) > 0
    assert isinstance(data["notes"], list)


def test_steps_are_strings():
    """Steps must be a list of strings (LaTeX)."""
    body = {
        "mode": "summary",
        "confidence": 0.95,
        "population_normal": True,
        "x_bar": 15,
        "n": 25,
        "sigma": 4,
    }
    data = ci_mean(body)
    for step in data["steps"]:
        assert isinstance(step, str)
