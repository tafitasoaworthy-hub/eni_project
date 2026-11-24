#!/usr/bin/env bash
# Start ENI on GKE without recreating persistent data.
# Usage: ./infra/start-eni.sh [DRY_RUN=1]
set -euo pipefail

PROJECT_ID=${PROJECT_ID:-eni-universite-b9124bd9}
REGION=${REGION:-africa-south1}
CLUSTER=${CLUSTER:-eni}
NAMESPACE=${NAMESPACE:-eni}
SITE=${SITE:-https://eni-fianarantsoa.com}
WAIT=${WAIT:-600}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
CONTEXT="gke_${PROJECT_ID}_${REGION}_${CLUSTER}"
DRY=()
[[ ${DRY_RUN:-0} == 1 ]] && DRY+=(--dry-run=server)

command -v gcloud >/dev/null || { echo 'gcloud is required.' >&2; exit 1; }
command -v kubectl >/dev/null || { echo 'kubectl is required.' >&2; exit 1; }
gcloud container clusters get-credentials "$CLUSTER" --region "$REGION" --project "$PROJECT_ID"
kubectl --context "$CONTEXT" cluster-info >/dev/null
k() { kubectl --context "$CONTEXT" --namespace "$NAMESPACE" "$@"; }
step() { printf '\n==> %s\n' "$*"; }

step 'Restore the public ingress, certificate, and HTTPS redirect'
k apply -f "$ROOT/infra/gke/public.yaml" "${DRY[@]}"

step 'Start PostgreSQL; keep its persistent volume'
k scale statefulset/postgres --replicas=1 "${DRY[@]}"
if [[ ${#DRY[@]} -eq 0 ]]; then k rollout status statefulset/postgres --timeout="${WAIT}s"; fi

step 'Start the backend'
k scale deployment/backend --replicas=1 "${DRY[@]}"
if [[ ${#DRY[@]} -eq 0 ]]; then k rollout status deployment/backend --timeout="${WAIT}s"; fi

step 'Start the frontend'
k scale deployment/frontend --replicas=1 "${DRY[@]}"
if [[ ${#DRY[@]} -eq 0 ]]; then k rollout status deployment/frontend --timeout="${WAIT}s"; fi

if [[ ${#DRY[@]} -gt 0 ]]; then
  echo 'Dry run complete; no resources were changed.'
  exit 0
fi

step "Check the public site at $SITE"
deadline=$((SECONDS + WAIT))
code=000
while (( SECONDS < deadline )); do
  code=$(curl -k -sS -o /dev/null --connect-timeout 5 --max-time 15 -w '%{http_code}' "$SITE" || true)
  [[ $code == 200 ]] && break
  sleep 10
done
if [[ $code != 200 ]]; then
  echo "Workloads are running, but $SITE did not return HTTP 200 (last status: $code)." >&2
  exit 1
fi
k get statefulset,deployment,pods,ingress
echo "ENI is running: $SITE"
