#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v inkscape >/dev/null || { echo 'Inkscape is required.' >&2; exit 1; }
inkscape after_the_turn.svg --export-type=png --export-filename=after_the_turn.png --export-width=3200
