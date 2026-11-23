# Owner: Issue 5 - CLT Simulator & CI Coverage Demo
import time

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_clt_simulate_convergence_and_shape() -> None:
    response = client.post(
        "/clt/simulate",
        json={"population": "exponential", "n": 100, "samples": 5000, "seed": 42},
    )
    assert response.status_code == 200
    body = response.json()
    res = body["result"]

    assert res["pop_mean"] == pytest.approx(1.0, abs=1e-4)
    assert res["pop_sd"] == pytest.approx(1.0, abs=1e-4)
    assert res["theoretical_se"] == pytest.approx(0.1, abs=1e-4)
    assert res["mean_of_means"] == pytest.approx(res["pop_mean"], abs=0.02)
    assert res["sd_of_means"] == pytest.approx(res["theoretical_se"], abs=0.01)

    plot = body["plot"]
    assert "population_hist" in plot
    assert "means_hist" in plot
    assert "normal_curve" in plot
    assert len(plot["means_hist"]["counts"]) == len(plot["means_hist"]["edges"]) - 1
    assert len(plot["normal_curve"]["x"]) == len(plot["normal_curve"]["y"])
    assert len(body["steps"]) >= 4


@pytest.mark.parametrize("population", ["uniform", "exponential", "skewed", "bimodal"])
def test_clt_all_populations(population: str) -> None:
    response = client.post(
        "/clt/simulate",
        json={"population": population, "n": 50, "samples": 2000, "seed": 7},
    )
    assert response.status_code == 200
    res = response.json()["result"]
    assert res["mean_of_means"] == pytest.approx(res["pop_mean"], abs=0.1)
    assert res["sd_of_means"] == pytest.approx(res["theoretical_se"], abs=0.03)


def test_clt_simulate_performance_max_bounds() -> None:
    start = time.perf_counter()
    response = client.post(
        "/clt/simulate",
        json={"population": "skewed", "n": 500, "samples": 20000, "seed": 123},
    )
    elapsed = time.perf_counter() - start
    assert response.status_code == 200
    assert elapsed < 2.0


def test_clt_simulate_validation_422() -> None:
    bad_payloads = [
        {"population": "uniform", "n": 0, "samples": 1000},
        {"population": "uniform", "n": 501, "samples": 1000},
        {"population": "uniform", "n": 30, "samples": 50},
        {"population": "uniform", "n": 30, "samples": 20001},
        {"population": "gamma_unknown", "n": 30, "samples": 1000},
    ]
    for payload in bad_payloads:
        res = client.post("/clt/simulate", json=payload)
        assert res.status_code == 422


def test_clt_coverage_95_percent() -> None:
    response = client.post(
        "/clt/coverage",
        json={"mu": 50.0, "sigma": 10.0, "n": 25, "confidence": 0.95, "intervals": 100, "seed": 42},
    )
    assert response.status_code == 200
    body = response.json()
    res = body["result"]

    assert res["total_intervals"] == 100
    assert len(res["intervals"]) == 100
    assert res["coverage_rate"] == pytest.approx(0.95, abs=0.05)

    for iv in res["intervals"]:
        assert iv["lower"] < iv["upper"]
        assert iv["contains_mu"] == (iv["lower"] <= 50.0 <= iv["upper"])


def test_clt_coverage_validation_422() -> None:
    assert (
        client.post(
            "/clt/coverage",
            json={"mu": 0, "sigma": -2, "n": 25, "confidence": 0.95},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/clt/coverage",
            json={"mu": 0, "sigma": 5, "n": 25, "confidence": 1.2},
        ).status_code
        == 422
    )