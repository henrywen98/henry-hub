"""Post-process pandoc docx output for the 璞华需求确认单 style.

What it does:

1. Insert a cover page with empty fields for the user to fill in Word:
   主标题（项目名称）/ 副标题（需求确认单）/ 编号 /
   项目信息 4 列表 / 文件修订历史 4 列表 / 分页符
2. Normalize every body table:
   - Apply preset column widths by column count and header signature
     (信息项-备注 narrow/wide; 项目信息 4 列固定宽度; 等等)
   - Center the table, fixed layout, full single-line borders 0.5pt
   - Header row: F2F2F2 grey fill + bold + horizontal center
   - All cells: vertical center; drop first-line indent inside cells

Usage:  python3 postprocess.py path/to/output.docx
"""
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

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
            tc.append(make_paragraph(
                text or "", sz_half_pt=24, bold=bold, jc=jc,
                rfonts_eastAsia="等线", no_indent=True,
            ))
            tr.append(tc)
            col_idx += span
        tbl.append(tr)
    return tbl


def build_cover_blocks():
    """Build the cover page matching the 杭州产投-AI应用 standard template.

    Layout (all fields blank for the user to fill in Word):
      - title 26pt, subtitle 22pt, 编号 right
      - 6-row project info table with gridSpan merges on rows 0/4/5
      - 变更记录 label + 4-col changelog table with one empty data row
    """
    blocks = []

    # Title (project name placeholder) — 26pt bold center
    blocks.append(make_paragraph(
        "（项目名称）", sz_half_pt=52, bold=True, jc="center",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    # Subtitle — 22pt bold center
    blocks.append(make_paragraph(
        "需求确认单", sz_half_pt=44, bold=True, jc="center",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    # 编号 — right aligned
    blocks.append(make_paragraph(
        "编号：(              )", sz_half_pt=24, bold=False, jc="right",
        rfonts_eastAsia="等线", no_indent=True,
    ))

    # Project info table (6 rows, gridSpan on rows 0/4/5)
    project_info_widths = [1680, 2585, 2086, 2436]  # total 8787
    project_info_row_heights = [907, 919, 743, 870, 1088, 1269]
    project_info_rows = [
        [("项目名称", 1), ("", 3)],
        [("需求版本", 1), ("", 1), ("项目经理", 1), ("", 1)],
        [("编写人", 1), ("", 1), ("最新编辑日期", 1), ("", 1)],
        [("业务部门", 1), ("", 1), ("需求调研日期", 1), ("", 1)],
        [("需求类型", 1),
         ("☐初始需求    ☐新增需求    ☐需求变更    ☐系统环境变更", 3)],
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

    # Changelog table (matches the AI 应用 reference: 4 cols, one empty data row)
    changelog_widths = [1200, 1500, 4587, 1500]  # total 8787
    changelog_rows = [
        ["版本", "日期", "变更内容", "修改人"],
        ["", "", "", ""],
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

def main():
    if len(sys.argv) < 2:
        print("usage: postprocess.py <docx>", file=sys.stderr)
        sys.exit(1)
    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(f"file not found: {target}", file=sys.stderr)
        sys.exit(1)

    doc = Document(str(target))
    body = doc.element.body

    for tbl in body.findall(W("tbl")):
        normalize_table(tbl)

    cover = build_cover_blocks()
    first_child = list(body)[0]
    for blk in cover:
        first_child.addprevious(blk)

    doc.save(str(target))
    print(f"postprocessed: {target}")


if __name__ == "__main__":
    main()
