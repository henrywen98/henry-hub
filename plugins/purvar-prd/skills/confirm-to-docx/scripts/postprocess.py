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


def make_cover_table(rows, widths, *, header=False):
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
        for ci, text in enumerate(row_cells):
            tc = OxmlElement("w:tc")
            tcPr = OxmlElement("w:tcPr")
            tcPr.append(make("tcW", w=widths[ci], type="dxa"))
            tcPr.append(make("vAlign", val="center"))
            if header and ri == 0:
                tcPr.append(make("shd", val="clear", color="auto", fill="F2F2F2"))
            tc.append(tcPr)
            jc = "center" if (header and ri == 0) else "left"
            bold = (header and ri == 0) or (ci % 2 == 0 and not header)
            tc.append(make_paragraph(
                text or "", sz_half_pt=24, bold=bold, jc=jc,
                rfonts_eastAsia="等线", no_indent=True,
            ))
            tr.append(tc)
        tbl.append(tr)
    return tbl


def build_cover_blocks():
    blocks = []
    blocks.append(make_paragraph(
        "（项目名称）", sz_half_pt=52, bold=True, jc="center",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    blocks.append(make_paragraph(
        "需求确认单", sz_half_pt=44, bold=True, jc="center",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    blocks.append(make_paragraph(
        "编号:(              )", sz_half_pt=24, bold=False, jc="right",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    blocks.append(make_blank_paragraph())
    project_info_widths = [1660, 2493, 2076, 2077]
    project_info_rows = [
        ["项目名称", "", "需求版本", ""],
        ["项目经理", "", "编写日期", ""],
    ]
    blocks.append(make_cover_table(project_info_rows, project_info_widths, header=False))
    blocks.append(make_blank_paragraph())
    blocks.append(make_paragraph(
        "文件修订历史", sz_half_pt=24, bold=True, jc="left",
        rfonts_eastAsia="等线", no_indent=True,
    ))
    revision_widths = [1882, 1314, 1118, 3992]
    revision_rows = [
        ["修订时间", "版本", "作者", "说明"],
        ["", "", "", ""],
    ]
    blocks.append(make_cover_table(revision_rows, revision_widths, header=True))
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
