from backend.agent.desk_status import desk_status


def test_desk_status_maps_known_outcomes() -> None:
    assert desk_status("create") == "done"
    assert desk_status("update") == "done"
    assert desk_status("clarify") == "clarify"
    assert desk_status("dispatch") == "dispatch"
    assert desk_status("approve") == "approve"
    assert desk_status("refuse_auto") == "dispatch"


def test_desk_status_unknown_is_dispatch() -> None:
    assert desk_status("") == "dispatch"
    assert desk_status("unknown") == "dispatch"
