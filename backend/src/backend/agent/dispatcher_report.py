from datetime import datetime
from typing import Any

from backend.agent.card_slots import slot

OUTCOME_TITLE = {
    "create": "Создать заявку",
    "update": "Обновить заявку",
    "clarify": "Нужно уточнение",
    "dispatch": "Передать диспетчеру",
    "approve": "На согласовании",
    "refuse_auto": "Автоматика заявку не пишет",
}

OUTCOME_NEXT = {
    "create": (
        "Код пробует сухой прогон создания заявки. Проверьте черновик и результат примерки слева."
    ),
    "update": (
        "Код пробует сухой прогон обновления найденной заявки. "
        "Проверьте черновик и результат примерки слева."
    ),
    "clarify": "Ответьте на вопросы ниже — после ответа можно продолжить разбор.",
    "dispatch": "Возьмите обращение в работу вручную: автоматика здесь не закрывает исход.",
    "approve": "Нужно ваше решение: пускать в заявку или нет.",
    "refuse_auto": "Заявку автоматически не пишем. Решите, что ответить клиенту.",
}

BINDING_LABEL = {
    "mentioned": "упомянуто",
    "resolved": "опознано",
    "not_found": "не найдено",
    "ambiguous": "несколько",
}

SLOT_LABEL = {
    "customer": "Клиент",
    "site": "Объект",
    "asset": "Оборудование",
    "history": "Открытая заявка",
}

VALUE_SLOT_LABEL = {
    "problem": "Проблема",
    "symptoms": "Симптомы",
    "desired_deadline": "Желаемый срок клиента",
    "backup": "Резерв",
}

TOOL_LABEL = {
    "search_sites": "поиск площадок",
    "search_assets": "поиск оборудования",
    "search_tickets": "поиск открытых заявок",
    "get_contract": "чтение договора",
    "calculate": "расчёт срока и приоритета",
    "update_card": "запись в карточку",
    "patch_facts": "запись в карточку",
}

PRIORITY_LABEL = {
    "low": "низкий",
    "medium": "средний",
    "high": "высокий",
    "critical": "критический",
}

SLA_LABEL = {
    "60_minutes": "60 минут",
    "4_business_hours": "4 рабочих часа",
    "next_business_day": "следующий рабочий день",
}

CALC_STATUS = {
    "computed": "посчитан",
    "conditional": "условный",
    "blocked": "не хватает данных",
}


def attach_report_if_missing(
    card: dict[str, Any],
    items: list[dict[str, Any]],
    *,
    tool_names: list[str],
    message_id: int,
    created_at: str,
) -> list[dict[str, Any]]:
    if any(_item_is_report(item) for item in items):
        return items
    if not _as_dict(card.get("decision")).get("outcome"):
        return items
    report = {
        "id": message_id,
        "author": "agent",
        "kind": "message",
        "body": {"text": build_dispatcher_report(card, tool_names=tool_names)},
        "created_at": created_at,
    }
    return [*items, report]


def _item_is_report(item: dict[str, Any]) -> bool:
    if item.get("author") != "agent" or item.get("kind") != "message":
        return False
    return bool(_text(_as_dict(item.get("body")).get("text")))


def persist_has_message_final(persist: object) -> bool:
    if not isinstance(persist, list):
        return False
    return any(
        isinstance(event, dict)
        and event.get("type") == "message_final"
        and str(event.get("text") or "").strip()
        for event in persist
    )


def tool_names_from_persist(persist: object) -> list[str]:
    if not isinstance(persist, list):
        return []
    names: list[str] = []
    for event in persist:
        if not isinstance(event, dict) or event.get("type") != "tool_result":
            continue
        name = event.get("name")
        if isinstance(name, str) and name:
            names.append(name)
    return names


def build_dispatcher_report(card: dict[str, Any], *, tool_names: list[str] | None = None) -> str:
    decision = _as_dict(card.get("decision"))
    outcome = str(decision.get("outcome") or "dispatch")
    title = OUTCOME_TITLE.get(outcome, outcome)
    parts = [f"## {title}", ""]
    reason = _text(decision.get("reason"))
    if reason:
        parts.extend([reason, ""])
    done = _work_done(tool_names or [])
    if done:
        parts.extend(["### Что сделано", "", done, ""])
    found = _found_lines(card)
    if found:
        parts.extend(["### Что опознано", "", found, ""])
    questions = _item_texts(decision.get("questions"))
    if questions:
        numbered = [f"{index}. {text}" for index, text in enumerate(questions, start=1)]
        parts.extend(["### Что нужно от вас", "", *numbered, ""])
    elif outcome in OUTCOME_NEXT:
        parts.extend(["### Что дальше", "", OUTCOME_NEXT[outcome], ""])
    warnings = _warning_texts(decision.get("warnings"))
    if warnings:
        parts.extend(["### Предупреждения", "", *[f"- {text}" for text in warnings], ""])
    reply = _text(decision.get("reply_draft"))
    if reply:
        parts.extend(["### Черновик ответа клиенту", "", reply, ""])
    dry = _dry_run_line(decision)
    if dry:
        parts.extend(["### Примерка заявки", "", dry, ""])
    return "\n".join(parts).strip() + "\n"


def _work_done(tool_names: list[str]) -> str:
    labels: list[str] = []
    for name in tool_names:
        label = TOOL_LABEL.get(name, name)
        if label not in labels:
            labels.append(label)
    return "\n".join(f"- {label}" for label in labels)


def _found_lines(card: dict[str, Any]) -> str:
    lines: list[str] = []
    for name in ("customer", "site", "asset", "history"):
        line = _binding_line(card, name)
        if line:
            lines.append(line)
    facts = _as_dict(card.get("facts"))
    for name, label in VALUE_SLOT_LABEL.items():
        value = _text(_as_dict(facts.get(name)).get("value"))
        if value:
            lines.append(f"- **{label}:** {value}")
    contract_line = _contract_line(_as_dict(card.get("contract")))
    if contract_line:
        lines.append(contract_line)
    calc_line = _calculation_line(_as_dict(card.get("calculation")))
    if calc_line:
        lines.append(calc_line)
    return "\n".join(lines)


def _binding_line(card: dict[str, Any], name: str) -> str | None:
    try:
        row = slot(card, name)
    except (KeyError, TypeError):
        return None
    binding = _as_dict(row.get("binding"))
    status = str(binding.get("status") or "empty")
    mention = _text(row.get("mention"))
    if status == "empty" and not mention:
        return None
    label = SLOT_LABEL[name]
    body = BINDING_LABEL.get(status, status)
    if status == "resolved":
        body = _resolved(binding)
    elif status == "ambiguous":
        body = f"несколько — {_candidates(binding)}"
    elif status == "not_found":
        body = f"не найдено (в письме: {mention})" if mention else "не найдено"
    elif mention:
        body = f"упомянуто — {mention}"
    return f"- **{label}:** {body}"


def _resolved(binding: dict[str, Any]) -> str:
    name = _text(binding.get("label")) or "запись"
    ident = _text(binding.get("id"))
    return f"{name} (`{ident}`)" if ident else name


def _candidates(binding: dict[str, Any]) -> str:
    raw = binding.get("candidates")
    if not isinstance(raw, list) or not raw:
        return "несколько совпадений"
    labels: list[str] = []
    for item in raw:
        row = _as_dict(item)
        labels.append(_text(row.get("label")) or _text(row.get("id")) or "запись")
    return " / ".join(labels)


def _contract_line(contract: dict[str, Any]) -> str | None:
    status = str(contract.get("status") or "empty")
    if status == "empty":
        return None
    if status == "not_found":
        return "- **Договор:** на площадку нет"
    ident = _text(contract.get("id"))
    plan = _text(contract.get("plan"))
    sla_code = str(contract.get("response_sla") or "")
    sla = SLA_LABEL.get(sla_code, _text(contract.get("response_sla")))
    bits = [part for part in (ident, plan, sla) if part]
    return f"- **Договор:** {', '.join(bits)}" if bits else "- **Договор:** есть"


def _calculation_line(calculation: dict[str, Any]) -> str | None:
    status = str(calculation.get("status") or "")
    if status in {"", "none"}:
        return None
    bits: list[str] = []
    status_label = CALC_STATUS.get(status)
    if status_label:
        bits.append(status_label)
    priority = _as_dict(calculation.get("priority")).get("value")
    if priority:
        bits.append(f"приоритет {PRIORITY_LABEL.get(str(priority), priority)}")
    sla = _as_dict(calculation.get("sla")).get("code")
    if sla:
        bits.append(f"срок {SLA_LABEL.get(str(sla), sla)}")
    deadline = _when(_as_dict(calculation.get("deadline")).get("at"))
    if deadline:
        bits.append(f"до {deadline}")
    return f"- **Расчёт:** {', '.join(bits)}" if bits else None


def _dry_run_line(decision: dict[str, Any]) -> str | None:
    dry = _as_dict(decision.get("itsm_dry_run"))
    if not dry:
        return None
    accepted = dry.get("accepted")
    ticket = _text(dry.get("would_ticket_id")) or _text(dry.get("ticket_id")) or "без номера"
    if accepted is True:
        return f"Сухой прогон принят, номер заявки {ticket}."
    if accepted is False:
        return "Сухой прогон отклонён. Смотрите детали слева."
    return f"Сухой прогон: {ticket}."


def _item_texts(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    texts: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            texts.append(item.strip())
            continue
        text = _text(_as_dict(item).get("text"))
        if text:
            texts.append(text)
    return texts


def _warning_texts(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    texts: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            texts.append(item.strip())
            continue
        row = _as_dict(item)
        text = _text(row.get("text"))
        code = _text(row.get("code"))
        if text and code:
            texts.append(f"{code}: {text}")
        elif text:
            texts.append(text)
        elif code:
            texts.append(code)
    return texts


def _when(raw: object) -> str | None:
    text = _text(raw)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return text


def _text(raw: object) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _as_dict(raw: object) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}
