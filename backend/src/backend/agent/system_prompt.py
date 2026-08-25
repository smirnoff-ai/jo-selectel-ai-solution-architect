from pathlib import Path

_MARKER = "<!-- agent -->"
_RELATIVE = "docs/requirements/severholod/prompts/system.md"


def _prompt_path() -> Path:
    candidates = (
        Path(__file__).resolve().parents[4] / _RELATIVE,
        Path("/") / _RELATIVE,
    )
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(_RELATIVE)


def load_system_prompt() -> str:
    path = _prompt_path()
    text = path.read_text(encoding="utf-8")
    if _MARKER in text:
        return text.split(_MARKER, 1)[1].strip()
    return text.strip()
