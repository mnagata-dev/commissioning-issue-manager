#!/usr/bin/env bash

set -e

# Detect the current Windows/WSL gateway address.
WSL_GATEWAY=$(ip route show default | awk '{print $3}')

export CIM_SESSION_SECRET="local-development-secret"
export CIM_OLLAMA_HOST="http://${WSL_GATEWAY}:11434"
export CIM_OLLAMA_MODEL="qwen3:4b-instruct"
export CIM_OLLAMA_TIMEOUT_SECONDS="60"

echo "Starting CIM development server..."
echo "CIM_OLLAMA_HOST=${CIM_OLLAMA_HOST}"
echo "CIM_OLLAMA_MODEL=${CIM_OLLAMA_MODEL}"

cd "$(dirname "$0")/../backend"

exec uv run uvicorn app.main:app --reload
