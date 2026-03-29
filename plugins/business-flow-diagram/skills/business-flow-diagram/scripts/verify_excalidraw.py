#!/usr/bin/env python3
"""
Verify an .excalidraw file for common issues:
  1. Corrupted characters (encoding)
  2. Wrong font family (must be 2 for CJK)
  3. Technical terms in displayed text
  4. Element overlaps (>30% area)
  5. Bound text overflowing container

Usage: python verify_excalidraw.py <path_to_excalidraw_file>
Exit code 0 = all pass, 1 = issues found
"""
import json
import sys


def verify(filepath):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    els = data["elements"]
    by_id = {e["id"]: e for e in els}
    content = json.dumps(data, ensure_ascii=False)
    errors = []

    # 1. Encoding
    if "\ufffd" in content:
        errors.append("ENCODING: corrupted characters (U+FFFD) found")

    # 2. Font family
    families = set(e.get("fontFamily") for e in els if "fontFamily" in e)
    if families and families != {2}:
        errors.append(f"FONT: expected fontFamily {{2}}, got {families}")

    # 3. Tech terms
    tech_terms = [
        "pick_up(", "warehouse()", "start_shipping", "receive_payment(",
        "mark_documents", "EventBus", "InventoryACL", "DomainEvent",
        "aggregate", "repository", "Handler", "subscribe", "event_type",
        "BusinessException", "fontFamily", "autoResize",
    ]
    # Only check displayed text, not JSON structure keys
    displayed = " ".join(
        e.get("text", "") for e in els if e["type"] == "text"
    )
    found = [t for t in tech_terms if t in displayed]
    if found:
        errors.append(f"TECH_TERMS: {found}")

    # 4. Overlap detection
    skip_bg = {
        e["id"]
        for e in els
        if e.get("opacity", 100) <= 35 and e["type"] == "rectangle"
    }
    visible = [
        e for e in els
        if e["type"] in ("rectangle", "text", "diamond")
        and e["id"] not in skip_bg
        and not e.get("containerId")
        and e.get("width", 0) > 0
    ]
    for i, a in enumerate(visible):
        ax1, ay1 = a["x"], a["y"]
        ax2, ay2 = ax1 + a["width"], ay1 + a["height"]
        for b in visible[i + 1:]:
            bx1, by1 = b["x"], b["y"]
            bx2, by2 = bx1 + b["width"], by1 + b["height"]
            if ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1:
                continue
            ox = min(ax2, bx2) - max(ax1, bx1)
            oy = min(ay2, by2) - max(ay1, by1)
            area = ox * oy
            mi = min(
                (ax2 - ax1) * (ay2 - ay1), (bx2 - bx1) * (by2 - by1)
            )
            if mi > 0 and area / mi > 0.3:
                at = a.get("text", a["id"])[:15]
                bt = b.get("text", b["id"])[:15]
                errors.append(f"OVERLAP: [{at}] vs [{bt}]")

    # 5. Bound text overflow
    for e in els:
        cid = e.get("containerId")
        if cid and e["type"] == "text" and cid in by_id:
            c = by_id[cid]
            if c["type"] != "arrow" and e.get("width", 0) > c.get("width", 0) + 15:
                errors.append(
                    f"OVERFLOW: '{e['text'][:12]}' in '{cid}'"
                )

    # Report
    if errors:
        print(f"FAILED ({len(errors)} issues):")
        for e in errors:
            print(f"  {e}")
        return False
    else:
        print(f"ALL CHECKS PASSED ({len(els)} elements)")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_excalidraw.py <file.excalidraw>")
        sys.exit(1)
    ok = verify(sys.argv[1])
    sys.exit(0 if ok else 1)
