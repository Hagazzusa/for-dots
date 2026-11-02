#!/usr/bin/env bash
set -euo pipefail
base="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
mkdir -p "$base/work/"{tmp,data,config,cache}
export TMPDIR="$base/work/tmp"
export XDG_DATA_HOME="$base/work/data"
export XDG_CONFIG_HOME="$base/work/config"
export XDG_CACHE_HOME="$base/work/cache"
# Import only this isolated project. No Blender subprocess is needed.
godot --headless --path "$base" --editor --import \
  --rendering-method gl_compatibility --audio-driver Dummy
# --capture-matrix replaces qa/*.png and qa/native_matrix.json. Use a copy!
exec godot --path "$base" --rendering-method gl_compatibility \
  --rendering-driver opengl3 --audio-driver Dummy --resolution 720x640 -- "$@"
