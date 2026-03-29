#!/usr/bin/env python3
"""
Excalidraw File Generator - Business Flow Diagram

Converts a list of diagram element definitions into a valid .excalidraw JSON file.
Handles CJK character width calculation, bound text creation, and required defaults.

Usage:
    from gen_excalidraw import convert_and_save
    elements = [...]  # list of element dicts
    convert_and_save(elements, "output.excalidraw")

Or as CLI:
    python gen_excalidraw.py <output_path>
    (requires RAW list defined in __main__ block or piped via wrapper script)
"""
import json
import random
import sys
import time
import unicodedata

R = random.randint

# fontFamily 2 = Helvetica/sans-serif (supports CJK via system fallback)
# fontFamily 1 = Virgil (hand-drawn, no CJK support)
# fontFamily 3 = Cascadia (code font, poor CJK)
FONT_FAMILY = 2
LINE_HEIGHT = 1.25


def _is_wide(ch):
    """Check if character is full-width (CJK, etc.)"""
    return unicodedata.east_asian_width(ch) in ("W", "F")


def _text_width(text, font_size):
    """Estimate text pixel width (CJK ~1.05x, ASCII ~0.55x per char)"""
    lines = text.split("\n")
    max_w = 0
    for line in lines:
        w = sum(font_size * (1.05 if _is_wide(ch) else 0.55) for ch in line)
        max_w = max(max_w, w)
    return round(max_w + 4, 1)


def _text_height(text, font_size):
    """Estimate text pixel height based on line count"""
    return len(text.split("\n")) * font_size * LINE_HEIGHT


def _defaults(e):
    """Add required Excalidraw element properties with sensible defaults"""
    for k, v in [
        ("angle", 0),
        ("strokeColor", "#1e1e1e"),
        ("backgroundColor", "transparent"),
        ("fillStyle", "solid"),
        ("strokeWidth", 2),
        ("strokeStyle", "solid"),
        ("roughness", 0),
        ("opacity", 100),
        ("groupIds", []),
        ("frameId", None),
        ("seed", R(1, 2**31)),
        ("version", 1),
        ("versionNonce", R(1, 2**31)),
        ("isDeleted", False),
        ("boundElements", None),
        ("updated", int(time.time() * 1000)),
        ("link", None),
        ("locked", False),
    ]:
        e.setdefault(k, v)
    return e


def _text_defaults(e):
    """Add text-specific defaults"""
    fs = e.setdefault("fontSize", 16)
    e.setdefault("fontFamily", FONT_FAMILY)
    e.setdefault("textAlign", "left")
    e.setdefault("verticalAlign", "top")
    e.setdefault("containerId", None)
    e.setdefault("originalText", e.get("text", ""))
    e.setdefault("autoResize", True)
    e.setdefault("lineHeight", LINE_HEIGHT)
    txt = e.get("text", "")
    e.setdefault("width", _text_width(txt, fs))
    e.setdefault("height", _text_height(txt, fs))
    return e


def _arrow_defaults(e):
    """Add arrow-specific defaults"""
    for k in ["startBinding", "endBinding", "startArrowhead", "lastCommittedPoint"]:
        e.setdefault(k, None)
    return e


def _make_bound_text(parent, label):
    """Create a bound text element for a labeled shape/arrow"""
    tid = parent["id"] + "_t"
    fs = label.get("fontSize", 16)
    txt = label["text"]
    tw = _text_width(txt, fs)
    th = _text_height(txt, fs)
    px, py = parent.get("x", 0), parent.get("y", 0)
    pw, ph = parent.get("width", 0), parent.get("height", 0)
    cx = px + (pw - tw) / 2
    cy = py + (ph - th) / 2
    te = {
        "id": tid,
        "type": "text",
        "x": round(cx, 1),
        "y": round(cy, 1),
        "width": round(tw, 1),
        "height": round(th, 1),
        "strokeColor": parent.get("strokeColor", "#1e1e1e"),
        "backgroundColor": "transparent",
        "fontSize": fs,
        "fontFamily": FONT_FAMILY,
        "textAlign": "center",
        "verticalAlign": "middle",
        "containerId": parent["id"],
        "originalText": txt,
        "text": txt,
        "autoResize": True,
        "lineHeight": LINE_HEIGHT,
    }
    _defaults(te)
    te["strokeWidth"] = 0
    if parent.get("boundElements") is None:
        parent["boundElements"] = []
    parent["boundElements"].append({"id": tid, "type": "text"})
    return te


def convert(raw):
    """Convert internal DSL elements to standard Excalidraw format"""
    result = []
    for e in raw:
        if e.get("type") == "cameraUpdate":
            continue
        label = e.pop("label", None)
        _defaults(e)
        if e["type"] == "text":
            _text_defaults(e)
        if e["type"] == "arrow":
            _arrow_defaults(e)
        result.append(e)
        if label and e["type"] in ("rectangle", "ellipse", "diamond", "arrow"):
            result.append(_make_bound_text(e, label))
    return result


def convert_and_save(raw_elements, output_path):
    """Convert elements and save as .excalidraw file"""
    elements = convert(raw_elements)
    output = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
        "files": {},
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    print(f"Saved to {output_path} ({len(elements)} elements)")
    return output_path


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "business_flow.excalidraw"
    try:
        convert_and_save(RAW, output)  # noqa: F821 - RAW defined by wrapper
    except NameError:
        print("Error: RAW elements list not defined.")
        print("Usage: define RAW in this file, or import convert_and_save() from a wrapper.")
        sys.exit(1)
