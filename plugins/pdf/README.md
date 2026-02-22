# pdf

全面的 PDF 处理工具包，支持文本和表格提取、创建新 PDF、合并/拆分文档以及表单处理。适用于需要程序化处理、生成或大规模分析 PDF 文档的场景。

## 使用场景

当用户需要进行以下操作时触发：

- 填写 PDF 表单
- 提取 PDF 中的文本或表格数据
- 创建新的 PDF 文档
- 合并或拆分 PDF 文件
- 添加水印、密码保护
- OCR 扫描件识别
- 提取 PDF 中的图片

### 支持的工具链

- **pypdf**：基础操作（合并、拆分、旋转、元数据）
- **pdfplumber**：文本和表格提取
- **reportlab**：创建新 PDF
- **qpdf / pdftk**：命令行工具
- **pytesseract**：OCR 扫描件识别

## 安装

```bash
/plugins install pdf@henry-hub
```

## 使用示例

```
用户：帮我填写这份 PDF 表单
Claude：我来读取表单字段并帮你填写...

用户：从这份 PDF 中提取所有表格数据
Claude：我使用 pdfplumber 来提取表格...

用户：把这三份 PDF 合并成一个文件
Claude：我用 pypdf 来合并这些文档...
```
