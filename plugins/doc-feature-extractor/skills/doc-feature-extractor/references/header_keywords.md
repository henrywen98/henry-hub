# PRD 常见表头关键字参考

抽取脚本能不能识别一个表为"FR 表"或"AI 字段表",取决于 `aggregate.py` 顶部那几个关键字元组。下面是实战中遇到过的表头,按场景分类。**用 `inspect_docx.py` 看实际表头后,从这里挑相关项加到对应元组里。**

## FR 编号表(Sheet 1 数据来源)

判定: 表头同时命中 `FR_NUMBER_KEYS` 和 `FR_DESC_KEYS`。

| 元组 | 中文场景 | 英文场景 |
|---|---|---|
| `FR_NUMBER_KEYS` | 编号、FR编号、需求编号、需求号、序号 | Requirement ID, Req ID, ID, FR No, Story ID |
| `FR_DESC_KEYS` | 需求描述、描述、需求、需求内容、详情 | Description, Requirement, Acceptance Criteria, User Story |

陷阱:
- 「序号」太宽,有些项目章节列表也用「序号」做表头 → 会误命中。如果是 Jira / Linear 风格,优先用 `Issue Key` 或 `ID`。
- 「需求」过短,容易和「需求确认」「需求方」混。一般和「需求描述」一起放进 `FR_DESC_KEYS`,避免单独使用。

## AI 字段定义表(Sheet 2 数据来源)

判定: NAME 列命中 + (KEY 列命中 OR TYPE 列命中)。`LENIENT_FIELD_PREFIXES` 里的前缀只需要 NAME 命中即可。

| 元组 | 中文场景 | 英文场景 |
|---|---|---|
| `FIELD_NAME_KEYS` | 字段名称、字段名、信息项、Agent输出字段、字段、属性、参数 | Field Name, Field, Attribute, Parameter, Property |
| `FIELD_KEY_KEYS` | 字段Key、字段 Key、AI 返回 Key、AI返回Key、字段标识、Key、表单字段 Key、变量名 | Key, Variable Name, JSON Key, API Key |
| `TYPE_KEYS` | 类型、数据类型 | Type, Data Type, Datatype |
| `REQUIRED_KEYS` | 必填、是否必填 | Required, Mandatory |
| `CONSTRAINT_KEYS` | 校验规则、约束、限制 | Constraint, Validation, Rule |
| `DESC_KEYS_FIELD` | 说明、描述、备注、注释 | Description, Notes, Remark |
| `SCENARIO_KEYS` | 适用场景、场景、使用场景 | Scenario, Use Case, Context |

陷阱:
- 「字段」单独出现时,有可能是「字段Key」的简写。脚本会先尝试匹配 NAME 里更具体的 `字段名称`,匹配不到才回退到 `字段`。所以**保留「字段」在元组里是安全的**,但要确保 `字段名称` 排在前面。
- 如果表头是 `Agent输出字段` 之类的复合词,这是 06-style PRD 的特点 — 一定要加到 `FIELD_NAME_KEYS`,否则字段表识别不了。
- 「信息项」是需求确认单 / 业务规格类文档的特征,同时它的表只有 2 列(`信息项 + 备注`)— 这种 PRD 要把前缀加到 `LENIENT_FIELD_PREFIXES`。

## 跳过的章节(避免抽到 Prompt / 附录这种)

`SKIP_SECTION_KEYWORDS` 里命中任一关键字的章节都跳过。常见:

| 中文 | 英文 |
|---|---|
| 版本记录、变更记录、修订历史 | Version History, Change Log, Revision History |
| 澄清记录、答疑、Q&A、开放问题 | Clarifications, Q&A, Open Questions |
| 附录、Prompt、调用OCR、示例、API 文档 | Appendix, Examples, API Reference |
| 假设、依赖、范围外、边缘情况、风险 | Assumptions, Dependencies, Out of Scope, Edge Cases, Risks |

## 兜底章节切段时的常见结构

不同 PRD 的"功能粒度"对应的标题级别:

| PRD 风格 | 功能粒度对应级别 | `FALLBACK_HEADING_LEVEL` |
|---|---|---|
| Notion / Confluence 风格,大功能用 H1,子功能用 H2 | H2 | `2` |
| 详细规格,大模块 H1,模块内功能 H2,验收/字段在 H3 | H3 | `3` |
| 简单需求确认单,只用 H1 + H2 | H2 | `2` |
| 飞书 Doc 默认 (H1 = 文档标题, 功能从 H2 起) | H2 | `2` |

不确定时:**先用 inspect_docx 看,有疑问问用户**。错误的兜底层级会导致功能切得过细(取到 H3 切段)或过粗(只在 H1 切到大模块)。
