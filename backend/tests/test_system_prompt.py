from backend.agent.system_prompt import load_system_prompt


def test_system_prompt_rewritten() -> None:
    text = load_system_prompt()
    assert "Action space" in text
    assert "Когда остановиться" in text
    assert "Недоверенный ввод" in text
    assert "create_ticket" not in text
