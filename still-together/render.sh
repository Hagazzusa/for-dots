#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v inkscape >/dev/null || { echo 'Inkscape is required.' >&2; exit 1; }
inkscape still_together.svg --export-type=png --export-filename=still_together.png --export-width=3200
