"""
_common.py — 三个 extractor 共享的纯结构 + 共用样式工具。

设计原则: 只放真正"行为一致"的工具,不强行统一不同脚本的语义。

入选 (单一权威实现):
- iter_block_items / normalize / heading_level: 三脚本中 (或 agg+sol 中) 实现 byte-equivalent
- 样式常量 HEADER_FILL/HEADER_FONT/ZEBRA_FILL/THIN_BORDER + _font + _apply_header +
  _apply_data_styles: extract_solution.py + extract_quotation.py 视觉规范一致
  (深蓝表头 / 浅灰斑马 / 浅灰边框)。aggregate.py 有自己的多色样式系统 (手填列橙/
  警告/成功),不在这里;它只用上面的 3 个结构工具。
- 报价列浅黄 PRICE_FILL 仅 extract_quotation 使用,通过 _apply_data_styles 的
  price_col 参数控制 (默认 None 不高亮)。

不入选 (语义差异):
- find_col: aggregate 用完全匹配 `if h in candidates`,extract_solution 用子串匹配
  `if cand in h`,extract_quotation 把子串匹配 inline 在 map_columns 里。
- table_header: aggregate 用 `normalize(c.text)`,extract_solution 用 cell_text
  (多 paragraph join)。
"""
from __future__ import annotations

import re
from typing import Iterator

from docx.document import Document as DocxDocumentT
from docx.oxml.ns import qn
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


# ---------------------------------------------------------------------------
# docx 结构工具
# ---------------------------------------------------------------------------


def iter_block_items(doc: DocxDocumentT) -> Iterator[Paragraph | DocxTable]:
    """按文档顺序产出段落或表格。"""
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield DocxTable(child, doc)


def normalize(text: str) -> str:
    """空白折叠 + strip。"""
    return re.sub(r"\s+", " ", (text or "").strip())


def heading_level(p: Paragraph) -> int | None:
    """从 paragraph style 解析 Heading 层级。

    匹配 "Heading 1" / "Heading10" / "heading 2" 等变体 (大小写不敏感)。
    """
    style = (p.style.name if p.style else "") or ""
    m = re.match(r"Heading\s*(\d+)", style, re.IGNORECASE)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# 共享 openpyxl 样式 (extract_solution.py + extract_quotation.py)
# ---------------------------------------------------------------------------


HEADER_FILL = PatternFill("solid", fgColor="1F4E78")  # 深蓝
HEADER_FONT = Font(name="Arial", size=11, bold=True, color="FFFFFF")
ZEBRA_FILL = PatternFill("solid", fgColor="F2F2F2")
PRICE_FILL = PatternFill("solid", fgColor="FFF2CC")  # 报价列浅黄 (extract_quotation 专用)
_SIDE = Side(style="thin", color="D9D9D9")
THIN_BORDER = Border(left=_SIDE, right=_SIDE, top=_SIDE, bottom=_SIDE)


def _font(bold: bool = False, size: int = 10, color: str = "000000") -> Font:
    return Font(name="Arial", size=size, bold=bold, color=color)


def _apply_header(ws: Worksheet, headers: list[str]) -> None:
    """深蓝表头 + 居中 + 冻结首行 + 自动筛选。"""
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=i, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = THIN_BORDER
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"


def _apply_data_styles(
    ws: Worksheet,
    n_rows: int,
    n_cols: int,
    price_col: int | None = None,
) -> None:
    """斑马纹数据行 + 浅灰边框。可选高亮 price_col 列为浅黄。"""
    for r in range(2, n_rows + 2):
        zebra = ZEBRA_FILL if r % 2 == 0 else None
        for col in range(1, n_cols + 1):
            c = ws.cell(row=r, column=col)
            c.font = _font(size=10)
            c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            c.border = THIN_BORDER
            if col == price_col:
                c.fill = PRICE_FILL
            elif zebra:
                c.fill = zebra
        ws.row_dimensions[r].height = 30
