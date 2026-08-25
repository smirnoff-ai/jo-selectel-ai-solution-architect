from copy import deepcopy
from typing import Any

from backend.agent.schemas.update_card import (
    BindingPatch,
    ContractPatch,
    DecisionPatch,
    IdentityFactPatch,
    NarrativeFactPatch,
    UpdateCardInput,
)


class MergeRejectedError(ValueError):
    """Агент передал идентификатор, которого не было в ответах поиска."""


def merge_update(
    card: dict[str, Any],
    patch: UpdateCardInput,
    *,
    seen_ids: set[str],
    last_calculation: dict[str, Any] | None,
) -> list[str]:
    updated: list[str] = []
    for name in ("customer", "site", "asset", "history"):
        part: IdentityFactPatch | None = getattr(patch, name)
        if part is None:
            continue
        _merge_identity(card["facts"][name], part, seen_ids)
        updated.append(f"facts.{name}")
    for name in ("problem", "symptoms", "desired_deadline", "backup"):
        part_n: NarrativeFactPatch | None = getattr(patch, name)
        if part_n is None:
            continue
        _merge_narrative(card["facts"][name], part_n)
        updated.append(f"facts.{name}")
    if patch.contract is not None:
        _merge_contract(card, patch.contract, seen_ids)
        updated.append("contract")
    if patch.calculation is not None:
        if last_calculation is None:
            msg = "сначала вызови calculate"
            raise MergeRejectedError(msg)
        card["calculation"] = deepcopy(last_calculation)
        updated.append("calculation")
    if patch.decision is not None:
        _merge_decision(card, patch.decision)
        updated.append("decision")
    return updated


def _merge_identity(
    slot: dict[str, Any],
    part: IdentityFactPatch,
    seen_ids: set[str],
) -> None:
    if part.mention is not None:
        slot["mention"] = part.mention
        if slot["binding"]["status"] == "empty" and part.binding is None:
            slot["binding"]["status"] = "mentioned"
    if part.binding is not None:
        _apply_binding(slot, part.binding, seen_ids)
        if slot.get("mention") and slot["binding"]["status"] == "empty":
            slot["binding"]["status"] = "mentioned"
    slot["evidences"].extend(item.model_dump() for item in part.evidences)


def _apply_binding(slot: dict[str, Any], binding: BindingPatch, seen_ids: set[str]) -> None:
    if binding.status == "resolved":
        if not binding.id:
            msg = "resolved требует id из ответа поиска"
            raise MergeRejectedError(msg)
        _require_seen(binding.id, seen_ids)
    for candidate in binding.candidates:
        _require_seen(candidate.id, seen_ids)
    slot["binding"] = {
        "status": binding.status,
        "id": binding.id,
        "label": binding.label,
        "candidates": [item.model_dump() for item in binding.candidates],
    }


def _merge_narrative(slot: dict[str, Any], part: NarrativeFactPatch) -> None:
    if part.value is not None:
        slot["value"] = part.value
    slot["evidences"].extend(item.model_dump() for item in part.evidences)


def _merge_contract(card: dict[str, Any], part: ContractPatch, seen_ids: set[str]) -> None:
    if part.status == "resolved":
        if not part.id:
            msg = "договор resolved требует id из get_contract"
            raise MergeRejectedError(msg)
        _require_seen(part.id, seen_ids)
    card["contract"] = {
        "status": part.status,
        "id": part.id,
        "site_id": part.site_id,
        "plan": part.plan,
        "response_sla": part.response_sla,
        "service_window": part.service_window,
        "coverage": list(part.coverage),
    }


def _merge_decision(card: dict[str, Any], part: DecisionPatch) -> None:
    decision = card.setdefault("decision", {})
    dumped = part.model_dump(exclude_none=True)
    decision.update(dumped)


def _require_seen(ident: str, seen_ids: set[str]) -> None:
    if ident not in seen_ids:
        msg = f"идентификатор {ident} не встречался в ответах поиска этого прогона"
        raise MergeRejectedError(msg)
