from pathlib import Path

_MARKER = "<!-- agent -->"


def load_system_prompt() -> str:
    path = Path(__file__).resolve().parents[4] / "docs/requirements/severholod/prompts/system.md"
    text = path.read_text(encoding="utf-8")
    if _MARKER in text:
        return text.split(_MARKER, 1)[1].strip()
    return text.strip()
