#!/usr/bin/env bash
# Usage: tools/run_checks.sh [--fresh-import]
# Fresh import moves the existing .godot cache into external qa_work/cache first.
set -uo pipefail
cd "$(dirname "$0")/.."
engine="${GODOT_BIN:-godot}"
work="${RAIN_QA_ROOT:-$(cd .. && pwd)/qa_work}"
mkdir -p "$work"
work="$(cd "$work" && pwd)"
case "$work/" in "$(pwd)/"*) echo "RAIN_QA_ROOT must be outside the source project"; exit 2;; esac
mkdir -p "$work"/{tmp,data,config,cache,logs}
export TMPDIR="$work/tmp" XDG_DATA_HOME="$work/data" XDG_CONFIG_HOME="$work/config" XDG_CACHE_HOME="$work/cache"
exec 9>"$work/engine.lock"
flock -n 9 || { echo 'Another check/export owns the serial engine slot'; exit 3; }
if [[ $# -gt 1 || ( $# -eq 1 && "$1" != '--fresh-import' ) ]]; then echo "Usage: $0 [--fresh-import]"; exit 2; fi
logs="${RAIN_TEST_LOG_DIR:-$work/logs/checks-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
mkdir -p "$logs"
if [[ "${1:-}" == '--fresh-import' && -d .godot ]]; then
 backup="$(mktemp -d "$work/cache/before-fresh-import.XXXXXX")"
 mv .godot "$backup/.godot"
 echo "Previous import cache preserved: $backup/.godot"
fi
count=0; failed=0
run_check() {
 local label="$1"; shift
 timeout "${RAIN_TEST_TIMEOUT:-120}" "$engine" --headless --path . "$@" >"$logs/$label.log" 2>&1
 local status=$?
 count=$((count+1))
 if [[ $status -ne 0 ]] || grep -Eq 'SCRIPT ERROR|(^|[[:space:]])ERROR:|QA FAIL|(^|[[:space:]])FAIL:|instances leaked|resources still in use' "$logs/$label.log"; then
  echo "FAIL $label (exit $status)"; tail -20 "$logs/$label.log"; failed=$((failed+1)); return 1
 fi
 echo "PASS $label"
}
# Do not run tests against a partially imported project.
run_check import --editor --import || { echo "Import failed. Logs: $logs"; exit 1; }
for script in tests/*.gd; do
 [[ -f "$script" ]] || continue
 if grep -Eq '^[[:space:]]*extends[[:space:]]+SceneTree([[:space:]]|$)' "$script"; then
  run_check "$(basename "$script" .gd)" --script "res://$script" || :
 fi
done
run_check main -- --test || :
printf '%d checks, %d failures. Logs: %s\n' "$count" "$failed" "$logs"
[[ $failed -eq 0 ]]
