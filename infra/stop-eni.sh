#!/usr/bin/env bash
# Stop ENI while retaining database/media disks, secrets, and reserved IP.
# Usage: ./infra/stop-eni.sh [--deep] [DRY_RUN=1]
set -euo pipefail

PROJECT_ID=${PROJECT_ID:-eni-universite-b9124bd9}
REGION=${REGION:-africa-south1}
CLUSTER=${CLUSTER:-eni}
NAMESPACE=${NAMESPACE:-eni}
WAIT=${WAIT:-300}
DEEP=0
for arg in "$@"; do
  case "$arg" in
    --deep) DEEP=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done
CONTEXT="gke_${PROJECT_ID}_${REGION}_${CLUSTER}"
DRY=()
[[ ${DRY_RUN:-0} == 1 ]] && DRY+=(--dry-run=server)

command -v gcloud >/dev/null || { echo 'gcloud is required.' >&2; exit 1; }
command -v kubectl >/dev/null || { echo 'kubectl is required.' >&2; exit 1; }
gcloud container clusters get-credentials "$CLUSTER" --region "$REGION" --project "$PROJECT_ID"
kubectl --context "$CONTEXT" cluster-info >/dev/null
k() { kubectl --context "$CONTEXT" --namespace "$NAMESPACE" "$@"; }
step() { printf '\n==> %s\n' "$*"; }

step 'Stop the frontend first'
k scale deployment/frontend --replicas=0 "${DRY[@]}"
if [[ ${#DRY[@]} -eq 0 ]]; then k wait --for=delete pod -l app=frontend --timeout="${WAIT}s" || true; fi

step 'Stop the backend'
k scale deployment/backend --replicas=0 "${DRY[@]}"
if [[ ${#DRY[@]} -eq 0 ]]; then k wait --for=delete pod -l app=backend --timeout="${WAIT}s" || true; fi

step 'Stop PostgreSQL last; its persistent volume is retained'
k scale statefulset/postgres --replicas=0 "${DRY[@]}"
if [[ ${#DRY[@]} -eq 0 ]]; then k wait --for=delete pod/postgres-0 --timeout="${WAIT}s" || true; fi

if [[ $DEEP == 1 ]]; then
  step 'Release the public load balancer; keep its reserved IP and certificate'
  k delete ingress eni-web --ignore-not-found=true --wait=false "${DRY[@]}"
fi

if [[ ${#DRY[@]} -gt 0 ]]; then
  echo 'Dry run complete; no resources were changed.'
  exit 0
fi
k get statefulset,deployment,pods,ingress
echo 'ENI is stopped. Persistent database/media volumes, secrets, and the reserved IP are retained.'
