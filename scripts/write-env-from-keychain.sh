#!/usr/bin/env bash
set -euo pipefail

kc() {
  security find-generic-password -a "${USER}" -s "$1" -w 2>/dev/null || true
}

ensure() {
  local name="$1"
  local value
  value="$(kc "$name")"
  if [[ -z "${value}" ]]; then
    value="$2"
    security add-generic-password -a "${USER}" -s "$name" -w "${value}" -U
  fi
  printf '%s' "${value}"
}

openai_key="$(kc OPENROUTER_API_KEY)"
if [[ -z "${openai_key}" ]]; then
  echo "В Keychain нет OPENROUTER_API_KEY" >&2
  exit 1
fi

session="$(ensure REFLEX_SESSION_SECRET "$(python3 -c 'import secrets; print(secrets.token_hex(32))')")"
password="$(ensure REFLEX_DISPATCHER_PASSWORD secret)"
lf_pub="$(ensure LANGFUSE_PUBLIC_KEY pk-lf-local)"
lf_sec="$(ensure LANGFUSE_SECRET_KEY sk-lf-local)"

root="$(cd "$(dirname "$0")/.." && pwd)"
db_host="postgres"
mock_url="http://mock-severholod:8080"
lf_host="http://langfuse:3000"
if [[ "${1:-}" == "local" ]]; then
  db_host="127.0.0.1"
  mock_url="http://127.0.0.1:8080"
  lf_host="http://127.0.0.1:3001"
fi

cat > "${root}/.env" <<EOF
OPENAI_API_KEY=${openai_key}
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=qwen/qwen3.6-35b-a3b
LANGFUSE_PUBLIC_KEY=${lf_pub}
LANGFUSE_SECRET_KEY=${lf_sec}
LANGFUSE_HOST=${lf_host}
DATABASE_URL=postgresql+asyncpg://reflex:reflex@${db_host}:5432/reflex
SESSION_SECRET=${session}
DISPATCHER_LOGIN=dispatcher
DISPATCHER_PASSWORD=${password}
MOCK_SEVERHOLOD_URL=${mock_url}
EOF

echo "Wrote ${root}/.env from Keychain"
