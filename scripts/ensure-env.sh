#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "${root}"
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example" >&2
fi
if ! grep -qE '^OPENAI_API_KEY=.+' .env; then
  echo "В .env пустой OPENAI_API_KEY. Нужен ключ OpenRouter (в письме рекрутеру — тестовый на 1 USD)." >&2
  exit 1
fi
