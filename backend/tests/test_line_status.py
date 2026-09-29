from fastapi.testclient import TestClient


def _line_id(client: TestClient) -> int:
    rows = client.get("/api/lines").json()
    return rows[0]["id"]


def test_seeded_line_is_active(client: TestClient):
    rows = client.get("/api/lines").json()
    assert rows, "seed data should contain at least the B12 line"
    b12 = next(r for r in rows if r["code"] == "B12")
    assert b12["is_active"] is True


def test_detection_runs_while_active(client: TestClient):
    line_id = _line_id(client)
    res = client.post(f"/api/reports/run?line_id={line_id}")
    assert res.status_code == 200
    assert "events" in res.json()


def test_timeline_reports_active_flag(client: TestClient):
    line_id = _line_id(client)
    res = client.get(f"/api/reports/timeline?line_id={line_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["is_active"] is True
    assert isinstance(body["marks"], list)


def test_deactivate_blocks_detection_with_clear_message(client: TestClient):
    line_id = _line_id(client)
    assert client.post(f"/api/lines/{line_id}/deactivate").status_code == 200
    assert client.get("/api/lines").json()[0]["is_active"] is False

    run = client.post(f"/api/reports/run?line_id={line_id}")
    assert run.status_code == 409
    assert run.json()["detail"] == "线路已停用"
    assert "到站" not in run.json()["detail"]

    sug = client.get(f"/api/reports/suggestions?line_id={line_id}")
    assert sug.status_code == 409
    assert sug.json()["detail"] == "线路已停用"


def test_timeline_still_opens_when_deactivated(client: TestClient):
    line_id = _line_id(client)
    res = client.get(f"/api/reports/timeline?line_id={line_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["is_active"] is False
    # Historical arrival marks remain available, no error raised.
    assert isinstance(body["marks"], list)


def test_history_still_viewable_when_deactivated(client: TestClient):
    reports = client.get("/api/reports").json()
    assert reports, "the report generated before deactivation must remain viewable"
    assert all("events" in r and "created_at" in r for r in reports)


def test_reactivate_resumes_detection(client: TestClient):
    line_id = _line_id(client)
    assert client.post(f"/api/lines/{line_id}/activate").status_code == 200
    assert client.get("/api/lines").json()[0]["is_active"] is True
    res = client.post(f"/api/reports/run?line_id={line_id}")
    assert res.status_code == 200


def test_unknown_line_returns_404(client: TestClient):
    assert client.post("/api/lines/99999/deactivate").status_code == 404
