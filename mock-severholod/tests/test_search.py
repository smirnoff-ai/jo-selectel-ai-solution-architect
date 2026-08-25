from fastapi.testclient import TestClient


def test_two_hu17_without_site(client: TestClient) -> None:
    response = client.get("/eam/v1/assets", params={"local_code": "ХУ-17"})
    assert response.status_code == 200
    ids = {item["asset_id"] for item in response.json()["items"]}
    assert ids == {"A-1001", "A-1002"}


def test_hu17_on_moscow_site(client: TestClient) -> None:
    response = client.get(
        "/eam/v1/assets",
        params={"local_code": "ХУ-17", "site_id": "S-MSK-01"},
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["asset_id"] for item in items] == ["A-1001"]


def test_empty_search_is_200(client: TestClient) -> None:
    response = client.get("/crm/v1/sites", params={"q": "НеизвестнаяФирма"})
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_sites_without_params_is_422(client: TestClient) -> None:
    response = client.get("/crm/v1/sites")
    assert response.status_code == 422
    assert response.json()["code"] == "validation"


def test_ticket_t884_has_contract(client: TestClient) -> None:
    response = client.get("/itsm/v1/tickets/T-884")
    assert response.status_code == 200
    body = response.json()
    assert body["customer_id"] == "C-101"
    assert body["site_id"] == "S-MSK-01"
    assert body["contract_id"] == "K-101"


def test_open_tickets_include_t884(client: TestClient) -> None:
    response = client.get("/itsm/v1/tickets", params={"site_id": "S-MSK-01", "status": "open"})
    assert response.status_code == 200
    ids = {item["ticket_id"] for item in response.json()["items"]}
    assert ids == {"T-884"}


def test_missing_asset_is_404(client: TestClient) -> None:
    response = client.get("/eam/v1/assets/A-9999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_contract_sla_codes(client: TestClient) -> None:
    response = client.get("/contracts/v1/contracts", params={"site_id": "S-MSK-01"})
    assert response.status_code == 200
    assert response.json()["items"][0]["response_sla"] == "60_minutes"
