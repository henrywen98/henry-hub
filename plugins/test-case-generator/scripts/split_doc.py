#!/usr/bin/env python3
"""Split a markdown document into per-module-group files based on analysis.json.

Usage: python split_doc.py <analysis.json> <document.md> <output_dir>

Outputs:
  output_dir/doc_common.md   — content before the first module group
  output_dir/doc_grp_N.md    — common prefix + module N content
"""
import json
import os
import re
import sys


def split_document(analysis_path, doc_path, output_dir):
    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    with open(doc_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    groups = analysis["module_groups"]

    # Find the line index where each group's heading starts
    boundaries = []
    for grp in groups:
        pattern = re.escape(grp["heading_pattern"])
        found = False
        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()):
                boundaries.append(i)
                found = True
                break
        if not found:
            # Fallback: search for the heading text without exact prefix match
            heading_text = grp["heading_pattern"].lstrip("# ").strip()
            for i, line in enumerate(lines):
                if heading_text in line:
                    boundaries.append(i)
                    found = True
                    break
        if not found:
            raise ValueError(f"Cannot find heading pattern '{grp['heading_pattern']}' in document")

    # Common section: everything before the first group
    common_end = boundaries[0] if boundaries else len(lines)
    common_lines = lines[:common_end]
    common_text = "".join(common_lines).rstrip() + "\n"

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
        print(f"Usage: {sys.argv[0]} <analysis.json> <document.md> <output_dir>")
        sys.exit(1)
    split_document(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Split complete. Files written to {sys.argv[3]}")
