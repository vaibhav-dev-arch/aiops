#!/usr/bin/env bash
# Shared deploy helpers (stub for local MVP).
set -euo pipefail

echo "[deploy] stage=${STAGE:-dev}"
echo "[deploy] Would build images, push to ACR, publish prompts, deploy to AKS."
