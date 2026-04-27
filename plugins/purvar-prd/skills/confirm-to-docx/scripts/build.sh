#!/usr/bin/env bash
# Convert a 需求确认单 markdown to docx using the shipped reference template.
#
#   bash build.sh <src.md> [out.docx] [-- <postprocess flags>]
#
# Anything after `--` is forwarded to postprocess.py — that's how you pre-fill
# the cover. Run `python3 postprocess.py --help` for the full flag list.
#
# Examples:
#   bash build.sh req.md req.docx
#   bash build.sh req.md req.docx -- --project-name "BP 智能评估系统" \
#       --version V1.0 --date 2026-04-27 --req-type initial --changelog 初稿
#
# Pre-conditions: pandoc + python-docx installed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/reference-zhcn.docx"

SRC="${1:?usage: build.sh <src.md> [out.docx] [-- <postprocess flags>]}"
shift
OUT=""
if [[ $# -gt 0 && "$1" != "--" ]]; then
  OUT="$1"
  shift
fi
OUT="${OUT:-${SRC%.md}.docx}"
# Drop the optional `--` separator; the rest are passthrough flags.
if [[ $# -gt 0 && "$1" == "--" ]]; then
  shift
fi
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

echo "[build.sh] postprocess $OUT $*"
python3 "$SCRIPT_DIR/postprocess.py" "$OUT" "$@"

echo "[build.sh] done -> $OUT"
