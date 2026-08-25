from typing import Any


def slot(card: dict[str, Any], name: str) -> dict[str, Any]:
    return card["facts"][name]


def binding_status(card: dict[str, Any], name: str) -> str:
    return str(slot(card, name)["binding"]["status"])


def set_binding(
    card: dict[str, Any],
    name: str,
    *,
    status: str,
    id_: str | None = None,
    label: str | None = None,
    candidates: list[dict[str, Any]] | None = None,
) -> None:
    slot(card, name)["binding"] = {
        "status": status,
        "id": id_,
        "label": label,
        "candidates": candidates or [],
    }


def add_system_evidence(
    card: dict[str, Any],
    name: str,
    *,
    source: str,
    record_id: str,
    label: str | None,
) -> None:
    evidences = slot(card, name)["evidences"]
    for item in evidences:
        record = item.get("record") or {}
        if item.get("kind") == "system" and record.get("id") == record_id:
            return
    evidences.append(
        {
            "kind": "system",
            "source": source,
            "fragment": None,
            "record": {"system": source, "id": record_id, "label": label},
            "confidence": "high",
        }
    )


def mentioned(card: dict[str, Any], name: str) -> bool:
    value = slot(card, name).get("mention")
    return bool(value)
