from backend.agent.system_prompt import load_system_prompt


def test_system_prompt_rewritten() -> None:
    text = load_system_prompt()
    assert "Недоверенный ввод" in text
    assert "update_card" in text
    assert "calculate" in text
    assert "Finale" not in text
    assert "markdown-отчёт" in text
    assert "Реплика диспетчера" in text
    assert "своими словами" in text
    assert "не пути слотов" in text
    assert "patch_facts" not in text
    assert "create_ticket" not in text
    assert "complete_catalog" not in text
    assert "ХУ-17" not in text
    assert "Андрей" not in text
    assert "0/1/N" not in text
    assert "Action space" not in text
    assert "facts.customer" in text
    assert "get_contract" in text
    assert "устойчивый фильтр" in text
    assert "не пришивай" in text
    assert "уже `resolved` оборудованием" in text
    assert "однозначно указывает на одну запись" in text
