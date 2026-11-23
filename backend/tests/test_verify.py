# Owner: Issue 5 - Check the Slides
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_slides_endpoint_contains_all_discrepancies() -> None:
    response = client.get("/verify/slides")
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body

    items = body["result"]["items"]
    by_id = {item["id"]: item for item in items}

    expected_ids = {
        "l1-remark-iii",
        "l1-clinic-gt10",
        "l1-clinic-between",
        "l1-inverse-k",
        "l1-rounding-p14",
        "l2-f-table-row27",
        "l3-tablets-var",
        "l3-smokers-prop",
        "l3-kansas-prop",
        "l3-dogs-prop",
        "l3-rounding-se",
        "l4-seniors-ci",
        "l4-cotton-threads",
        "l4-sample-20",
        "l4-sample-size",
        "l4-rounding-ci",
    }
    assert expected_ids.issubset(by_id.keys())

    assert "phi(b) - phi(a)" in by_id["l1-remark-iii"]["exact_answer"]
    assert by_id["l1-clinic-gt10"]["exact_answer"] == "0.6915"
    assert by_id["l1-clinic-between"]["exact_answer"] == "0.5328"
    assert by_id["l1-inverse-k"]["exact_answer"] == "k = 14.02"
    assert by_id["l2-f-table-row27"]["exact_answer"] == "2.2501 and 2.2043"
    assert by_id["l3-tablets-var"]["exact_answer"] == "0.1025"
    assert by_id["l3-smokers-prop"]["exact_answer"] == "0.9332"
    assert by_id["l3-kansas-prop"]["exact_answer"] == "0.1116"
    assert by_id["l3-dogs-prop"]["exact_answer"] == "0.4093"
    assert by_id["l3-rounding-se"]["exact_answer"] == "0.0432"
    assert by_id["l3-rounding-se"]["category"] == "rounding"
    assert by_id["l4-seniors-ci"]["exact_answer"] == "(1.29, 3.91)"
    assert by_id["l4-cotton-threads"]["exact_answer"] == "t = 2.201, (6.59, 8.17)"
    assert by_id["l4-sample-20"]["exact_answer"] == "t = 2.093, (30.69, 34.91)"
    assert by_id["l4-sample-size"]["exact_answer"] == "139"

    for item in items:
        assert item["category"] in {"error", "rounding"}
        assert isinstance(item["differs"], bool)
        assert item["explanation"]