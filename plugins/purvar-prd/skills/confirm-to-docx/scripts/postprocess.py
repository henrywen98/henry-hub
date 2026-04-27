"""Post-process pandoc docx output for the 璞华需求确认单 style.

What it does:

1. Insert a cover page (杭州产投-AI应用 standard layout). Pass --project-name
   /--version/--editor/--date/etc to pre-fill cells; unsupplied fields stay
   blank for the user to fill in Word.
2. Normalize every body table:
   - Apply preset column widths by column count and header signature
   - Center the table, fixed layout, full single-line borders 0.5pt
   - Header row: F2F2F2 grey fill + bold + horizontal center
   - All cells: vertical center; drop first-line indent inside cells

Usage examples:

  python3 postprocess.py out.docx
  python3 postprocess.py out.docx --project-name "BP 智能评估系统" \
      --version V1.0 --date 2026-04-27 --req-type initial --changelog 初稿
"""
import argparse
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Map machine-friendly --req-type values to the four checkbox labels.
REQ_TYPE_LABELS = [
    ("initial", "初始需求"),
    ("new", "新增需求"),
    ("change", "需求变更"),
    ("env", "系统环境变更"),
]

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Total page text width = 11906 - 1800*2 = 8306 twip; presets sum to 8306.
COL_WIDTHS = {
    2: [4153, 4153],                          # generic 2-col equal
    3: [1800, 2200, 4306],                    # label / short / long note
    4: [2076, 2077, 2076, 2077],              # 4-col equal default
    6: [1500, 1361, 1361, 1361, 1361, 1362],  # 维度 + 多业务线
}
COL_WIDTHS_LABEL_NOTE_2 = [2200, 6106]        # 信息项 / 备注
COL_WIDTHS_PROJECT_INFO_4 = [1660, 2493, 2076, 2077]  # cover project-info table


def W(tag: str) -> str:
    return qn(f"w:{tag}")


def make(tag: str, **attrs):
    el = OxmlElement(f"w:{tag}")
    for k, v in attrs.items():
        el.set(qn(f"w:{k}"), str(v))
    return el


def get_or_make(parent, tag, *, before=None):
    el = parent.find(W(tag))
    if el is not None:
        return el
    el = OxmlElement(f"w:{tag}")
    if before:
        anchor = parent.find(W(before))
        if anchor is not None:
            anchor.addprevious(el)
            return el
    parent.append(el)
    return el


# ---------- Table normalization ----------

def set_cell_vAlign(tc, val="center"):
    tcPr = get_or_make(tc, "tcPr")
    for old in tcPr.findall(W("vAlign")):
        tcPr.remove(old)
    tcPr.append(make("vAlign", val=val))


def set_cell_shading(tc, fill_hex):
    tcPr = get_or_make(tc, "tcPr")
    for old in tcPr.findall(W("shd")):
        tcPr.remove(old)
    tcPr.append(make("shd", val="clear", color="auto", fill=fill_hex))


def set_cell_width(tc, w_twip):
    tcPr = get_or_make(tc, "tcPr")
    for old in tcPr.findall(W("tcW")):
        tcPr.remove(old)
    tcPr.append(make("tcW", w=w_twip, type="dxa"))


def set_run_bold(r):
    rPr = get_or_make(r, "rPr", before="t")
    if rPr.find(W("b")) is None:
        rPr.append(OxmlElement("w:b"))
    if rPr.find(W("bCs")) is None:
        rPr.append(OxmlElement("w:bCs"))


def header_text(tbl):
    rows = tbl.findall(W("tr"))
    if not rows:
        return []
    return [
        "".join(t.text or "" for t in c.iter(W("t"))).strip()
        for c in rows[0].findall(W("tc"))
    ]


def normalize_table(tbl):
    headers = header_text(tbl)
    rows = tbl.findall(W("tr"))
    n_cols = max((len(r.findall(W("tc"))) for r in rows), default=0)
    if n_cols == 0:
        return

    if n_cols == 2 and len(headers) == 2 and "备注" in headers[1]:
        widths = COL_WIDTHS_LABEL_NOTE_2
    elif n_cols == 4 and headers and headers[0] == "项目名称":
        widths = COL_WIDTHS_PROJECT_INFO_4
    else:
        widths = COL_WIDTHS.get(n_cols)
        if widths is None or len(widths) != n_cols:
            total = 8306
            base = total // n_cols
            widths = [base] * (n_cols - 1) + [total - base * (n_cols - 1)]

    tblPr = get_or_make(tbl, "tblPr", before="tblGrid")
    for old in tblPr.findall(W("tblW")):
        tblPr.remove(old)
    tblPr.insert(0, make("tblW", w=sum(widths), type="dxa"))
    for old in tblPr.findall(W("jc")):
        tblPr.remove(old)
    tblPr.append(make("jc", val="center"))
    for old in tblPr.findall(W("tblLayout")):
        tblPr.remove(old)
    tblPr.append(make("tblLayout", type="fixed"))
    for old in tblPr.findall(W("tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(make(side, val="single", color="auto", sz=4, space=0))
    tblPr.append(borders)
    for old in tblPr.findall(W("tblCellMar")):
        tblPr.remove(old)
    cm = OxmlElement("w:tblCellMar")
    cm.append(make("top", w=0, type="dxa"))
    cm.append(make("left", w=108, type="dxa"))
    cm.append(make("bottom", w=0, type="dxa"))
    cm.append(make("right", w=108, type="dxa"))
    tblPr.append(cm)

    grid = get_or_make(tbl, "tblGrid")
    for old in grid.findall(W("gridCol")):
        grid.remove(old)
    for w_v in widths:
        grid.append(make("gridCol", w=w_v))

    for ri, tr in enumerate(rows):
        cells = tr.findall(W("tc"))
        for ci, tc in enumerate(cells):
            if ci < len(widths):
                set_cell_width(tc, widths[ci])
            set_cell_vAlign(tc, "center")
            for p in tc.findall(W("p")):
                pPr = p.find(W("pPr"))
                if pPr is not None:
                    for ind in pPr.findall(W("ind")):
                        pPr.remove(ind)
                    if ri == 0:
                        for old in pPr.findall(W("jc")):
                            pPr.remove(old)
                        pPr.append(make("jc", val="center"))
                if ri == 0:
                    for r in p.findall(W("r")):
                        set_run_bold(r)
            if ri == 0:
                set_cell_shading(tc, "F2F2F2")


# ---------- Cover page ----------

def make_paragraph(text, *, sz_half_pt=None, bold=False, jc="left",
                   rfonts_eastAsia=None, no_indent=True):
    p = OxmlElement("w:p")
    pPr = OxmlElement("w:pPr")
    p.append(pPr)
    if no_indent:
        ind = OxmlElement("w:ind")
        ind.set(qn("w:firstLineChars"), "0")
        ind.set(qn("w:firstLine"), "0")
        pPr.append(ind)
    if jc:
        pPr.append(make("jc", val=jc))
    if sz_half_pt or bold or rfonts_eastAsia:
        rPr_para = OxmlElement("w:rPr")
        if rfonts_eastAsia:
            f = OxmlElement("w:rFonts")
            f.set(qn("w:ascii"), "Calibri")
            f.set(qn("w:hAnsi"), "Calibri")
            f.set(qn("w:eastAsia"), rfonts_eastAsia)
            f.set(qn("w:cs"), "Calibri")
            rPr_para.append(f)
        if bold:
            rPr_para.append(OxmlElement("w:b"))
            rPr_para.append(OxmlElement("w:bCs"))
        if sz_half_pt:
            sz_el = OxmlElement("w:sz")
            sz_el.set(qn("w:val"), str(sz_half_pt))
            rPr_para.append(sz_el)
            szCs_el = OxmlElement("w:szCs")
            szCs_el.set(qn("w:val"), str(sz_half_pt))
            rPr_para.append(szCs_el)
        pPr.append(rPr_para)
    if text:
        r = OxmlElement("w:r")
        if sz_half_pt or bold or rfonts_eastAsia:
            rPr = OxmlElement("w:rPr")
            r.append(rPr)
            if rfonts_eastAsia:
                f = OxmlElement("w:rFonts")
                f.set(qn("w:ascii"), "Calibri")
                f.set(qn("w:hAnsi"), "Calibri")
                f.set(qn("w:eastAsia"), rfonts_eastAsia)
                f.set(qn("w:cs"), "Calibri")
                rPr.append(f)
            if bold:
                rPr.append(OxmlElement("w:b"))
                rPr.append(OxmlElement("w:bCs"))
            if sz_half_pt:
                sz_el = OxmlElement("w:sz")
                sz_el.set(qn("w:val"), str(sz_half_pt))
                rPr.append(sz_el)
                szCs_el = OxmlElement("w:szCs")
                szCs_el.set(qn("w:val"), str(sz_half_pt))
                rPr.append(szCs_el)
        t = OxmlElement("w:t")
        t.text = text
        t.set(qn("xml:space"), "preserve")
        r.append(t)
        p.append(r)
    return p


def make_blank_paragraph():
    return make_paragraph("", jc="left")


def make_cover_table(rows, widths, *, header=False, row_heights=None,
                     label_bold_predicate=None):
    """Build a cover-page table.

    rows: list of rows. Each row is a list of cells. A cell is either a string
          (span=1) or a tuple (text, span) for column merging via gridSpan.
    widths: per-column widths in twips (length == max columns before merging).
    header: when True, row 0 gets F2F2F2 fill + center + bold.
    row_heights: optional list of per-row twHeight values; pass [] or None to skip.
    label_bold_predicate: callable(ri, ci, text) -> bool for non-header rows;
          defaults to "even-indexed cells are labels (bold)".
    """
    if label_bold_predicate is None:
        label_bold_predicate = lambda _ri, ci, _text: ci % 2 == 0

    tbl = OxmlElement("w:tbl")
    tblPr = OxmlElement("w:tblPr")
    tblPr.append(make("tblW", w=sum(widths), type="dxa"))
    tblPr.append(make("jc", val="center"))
    tblPr.append(make("tblLayout", type="fixed"))
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(make(side, val="single", color="auto", sz=4, space=0))
    tblPr.append(borders)
    cm = OxmlElement("w:tblCellMar")
    cm.append(make("top", w=0, type="dxa"))
    cm.append(make("left", w=108, type="dxa"))
    cm.append(make("bottom", w=0, type="dxa"))
    cm.append(make("right", w=108, type="dxa"))
    tblPr.append(cm)
    tbl.append(tblPr)

    grid = OxmlElement("w:tblGrid")
    for w_v in widths:
        grid.append(make("gridCol", w=w_v))
    tbl.append(grid)

    for ri, row_cells in enumerate(rows):
        tr = OxmlElement("w:tr")
        if row_heights and ri < len(row_heights) and row_heights[ri]:
            trPr = OxmlElement("w:trPr")
            trPr.append(make("trHeight", val=row_heights[ri]))
            tr.append(trPr)
        col_idx = 0  # logical column index in the underlying grid
        for cell in row_cells:
            if isinstance(cell, tuple):
                text, span = cell
            else:
                text, span = cell, 1
            tc = OxmlElement("w:tc")
            tcPr = OxmlElement("w:tcPr")
            merged_w = sum(widths[col_idx:col_idx + span])
            tcPr.append(make("tcW", w=merged_w, type="dxa"))
            if span > 1:
                tcPr.append(make("gridSpan", val=span))
            tcPr.append(make("vAlign", val="center"))
            if header and ri == 0:
                tcPr.append(make("shd", val="clear", color="auto", fill="F2F2F2"))
            tc.append(tcPr)
            jc = "center" if (header and ri == 0) else "left"
            bold = (header and ri == 0) or (
                not header and label_bold_predicate(ri, col_idx, text)
            )
            # Split on \n so a single cell can contain multiple paragraphs
            # (used for 需求调研日期 with multiple dates stacked vertically).
            lines = (text or "").split("\n") if text else [""]
            for line in lines:
                tc.append(make_paragraph(
                    line, sz_half_pt=24, bold=bold, jc=jc,
                    rfonts_eastAsia="等线", no_indent=True,
                ))
            tr.append(tc)
            col_idx += span
        tbl.append(tr)
    return tbl


def render_req_type_cell(selected: str) -> str:
    """Render the 需求类型 row text. The matched key gets ☑, others ☐."""
    parts = []
    for key, label in REQ_TYPE_LABELS:
        prefix = "☑" if key == selected else "☐"
        parts.append(f"{prefix}{label}")
    return "    ".join(parts)


def build_cover_blocks(meta: dict | None = None):
    """Build the cover page matching the 杭州产投-AI应用 standard template.

    `meta` is a dict of pre-filled field values. Any missing key falls back to
    a blank cell so the user can hand-fill it in Word.

    Recognised keys:
      project_name, issue_no, version, manager, editor, date,
      department, research_dates (newline-separated for multi-line),
      req_type (one of: initial / new / change / env / ""),
      changelog (内容), changelog_version (默认沿用 version), changelog_date
    """
    m = dict(meta or {})
    title_text = m.get("project_name") or "（项目名称）"
    issue_no = m.get("issue_no", "")
    version = m.get("version", "")
    manager = m.get("manager", "")
    editor = m.get("editor", "")
    date = m.get("date", "")
    department = m.get("department", "")
    research_dates = m.get("research_dates", "")
    req_type = m.get("req_type", "")
    changelog = m.get("changelog", "")
    changelog_version = m.get("changelog_version") or version
    changelog_date = m.get("changelog_date") or date

    blocks = []

    # Title — 26pt bold center
    blocks.append(make_paragraph(
        title_text, sz_half_pt=52, bold=True, jc="center",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    # Subtitle — 22pt bold center
    blocks.append(make_paragraph(
        "需求确认单", sz_half_pt=44, bold=True, jc="center",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    # 编号 — right aligned
    issue_text = f"编号：（{issue_no}）" if issue_no else "编号：(              )"
    blocks.append(make_paragraph(
        issue_text, sz_half_pt=24, bold=False, jc="right",
        rfonts_eastAsia="等线", no_indent=True,
    ))

    # Project info table (6 rows, gridSpan on rows 0/4/5)
    project_info_widths = [1680, 2585, 2086, 2436]  # total 8787
    project_info_row_heights = [907, 919, 743, 870, 1088, 1269]
    project_info_rows = [
        [("项目名称", 1), (m.get("project_name", ""), 3)],
        [("需求版本", 1), (version, 1), ("项目经理", 1), (manager, 1)],
        [("编写人", 1), (editor, 1), ("最新编辑日期", 1), (date, 1)],
        [("业务部门", 1), (department, 1), ("需求调研日期", 1), (research_dates, 1)],
        [("需求类型", 1), (render_req_type_cell(req_type), 3)],
        [("客户确认", 1), ("确认签字：", 3)],
    ]
    blocks.append(make_cover_table(
        project_info_rows, project_info_widths,
        header=False, row_heights=project_info_row_heights,
    ))

    # Two blank paragraphs + 变更记录 label + one blank
    blocks.append(make_blank_paragraph())
    blocks.append(make_blank_paragraph())
    blocks.append(make_paragraph(
        "变更记录", sz_half_pt=24, bold=True, jc="left",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    blocks.append(make_blank_paragraph())

    # Changelog table — pre-fill row 1 with whatever meta provides
    changelog_widths = [1200, 1500, 4587, 1500]  # total 8787
    changelog_rows = [
        ["版本", "日期", "变更内容", "修改人"],
        [changelog_version, changelog_date, changelog, editor],
    ]
    blocks.append(make_cover_table(changelog_rows, changelog_widths, header=True))

    # Page break to push body to a new page
    pb = OxmlElement("w:p")
    pb.append(OxmlElement("w:pPr"))
    r = OxmlElement("w:r")
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r.append(br)
    pb.append(r)
    blocks.append(pb)
    return blocks


# ---------- Main ----------

def parse_args():
    p = argparse.ArgumentParser(
        description="Insert cover + normalize tables in a 需求确认单 docx.",
    )
    p.add_argument("docx", help="path to docx (modified in place)")
    p.add_argument("--project-name", default="",
                   help="项目名称：填封面主标题 + 项目信息表行1")
    p.add_argument("--issue-no", default="", help="编号 — 数字或字母，置于括号内")
    p.add_argument("--version", default="", help="需求版本 (例 V1.0)")
    p.add_argument("--manager", default="", help="项目经理")
    p.add_argument("--editor", default="", help="编写人 (同步填变更记录修改人)")
    p.add_argument("--date", default="", help="最新编辑日期 (YYYY-MM-DD)")
    p.add_argument("--department", default="", help="业务部门")
    p.add_argument("--research-dates", default="",
                   help="需求调研日期；多个日期用换行 \\n 分隔（cell 内多段）")
    p.add_argument("--req-type", default="",
                   choices=["", "initial", "new", "change", "env"],
                   help="需求类型对应的 ☑ 选项；不填则全部留 ☐")
    p.add_argument("--changelog", default="",
                   help="变更记录第一行的【变更内容】(例：初稿 / 新增 X 模块)")
    p.add_argument("--changelog-version", default="",
                   help="变更记录第一行的【版本】，默认沿用 --version")
    p.add_argument("--changelog-date", default="",
                   help="变更记录第一行的【日期】，默认沿用 --date")
    p.add_argument("--no-cover", action="store_true",
                   help="只规整表格，不插入封面（已有封面时用）")
    return p.parse_args()


def main():
    args = parse_args()
    target = Path(args.docx).resolve()
    if not target.exists():
        raise SystemExit(f"file not found: {target}")

    doc = Document(str(target))
    body = doc.element.body

    for tbl in body.findall(W("tbl")):
        normalize_table(tbl)

    if not args.no_cover:
        # \n in --research-dates is interpreted literally, but shells often pass
        # the two characters \ + n; normalise both forms.
        research_dates = args.research_dates.replace("\\n", "\n")
        meta = {
            "project_name": args.project_name,
            "issue_no": args.issue_no,
            "version": args.version,
            "manager": args.manager,
            "editor": args.editor,
            "date": args.date,
            "department": args.department,
            "research_dates": research_dates,
            "req_type": args.req_type,
            "changelog": args.changelog,
            "changelog_version": args.changelog_version,
            "changelog_date": args.changelog_date,
        }
        cover = build_cover_blocks(meta)
        first_child = list(body)[0]
        for blk in cover:
            first_child.addprevious(blk)

    doc.save(str(target))
    print(f"postprocessed: {target}")


if __name__ == "__main__":
    main()
