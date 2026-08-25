from fastapi.testclient import TestClient

CREATE_OK = {
    "customer_id": "C-101",
    "site_id": "S-MSK-01",
    "asset_id": "A-1003",
    "contract_id": "K-101",
    "summary": "ХУ-18 не запускается после перезагрузки",
    "priority": "high",
}


def test_dry_run_create(client: TestClient) -> None:
    response = client.post("/itsm/v1/tickets", json=CREATE_OK)
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["persisted"] is False
    assert body["would_ticket_id"] == "T-885"
    assert body["would_status"] == "new"
    assert all(check["passed"] for check in body["checks"])


def test_dry_run_id_is_stable(client: TestClient) -> None:
    first = client.post("/itsm/v1/tickets", json=CREATE_OK).json()["would_ticket_id"]
    second = client.post("/itsm/v1/tickets", json=CREATE_OK).json()["would_ticket_id"]
    assert first == second
    listed = client.get("/itsm/v1/tickets", params={"asset_id": "A-1003"})
    assert listed.json()["items"] == []


def test_flk_failed_is_400(client: TestClient) -> None:
    response = client.post(
        "/itsm/v1/tickets",
        json={
            "customer_id": "C-101",
            "site_id": "S-MSK-01",
            "asset_id": "A-2001",
            "contract_id": "K-101",
            "summary": "чужой актив",
            "priority": "high",
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["accepted"] is False
    assert body["code"] == "flk_failed"
    asset_check = next(check for check in body["checks"] if check["id"] == "asset_belongs_to_site")
    assert asset_check["passed"] is False


def test_patch_unknown_ticket(client: TestClient) -> None:
    response = client.patch("/itsm/v1/tickets/T-999", json={"summary": "нет такой"})
    assert response.status_code == 400
    body = response.json()
    assert body["accepted"] is False
    exists = next(check for check in body["checks"] if check["id"] == "ticket_exists")
    assert exists["passed"] is False
