from copy import deepcopy
from datetime import datetime
from typing import Any

_EMPTY_BINDING = {"status": "empty", "id": None, "label": None, "candidates": []}
_EMPTY_METRIC = {"value": None, "formula": None, "arguments": {}, "missing": []}


def empty_card(
    *,
    channel: str,
    sender: str | None,
    received_at: datetime,
    text: str,
    attachment_text: str | None,
) -> dict[str, Any]:
    return deepcopy(
        {
            "schema_version": 1,
            "intake": {
                "channel": channel,
                "sender": sender,
                "received_at": received_at.isoformat(),
                "text": text,
                "attachment_text": attachment_text,
            },
            "facts": {
                "customer": {"mention": None, "binding": dict(_EMPTY_BINDING), "evidences": []},
                "site": {"mention": None, "binding": dict(_EMPTY_BINDING), "evidences": []},
                "asset": {"mention": None, "binding": dict(_EMPTY_BINDING), "evidences": []},
                "problem": {"value": None, "evidences": []},
                "symptoms": {"value": None, "evidences": []},
                "desired_deadline": {"value": None, "parsed_at": None, "evidences": []},
                "backup": {"value": None, "evidences": []},
                "history": {"mention": None, "binding": dict(_EMPTY_BINDING), "evidences": []},
            },
            "contract": {
                "status": "empty",
                "id": None,
                "site_id": None,
                "plan": None,
                "response_sla": None,
                "service_window": None,
                "coverage": [],
            },
            "calculation": {
                "branch": "none",
                "status": "blocked",
                "priority": dict(_EMPTY_METRIC),
                "sla": {"code": None, "formula": None, "arguments": {}, "missing": []},
                "deadline": {
                    "at": None,
                    "timezone": None,
                    "formula": None,
                    "arguments": {},
                    "missing": [],
                },
            },
            "decision": {
                "outcome": None,
                "reason": None,
                "grounds": [],
                "ticket_draft": None,
                "itsm_dry_run": None,
                "auto_in_prod": None,
                "questions": [],
                "warnings": [],
                "reply_draft": None,
            },
        }
    )
