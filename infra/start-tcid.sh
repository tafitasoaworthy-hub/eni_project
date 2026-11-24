#!/usr/bin/env bash
# Backward-compatible alias: this workspace now manages ENI, not TCiD.
exec "$(dirname "$0")/start-eni.sh" "$@"