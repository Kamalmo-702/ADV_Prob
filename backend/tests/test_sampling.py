# Owner: Issue 3 - Sampling Distributions
"""Lecture 2 and 3 examples.

Slide answers come from printed tables, so we compare with a tolerance. Where a slide
is wrong, we assert the SciPy value and note the slide's number in a comment.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def post(path: str, **body) -> dict:
    response = client.post(f"/sampling/{path}", json=body)
    assert response.status_code == 200, response.text
    return response.json()


# ---- response shape ----
def test_response_shape() -> None:
    body = post("mean", mu=200, n=16, sigma2=36, a=199, b=203)
    assert set(body) >= {"result", "steps", "plot", "notes"}
    assert all(isinstance(s, str) for s in body["steps"]) and len(body["steps"]) >= 5
    plot = body["plot"]
    assert len(plot["curve"]["x"]) == len(plot["curve"]["y"])
    assert plot["regions"]["less"] and plot["regions"]["greater"] and plot["regions"]["between"]
    assert plot["se_vs_n"]["current"]["n"] == 16


# ---- Lecture 2: mean ----
def test_mean_n16_variance_36() -> None:  # slide 14: 0.251
    r = post("mean", mu=200, n=16, sigma2=36, a=199)["result"]
    assert r["case"] == "Z_sigma_known"
    assert r["p_less"] == pytest.approx(0.251, abs=2e-3)


def test_bulbs() -> None:  # slide 15: 0.006
    assert post("mean", mu=800, sigma=40, n=16, a=775)["result"]["p_less"] == pytest.approx(0.0062, abs=5e-4)


def test_n64_sigma_known() -> None:  # slide 16: 0.0668 and 0.0062
    assert post("mean", mu=3.2, sigma=1.6, n=64, a=3.5)["result"]["p_greater"] == pytest.approx(0.0668, abs=1e-4)
    assert post("mean", mu=3.2, sigma=1.6, n=64, a=2.7)["result"]["p_less"] == pytest.approx(0.0062, abs=1e-4)


def test_n64_sigma_unknown_uses_z_with_s() -> None:  # slide 17: 0.9452 and 0.0082
    r = post("mean", mu=3.2, s=5, n=64, a=2.2)["result"]
    assert r["case"] == "Z_s_large_n" and r["statistic"] == "Z"
    assert r["p_greater"] == pytest.approx(0.9452, abs=1e-4)
    assert post("mean", mu=3.2, s=5, n=64, a=1.7)["result"]["p_less"] == pytest.approx(0.0082, abs=1e-4)


def test_tubes_homework() -> None:  # slide 18 (left to the students)
    assert post("mean", mu=800, sigma=40, n=16, a=815)["result"]["p_greater"] == pytest.approx(0.0668, abs=1e-4)
    assert post("mean", mu=800, sigma=40, n=16, a=790, b=810)["result"]["p_between"] == pytest.approx(0.6827, abs=1e-4)


def test_small_n_unknown_sigma_uses_t() -> None:
    r = post("mean", mu=10, s=2, n=9, a=11)["result"]
    assert r["case"] == "T_df" and r["statistic"] == "T" and r["df"] == 8
    assert "T" in r["reason"] and "df" in r["reason"]


def test_t_vs_z_threshold() -> None:
    assert post("mean", mu=0, s=1, n=29, a=0.1)["result"]["statistic"] == "T"
    assert post("mean", mu=0, s=1, n=30, a=0.1)["result"]["statistic"] == "Z"


# ---- Lecture 3: variance ----
def test_variance_n25() -> None:  # slide 3: 0.05 and 0.94
    assert post("variance", n=25, sigma2=6, a=9.1)["result"]["p_greater"] == pytest.approx(0.05, abs=2e-3)
    assert post("variance", n=25, sigma2=6, a=3.462, b=10.745)["result"]["p_between"] == pytest.approx(0.94, abs=2e-3)


def test_variance_n8() -> None:  # slide 4: 0.76 (table 0.84 - 0.08); SciPy 0.7554
    assert post("variance", n=8, sigma2=4, a=1.5, b=6)["result"]["p_between"] == pytest.approx(0.76, abs=6e-3)


def test_tablets() -> None:
    # Slide 5 prints 0.25, but chi2 = 17.1875 with df = 11 gives about 0.10
    # (the slide's own table has 17.27 at alpha = 0.100).
    r = post("variance", n=12, sigma2=16, a=25)["result"]
    assert r["chi2_a"] == pytest.approx(17.1875)
    assert r["p_greater"] == pytest.approx(0.1025, abs=1e-3)
    assert r["e_s2"] == 16 and r["v_s2"] == pytest.approx(2 * 16**2 / 11)


# ---- Lecture 3: proportion ----
def test_p037_n125() -> None:  # slide 8: var 0.0019, sd 0.0436 (slide rounds before the square root; exact 0.0432)
    r = post("proportion", p=0.37, n=125, a=0.4)["result"]
    assert r["variance"] == pytest.approx(0.0019, abs=5e-5)
    assert r["standard_error"] == pytest.approx(0.0432, abs=5e-5)


def test_factory_smokers() -> None:  # slide 9: 0.9251 (slide rounds z to -1.49; exact z = -1.5)
    r = post("proportion", population_size=100, population_successes=20, n=36, a=0.1)["result"]
    assert r["p"] == 0.2 and r["z_a"] == pytest.approx(-1.5)
    assert r["p_greater"] == pytest.approx(0.9332, abs=1e-4)


def test_online_learning() -> None:  # slide 10: sd 0.042 and 0.117
    r = post("proportion", p=0.3, n=120, a=0.35)["result"]
    assert r["standard_error"] == pytest.approx(0.042, abs=5e-4)
    assert r["p_greater"] == pytest.approx(0.117, abs=2e-3)


def test_kansas() -> None:
    # Slide 11 prints 0.8888 (sign slip: z = -1.22, not +1.22). Correct: P(Z < -1.22) = 0.111.
    body = post("proportion", p=0.35, n=15, a=0.2)
    assert body["result"]["p_less"] == pytest.approx(0.1116, abs=1e-3)
    assert body["notes"] == []  # np = 5.25, so no warning


def test_dogs() -> None:
    # Slide 12 prints z = -9.12 and 2.28 (decimal slip; real z = -0.91 and 0.23) and 0.9887.
    r = post("proportion", p=0.19, n=80, a=0.15, b=0.2)["result"]
    assert r["z_a"] == pytest.approx(-0.912, abs=1e-3) and r["z_b"] == pytest.approx(0.228, abs=1e-3)
    assert r["p_between"] == pytest.approx(0.4093, abs=1e-3)


def test_smokers_18_homework() -> None:  # slide 13 (left to the students)
    r = post("proportion", p=0.18, n=200, a=0.15)["result"]
    assert r["standard_error"] == pytest.approx(0.0272, abs=1e-4)
    assert r["p_less"] == pytest.approx(0.1347, abs=1e-3)


# ---- warnings and validation ----
def test_normal_approximation_warning() -> None:
    assert "np" in post("proportion", p=0.1, n=30, a=0.2)["notes"][0]      # np = 3
    assert post("proportion", p=0.9, n=30, a=0.8)["notes"]                  # n(1-p) = 3


@pytest.mark.parametrize(
    "path, body",
    [
        ("mean", {"mu": 0, "n": 10, "a": 1}),                      # neither sigma nor s
        ("mean", {"mu": 0, "n": 1, "s": 2, "a": 1}),               # T needs n >= 2
        ("mean", {"mu": 0, "n": 10, "sigma": 1, "a": 1, "b": 0}),  # b <= a
        ("variance", {"n": 1, "sigma2": 4, "a": 1}),
        ("variance", {"n": 10, "sigma2": -4, "a": 1}),
        ("proportion", {"p": 1.2, "n": 10, "a": 0.5}),
        ("proportion", {"n": 10, "a": 0.5}),                       # no p and no N, X
        ("proportion", {"population_size": 10, "population_successes": 20, "n": 5, "a": 0.5}),
    ],
)
def test_validation_errors(path: str, body: dict) -> None:
    assert client.post(f"/sampling/{path}", json=body).status_code == 422
