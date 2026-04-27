"""Generate templates/reference-zhcn.docx — the pandoc reference doc that
encodes the 璞华需求确认单 style spec (abstracted from 杭州产投确认单 +
light Chinese-typography optimizations).

Run this script when you change the style spec; ship the resulting docx
in templates/ alongside the skill.

Style spec
----------
- Page A4, margins top/bottom 2.54 cm / left/right 3.17 cm
- docGrid lines, linePitch 312
- Default font: 等线 (eastAsia), Calibri (ascii), kern 2
- Normal: 12pt, justified, 1.5x line, 2-char first-line indent
- H1 22pt bold center (no color), H2 16pt bold 黑体, H3 16pt bold 等线,
  H4 14pt bold 黑体, H5 14pt bold 等线, H6 12pt bold 黑体
- Table Grid: 0.5pt single line all borders, cell margin L/R 108 twip,
  centered, fixed layout
"""
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Write into the skill's templates/ folder (sibling of scripts/).
OUT = Path(__file__).resolve().parent.parent / "templates" / "reference-zhcn.docx"


def w(tag: str) -> str:
    return qn(f"w:{tag}")


def make(tag: str, **attrs):
    el = OxmlElement(f"w:{tag}")
    for k, v in attrs.items():
        el.set(qn(f"w:{k}"), str(v))
    return el


def get_or_make(parent, tag, *, before=None):
    el = parent.find(w(tag))
    if el is not None:
        return el
    el = OxmlElement(f"w:{tag}")
    if before:
        anchor = parent.find(w(before))
        if anchor is not None:
            anchor.addprevious(el)
            return el
    parent.append(el)
    return el


def set_section(section):
    sectPr = section._sectPr
    for child_tag in ("pgSz", "pgMar", "cols", "docGrid"):
        for el in sectPr.findall(w(child_tag)):
            sectPr.remove(el)
    sectPr.append(make("pgSz", w=11906, h=16838))
    sectPr.append(make("pgMar", top=1440, right=1800, bottom=1440,
                       left=1800, header=851, footer=992, gutter=0))
    sectPr.append(make("cols", space=425, num=1))
    sectPr.append(make("docGrid", type="lines", linePitch=312, charSpace=0))


def set_rfonts(rPr, *, ascii_="Calibri", eastAsia="等线", cs="Calibri"):
    """Strip theme-font attrs and pin explicit font names. Theme fonts vary
    across machines that lack the matching theme mapping — explicit names
    keep rendering deterministic."""
    f = get_or_make(rPr, "rFonts")
    for theme_attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        if f.get(qn(f"w:{theme_attr}")) is not None:
            del f.attrib[qn(f"w:{theme_attr}")]
    f.set(qn("w:ascii"), ascii_)
    f.set(qn("w:hAnsi"), ascii_)
    f.set(qn("w:eastAsia"), eastAsia)
    f.set(qn("w:cs"), cs)


def strip_default_decorations(rPr):
    """python-docx ships headings with blue color + italic — drop both."""
    for tag in ("color", "i", "iCs"):
        for el in rPr.findall(w(tag)):
            rPr.remove(el)


def set_size(rPr, half_pt: int):
    sz = get_or_make(rPr, "sz")
    sz.set(qn("w:val"), str(half_pt))
    szCs = get_or_make(rPr, "szCs")
    szCs.set(qn("w:val"), str(half_pt))


def set_bold(rPr, on: bool = True):
    if on:
        if rPr.find(w("b")) is None:
            rPr.append(OxmlElement("w:b"))
        if rPr.find(w("bCs")) is None:
            rPr.append(OxmlElement("w:bCs"))


def set_kern(rPr, val: int):
    k = get_or_make(rPr, "kern")
    k.set(qn("w:val"), str(val))


def reset_pPr_spacing(pPr, *, before=None, after=None, line=None,
                      lineRule="auto", jc=None, widowControl=None,
                      keepNext=False, keepLines=False):
    sp = get_or_make(pPr, "spacing")
    if before is not None:
        sp.set(qn("w:before"), str(before))
        sp.set(qn("w:beforeLines"), "0")
        sp.set(qn("w:beforeAutospacing"), "0")
    if after is not None:
        sp.set(qn("w:after"), str(after))
        sp.set(qn("w:afterLines"), "0")
        sp.set(qn("w:afterAutospacing"), "0")
    if line is not None:
        sp.set(qn("w:line"), str(line))
        sp.set(qn("w:lineRule"), lineRule)
    if jc is not None:
        j = get_or_make(pPr, "jc")
        j.set(qn("w:val"), jc)
    if widowControl is not None:
        wc = get_or_make(pPr, "widowControl")
        wc.set(qn("w:val"), str(widowControl))
    if keepNext and pPr.find(w("keepNext")) is None:
        pPr.append(OxmlElement("w:keepNext"))
    if keepLines and pPr.find(w("keepLines")) is None:
        pPr.append(OxmlElement("w:keepLines"))


def style_by_name(doc, name):
    for s in doc.styles:
        if s.name == name:
            return s
    return None


def get_style_el(doc, name):
    s = style_by_name(doc, name)
    return s.element if s else None


def configure_normal(doc):
    el = get_style_el(doc, "Normal")
    pPr = get_or_make(el, "pPr", before="rPr")
    reset_pPr_spacing(pPr, line=360, lineRule="auto", jc="both", widowControl=0)
    ind = get_or_make(pPr, "ind")
    ind.set(qn("w:firstLineChars"), "200")
    ind.set(qn("w:firstLine"), "480")
    rPr = get_or_make(el, "rPr")
    set_rfonts(rPr, ascii_="Calibri", eastAsia="等线", cs="Calibri")
    set_size(rPr, 24)
    set_kern(rPr, 2)


def configure_heading(doc, level, *, sz_half_pt, eastAsia,
                      before, after, line, jc=None, kern=None):
    el = get_style_el(doc, f"Heading {level}")
    if el is None:
        return
    pPr = get_or_make(el, "pPr", before="rPr")
    reset_pPr_spacing(pPr, before=before, after=after, line=line,
                      lineRule="auto", jc=jc, widowControl=0,
                      keepNext=True, keepLines=True)
    # Headings should not first-line indent
    ind = pPr.find(w("ind"))
    if ind is not None:
        pPr.remove(ind)
    rPr = get_or_make(el, "rPr")
    strip_default_decorations(rPr)
    set_rfonts(rPr, ascii_="Calibri", eastAsia=eastAsia, cs="Calibri")
    set_size(rPr, sz_half_pt)
    set_bold(rPr, True)
    if kern is not None:
        set_kern(rPr, kern)


def configure_table_grid(doc):
    el = get_style_el(doc, "Table Grid")
    if el is None:
        return
    tblPr = get_or_make(el, "tblPr")
    for old in tblPr.findall(w("tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(make(side, val="single", color="auto", sz=4, space=0))
    tblPr.append(borders)
    for old in tblPr.findall(w("tblCellMar")):
        tblPr.remove(old)
    mar = OxmlElement("w:tblCellMar")
    mar.append(make("top", w=0, type="dxa"))
    mar.append(make("left", w=108, type="dxa"))
    mar.append(make("bottom", w=0, type="dxa"))
    mar.append(make("right", w=108, type="dxa"))
    tblPr.append(mar)
    for old in tblPr.findall(w("jc")):
        tblPr.remove(old)
    tblPr.append(make("jc", val="center"))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    set_section(doc.sections[0])

    configure_normal(doc)
    configure_heading(doc, 1, sz_half_pt=44, eastAsia="等线",
                      before=340, after=330, line=576, jc="center", kern=44)
    configure_heading(doc, 2, sz_half_pt=32, eastAsia="黑体",
                      before=260, after=260, line=413)
    configure_heading(doc, 3, sz_half_pt=32, eastAsia="等线",
                      before=260, after=260, line=413)
    configure_heading(doc, 4, sz_half_pt=28, eastAsia="黑体",
                      before=280, after=290, line=372)
    configure_heading(doc, 5, sz_half_pt=28, eastAsia="等线",
                      before=280, after=290, line=372)
    configure_heading(doc, 6, sz_half_pt=24, eastAsia="黑体",
                      before=240, after=64, line=317)

    configure_table_grid(doc)

    styles_part = doc.styles.element
    docDefaults = styles_part.find(w("docDefaults"))
    if docDefaults is not None:
        rPrDefault = docDefaults.find(w("rPrDefault"))
        if rPrDefault is not None:
            rPr = rPrDefault.find(w("rPr"))
            if rPr is None:
                rPr = OxmlElement("w:rPr")
                rPrDefault.append(rPr)
            set_rfonts(rPr, ascii_="Calibri", eastAsia="等线", cs="Calibri")
            set_kern(rPr, 2)
            set_size(rPr, 24)

    doc.save(str(OUT))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
