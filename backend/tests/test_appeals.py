from fastapi.testclient import TestClient

CREATE = {
    "channel": "email",
    "sender": "Андрей, СеверФуд",
    "received_at": "2026-08-13T16:40:00+03:00",
    "text": "Снова 17-я: температура уже +8 и продолжает расти.",
}


def _login(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"login": "dispatcher", "password": "secret"})
    assert response.status_code == 200


def test_appeals_require_login(db_client: TestClient) -> None:
    response = db_client.get("/api/v1/appeals/desk")
    assert response.status_code == 401


def test_create_and_card(db_client: TestClient) -> None:
    _login(db_client)
    created = db_client.post("/api/v1/appeals", json=CREATE)
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "new"
    assert body["run_status"] == "running"
    appeal_id = body["id"]
    stream = db_client.get(f"/api/v1/appeals/{appeal_id}/stream")
    assert stream.status_code == 200
    assert "run_finished" in stream.text

    card = db_client.get(f"/api/v1/appeals/{appeal_id}")
    assert card.status_code == 200
    payload = card.json()
    assert payload["card"]["schema_version"] == 1
    assert payload["card"]["intake"]["channel"] == "email"
    assert payload["card"]["facts"]["asset"]["binding"]["status"] == "empty"
    assert payload["auto_in_prod"] is False


def test_desk_has_four_widgets(db_client: TestClient) -> None:
    _login(db_client)
    db_client.post("/api/v1/appeals", json=CREATE)
    desk = db_client.get("/api/v1/appeals/desk")
    assert desk.status_code == 200
    widgets = desk.json()["widgets"]
    assert [item["status"] for item in widgets] == ["new", "clarify", "dispatch", "approve"]
    assert widgets[0]["count"] == 1
    assert widgets[0]["recent"][0]["text_preview"].startswith("Снова 17-я")


def test_journal_and_empty_filter(db_client: TestClient) -> None:
    _login(db_client)
    db_client.post("/api/v1/appeals", json=CREATE)
    items = db_client.get("/api/v1/appeals").json()["items"]
    assert len(items) == 1
    assert items[0]["created_by"] == "dispatcher"
    empty = db_client.get("/api/v1/appeals", params={"status": "done"})
    assert empty.status_code == 200
    assert empty.json()["items"] == []


def test_missing_appeal_is_404(db_client: TestClient) -> None:
    _login(db_client)
    assert db_client.get("/api/v1/appeals/9999").status_code == 404


def test_reply_lands_in_messages(db_client: TestClient) -> None:
    _login(db_client)
    appeal_id = db_client.post("/api/v1/appeals", json=CREATE).json()["id"]
    reply = db_client.post(
        f"/api/v1/appeals/{appeal_id}/replies",
        json={"text": "Это Дмитровское, ХУ-17"},
    )
    assert reply.status_code == 202
    assert reply.json()["run_status"] == "running"
    db_client.get(f"/api/v1/appeals/{appeal_id}/stream")
    messages = db_client.get(f"/api/v1/appeals/{appeal_id}/messages")
    assert messages.status_code == 200
    items = messages.json()["items"]
    assert len(items) == 1
    assert items[0]["kind"] == "dispatcher_reply"
    assert items[0]["body"]["text"].startswith("Это Дмитровское")


def test_stream_events(db_client: TestClient) -> None:
    _login(db_client)
    appeal_id = db_client.post("/api/v1/appeals", json=CREATE).json()["id"]
    response = db_client.get(f"/api/v1/appeals/{appeal_id}/stream")
    assert response.status_code == 200
    assert "run_started" in response.text
    assert "run_finished" in response.text
    assert db_client.get(f"/api/v1/appeals/{appeal_id}").json()["run_status"] == "idle"
