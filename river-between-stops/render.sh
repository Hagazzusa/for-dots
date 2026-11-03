#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v inkscape >/dev/null || { echo 'Inkscape is required.' >&2; exit 1; }
inkscape river_between_stops.svg --export-type=png --export-filename=river_between_stops.png --export-width=3200
