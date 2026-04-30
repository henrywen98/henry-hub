# Excel 排版常量与封装范式

`aggregate.py` 里所有样式都通过 openpyxl 的 `Font` / `Fill` / `Alignment` / `Border` 实现,不依赖外部主题。这份参考列出可调项,以及"为什么要这么调"的理由。

## 颜色面板(打开即用、视觉清爽)

| 用途 | 十六进制 | 出现位置 |
|---|---|---|
| 表头深蓝 | `#1F4E78` | 自动列表头(白字) |
| 标题深蓝 | `#305496` | 每张 sheet 顶部 row 1 |
| 手填列橙黄 | `#FFC000` | 手填列表头(黑字,提示用户可写) |
| 斑马纹浅灰 | `#F2F2F2` | 偶数行底色 |
| 边框灰 | `#BFBFBF` | 全表 thin 边框 |
| 警告浅红 | `#FCE4D6` | 条件格式: 缺件/异常行 |
| 成功浅绿 | `#E2EFDA` | 条件格式: 已完成行 |
| 汇总区蓝 | `#D9E1F2` | Sheet 3 底部统计行 |

前缀色带(为什么要给"功能前缀"列上色: 用户在 80 行以上的 sheet 里能瞬间分组定位到一类功能):

| 前缀 | 浅色调 |
|---|---|
| 第 1 组 | `#DEEBF7` 浅蓝 |
| 第 2 组 | `#E2EFDA` 浅绿 |
| 第 3 组 | `#EAD3F2` 浅紫 |
| 第 4 组 | `#FCE4B6` 浅橙 |
| 第 5 组 | `#FFF2CC` 浅黄 |
| 第 6 组 | `#E7E6E6` 浅灰 |

如果项目超过 6 个前缀,继续往下加: `#FFE4E1` (浅粉)、`#D5E8D4` (薄荷绿)、`#FFD9CC` (杏色)。**避免**红色/纯黄色高饱和填充,会和条件格式抢视觉。

## 字体

```python
FONT_NAME = "Arial"
# 中文回退到系统默认中文字体(macOS = PingFang SC, Windows = Microsoft YaHei)
# 不设 fallback,openpyxl 写出去 Excel/Numbers 会自动 fallback
```

为什么 Arial: xlsx skill 强制要求 "professional font",并且跨平台一致。**不要**用 Calibri(Office 默认,跨平台渲染不一致)或华文宋体(中文环境过时)。

字号:
- 标题(row 1): 14, bold
- 表头(row 2): 11, bold, white
- 数据行: 10
- README 章节标题: 12, bold

## 关键样式约束

排版能不能"打开即用",取决于这 5 件事都做对:

### 1. 冻结窗格

```python
ws.freeze_panes = "C3"  # 冻结前两列 + 表头(row 1+2)
```

`C3` 表示"C 列开始往右、第 3 行开始往下可以滚动"。用户横滑长行时,功能前缀和模块名始终可见。

### 2. 自动筛选

```python
ws.auto_filter.ref = f"A2:{last_col_letter}{last_row}"  # 表头从 row 2 开始
```

让用户能按"功能前缀 / 文档类型 / 开发状态 / 责任人"快速过滤。**别忘了** ref 范围要覆盖到表头所在那一行。

### 3. 条件格式(用 FormulaRule,不要 Python 端硬涂色)

```python
from openpyxl.formatting.rule import FormulaRule

# 整行高亮: 用 $G3 而不是 G3 (前者锁定列,后者会跟着列偏移)
ws.conditional_formatting.add(
    f"A3:{last_col}{last_row}",
    FormulaRule(formula=['$G3="已完成"'], stopIfTrue=False, fill=SUCCESS_FILL),
)
```

为什么不在 Python 端涂色: **用户改了"开发状态"列后,高亮要自动跟随**。Python 端硬涂的颜色不会更新。

### 4. 长文本自动换行

```python
WRAP_CENTER = Alignment(horizontal="left", vertical="center", wrap_text=True)
```

需求描述、说明、备注这种列必须 `wrap_text=True`,否则长文本会跑到下一列遮挡内容。其他列用 `CENTER_CENTER` (横向居中、竖向居中、wrap_text=True)。

### 5. 列宽手动指定

`auto_fit` 在 openpyxl 里不可靠(各 Excel 实现差异大)。手动指定:

```python
# 短码列 8-12,正文列 30-50,长说明列 50-60
widths = [10, 28, 14, 60, 40, 20, 12, 10, 10, 14, 30]  # Sheet 1 实战值
```

## 封装范式: apply_table_style

为了避免每张 sheet 都重复一遍样式代码,封装成一个函数:

```python
def apply_table_style(
    ws: Worksheet,
    n_rows: int,
    n_cols: int,
    long_text_cols: set[int],   # 哪些列需要 wrap_text
    prefix_col: int | None = None,  # 前缀色带应用的列(通常是第一列)
    rows_data: list | None = None,  # 用于按 row.prefix 上色
) -> None:
    for r in range(3, 3 + n_rows):
        zebra = (r - 2) % 2 == 0
        for c in range(1, n_cols + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = _font()
            cell.alignment = WRAP_CENTER if c in long_text_cols else CENTER_CENTER
            cell.border = BORDER
            if zebra:
                cell.fill = ALT_ROW_FILL
        if prefix_col and rows_data:
            data_idx = r - 3
            if data_idx < len(rows_data):
                pfx = getattr(rows_data[data_idx], "prefix", None)
                if pfx in PREFIX_FILLS:
                    ws.cell(row=r, column=prefix_col).fill = PREFIX_FILLS[pfx]
        ws.row_dimensions[r].height = 22
```

调用一次就能给整张 sheet 套上斑马纹 / 边框 / 字体 / wrap / 前缀色带。

## openpyxl 公式 vs 计算值

openpyxl 写出的公式**不会自动计算**,只会保存公式字符串。Excel/Numbers 打开时会延迟计算,但有些情况(比如其他脚本用 `data_only=True` 读)会读到 None。

唯一可靠的解法: 写完后用 LibreOffice 重算一遍。`document-skills:xlsx` skill 提供了 `scripts/recalc.py`:

```bash
python <xlsx_skill>/scripts/recalc.py <output>.xlsx 60
```

期望输出 `{"total_errors": 0}`。如果脚本生成的公式有 bug(`#REF!` / `#DIV/0!`),这一步会暴露。

## 为什么不引入 pandas styler / xlsxwriter

- pandas styler 写出的样式和 openpyxl 的不兼容,而且重跑读回来会丢
- xlsxwriter 不支持读取已有文件,无法做"手填列保留"
- 综上,坚持纯 openpyxl 是最小依赖、最大可控的方案

## 反模式速查

- ❌ 写死颜色字符串到每个 cell,不抽常量 → 改色要改一百处
- ❌ 用 `auto_fit` 替代手动 column_dimensions → 跨平台显示不一致
- ❌ 用 Python 涂色而非条件格式 → 用户改数据后高亮失效
- ❌ 不冻结窗格 / 不开筛选 → 大表用起来痛苦
- ❌ 把 `wrap_text` 用到所有列 → 短码列变得很难看(行高被拉爆)
