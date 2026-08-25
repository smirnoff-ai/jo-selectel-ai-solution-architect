OUTCOME_STATUS = {
    "create": "done",
    "update": "done",
    "clarify": "clarify",
    "dispatch": "dispatch",
    "approve": "approve",
    "refuse_auto": "dispatch",
}


def desk_status(outcome: str) -> str:
    return OUTCOME_STATUS.get(outcome, "dispatch")
