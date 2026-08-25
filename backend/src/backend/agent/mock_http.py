from typing import Any

import httpx


class MockHttp:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def get(self, path: str, params: dict[str, Any] | None = None) -> tuple[int, Any]:
        response = self._client.get(path, params=params)
        return response.status_code, _body(response)

    def post(self, path: str, payload: dict[str, Any]) -> tuple[int, Any]:
        response = self._client.post(path, json=payload)
        return response.status_code, _body(response)

    def patch(self, path: str, payload: dict[str, Any]) -> tuple[int, Any]:
        response = self._client.patch(path, json=payload)
        return response.status_code, _body(response)


def _body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {"detail": response.text}
