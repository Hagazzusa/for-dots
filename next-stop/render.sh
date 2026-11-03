#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v inkscape >/dev/null || { echo 'Inkscape is required.' >&2; exit 1; }
inkscape next_stop.svg --export-type=png --export-filename=next_stop.png --export-width=3200
