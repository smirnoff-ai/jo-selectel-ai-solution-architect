from typing import Any

from backend.agent.schemas.patch_facts import (
    IdentityFactPatch,
    NarrativeFactPatch,
    PatchFactsInput,
)


def merge_patch(card: dict[str, Any], patch: PatchFactsInput) -> list[str]:
    updated: list[str] = []
    for name in ("customer", "site", "asset", "history"):
        part: IdentityFactPatch | None = getattr(patch, name)
        if part is None:
            continue
        _merge_identity(card["facts"][name], part)
        updated.append(f"facts.{name}")
    for name in ("problem", "symptoms", "desired_deadline", "backup"):
        part_n: NarrativeFactPatch | None = getattr(patch, name)
        if part_n is None:
            continue
        _merge_narrative(card["facts"][name], part_n)
        updated.append(f"facts.{name}")
    return updated


def _merge_identity(slot: dict[str, Any], part: IdentityFactPatch) -> None:
    if part.mention is not None:
        slot["mention"] = part.mention
        if slot["binding"]["status"] == "empty":
            slot["binding"]["status"] = "mentioned"
    slot["evidences"].extend(item.model_dump() for item in part.evidences)


def _merge_narrative(slot: dict[str, Any], part: NarrativeFactPatch) -> None:
    if part.value is not None:
        slot["value"] = part.value
    slot["evidences"].extend(item.model_dump() for item in part.evidences)
