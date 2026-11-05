#!/usr/bin/env bash
# Rebuild the PNG from the editable SVG with an installed Inkscape.
set -euo pipefail
cd "$(dirname "$0")"
command -v inkscape >/dev/null || { echo 'Inkscape is required.' >&2; exit 1; }
inkscape a_seat_for_wind.svg --export-type=png --export-filename=a_seat_for_wind.png --export-width=3200
