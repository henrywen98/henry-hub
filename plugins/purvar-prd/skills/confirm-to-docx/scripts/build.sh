#!/usr/bin/env bash
# Convert a 需求确认单 markdown to docx using the shipped reference template.
#
#   bash build.sh <src.md> [out.docx]
#
# Defaults:  out.docx = same dir + same stem + .docx
#
# Pre-conditions: pandoc + python-docx installed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/reference-zhcn.docx"

SRC="${1:?usage: build.sh <src.md> [out.docx]}"
OUT="${2:-${SRC%.md}.docx}"
SRC_DIR="$(cd "$(dirname "$SRC")" && pwd)"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "[build.sh] template missing, generating: $TEMPLATE"
  python3 "$SCRIPT_DIR/build_reference.py"
fi

echo "[build.sh] pandoc $SRC -> $OUT"
pandoc "$SRC" \
  -o "$OUT" \
  --reference-doc="$TEMPLATE" \
  --resource-path="$SRC_DIR" \
  --from gfm

echo "[build.sh] postprocess $OUT"
python3 "$SCRIPT_DIR/postprocess.py" "$OUT"

echo "[build.sh] done -> $OUT"
