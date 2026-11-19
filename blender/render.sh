#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_MP4="${1:-$SCRIPT_DIR/shadows_out.mp4}"
SAMPLES="${SAMPLES:-32}"

echo "1/2 Rendering 175 looping frames with Blender..."
blender --background --python "$SCRIPT_DIR/build_shadows.py" -- --render --samples "$SAMPLES"

echo "2/2 Encoding web-ready MP4 with FFmpeg -> $OUT_MP4"
ffmpeg -y -framerate 25 -i "$SCRIPT_DIR/frames/frame_%04d.png" \
  -c:v libx264 -crf 26 -pix_fmt yuv420p -movflags +faststart -an \
  "$OUT_MP4"

echo "Done: $OUT_MP4"
