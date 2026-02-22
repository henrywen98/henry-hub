# docx

全面的 Word 文档（.docx）创建、编辑和分析工具。支持修订追踪、批注、格式保留和文本提取，涵盖专业文档处理的完整工作流。

## 使用场景

当用户需要进行以下操作时触发：

- 创建新的 Word 文档
- 修改或编辑现有 .docx 文件内容
- 使用修订追踪（Track Changes）进行文档审阅
- 添加批注（Comments）
- 提取文档文本或分析文档结构
- 将文档转换为图片进行可视化分析

### 支持的工作流

- **文本提取**：使用 pandoc 转换为 Markdown
- **新建文档**：使用 docx-js（JavaScript）创建
- **编辑文档**：使用 OOXML 直接操作 XML
- **文档审阅**：修订追踪（Redlining）工作流

## 安装

```bash
/plugins install docx@henry-hub
```

## 使用示例

```
用户：创建一份项目报告的 Word 文档
Claude：我来使用 docx-js 为你创建文档...

用户：帮我在这份合同中添加修订追踪的修改
Claude：我将使用 Redlining 工作流来添加修订...

用户：提取这份 docx 文件的文本内容
Claude：我用 pandoc 将文档转换为 Markdown 格式...
```
