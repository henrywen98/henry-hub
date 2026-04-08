#!/usr/bin/env python3
"""Split a markdown document into per-module-group files based on analysis.json.

Usage: python split_doc.py <analysis.json> <document.md> <output_dir>

Outputs:
  output_dir/doc_common.md   — content before the first module group
  output_dir/doc_grp_N.md    — common prefix + module N content

Matching semantics:
- Normalizes BOM, CR, non-breaking space (\\xa0), full-width space (\\u3000),
  and collapses consecutive spaces on both sides before comparing
- Does a literal EQUALITY comparison (not substring) to avoid "# 1" matching "# 11"
- On failure, dumps the 5 closest lines via difflib as a diagnostic
- Accepts the legacy field name `heading_pattern` with a deprecation warning
"""
import difflib
import json
import os
import re
import sys


def normalize(s: str) -> str:
    """Normalize whitespace and invisible chars for robust heading comparison.

    Handles:
    - UTF-8 BOM (\\ufeff) from pandoc-converted Word docs
    - CRLF line endings (\\r)
    - Non-breaking space (\\xa0) common in Chinese Word exports
    - Full-width space (\\u3000)
    - Multiple consecutive spaces collapsed to one
    """
    s = s.replace("\ufeff", "")  # BOM
    s = s.replace("\r", "")       # CRLF -> LF residue
    s = s.replace("\xa0", " ")    # non-breaking space
    s = s.replace("\u3000", " ")  # full-width space
    s = re.sub(r" +", " ", s)     # collapse multi-space
    return s.strip()


def get_heading_text(grp: dict) -> str:
    """Read heading_text, with backward-compat for the legacy heading_pattern field."""
    if "heading_text" in grp:
        return grp["heading_text"]
    if "heading_pattern" in grp:
        print(
            f"WARNING: module_group {grp.get('id', '?')} uses deprecated field "
            f"'heading_pattern'; please rename to 'heading_text'. "
            f"Compat will be removed in v3.2.",
            file=sys.stderr,
        )
        return grp["heading_pattern"]
    raise KeyError(
        f"module_group {grp.get('id', '?')} has neither 'heading_text' nor "
        f"'heading_pattern' field"
    )


def find_heading_line(heading_text: str, lines: list) -> int:
    """Return the 0-based line index of the heading. Raise with diagnostic on failure."""
    target = normalize(heading_text)
    normalized_lines = [normalize(l) for l in lines]

    for i, norm_line in enumerate(normalized_lines):
        if norm_line == target:
            return i

    # Failure: dump diagnostic
    close = difflib.get_close_matches(target, normalized_lines, n=5, cutoff=0.4)
    msg_parts = [
        f"Cannot find heading_text: {target!r}",
        "",
        "Top 5 closest lines in document (after normalize):",
    ]
    if close:
        for i, c in enumerate(close, 1):
            msg_parts.append(f"  {i}. {c!r}")
    else:
        msg_parts.append("  (no similar lines found)")
    msg_parts.append("")
    msg_parts.append(
        "Hint: heading_text must match the document literally after whitespace "
        "normalization. Common causes:"
    )
    msg_parts.append("  - Regex chars in heading_text (e.g., '^# 1\\\\s+...'); use literal text only")
    msg_parts.append("  - heading_text too short (e.g., '# 1') collides with '# 10', '# 11'")
    msg_parts.append("  - Heading differs between analysis and document")
    raise ValueError("\n".join(msg_parts))


def split_document(analysis_path: str, doc_path: str, output_dir: str) -> None:
    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    with open(doc_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    groups = analysis["module_groups"]

    # Find the line index for each group's heading
    boundaries = []
    for grp in groups:
        heading_text = get_heading_text(grp)
        idx = find_heading_line(heading_text, lines)
        boundaries.append(idx)

    # Common section: everything before the first group
    common_end = boundaries[0] if boundaries else len(lines)
    common_lines = lines[:common_end]
    common_text = "".join(common_lines).rstrip() + "\n"

    # Ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    # Write doc_common.md
    with open(os.path.join(output_dir, "doc_common.md"), "w", encoding="utf-8") as f:
        f.write(common_text)

    # Write each group file: common + group content
    for idx, grp in enumerate(groups):
        start = boundaries[idx]
        end = boundaries[idx + 1] if idx + 1 < len(boundaries) else len(lines)
        group_lines = lines[start:end]
        group_text = common_text + "\n" + "".join(group_lines).rstrip() + "\n"

        with open(os.path.join(output_dir, f"doc_{grp['id']}.md"), "w", encoding="utf-8") as f:
            f.write(group_text)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <analysis.json> <document.md> <output_dir>", file=sys.stderr)
        sys.exit(1)
    try:
        split_document(sys.argv[1], sys.argv[2], sys.argv[3])
    except (ValueError, KeyError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Split complete. Files written to {sys.argv[3]}")
