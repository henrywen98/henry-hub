# PRD Review Board — 多专家红队评审工作流

PRD（Product Requirements Document）多专家红队评审工具。使用 Claude Code 的 Team Swarm 能力，组建 14 位跨职能专家评审团，对 PRD 进行企业级红队评审。

## 使用场景

- 对已有 PRD 进行全方位专家评审
- 将原始需求（文本、截图、原型图等）转化为 PRD 并评审
- 模拟真实产品评审会议，多专家独立评审 + 交叉辩论
- 红队压力测试：评估系统在极端条件下的表现
- 生成风险矩阵、成本评估和修订版 PRD

## 安装

```
/plugins install prd-review-board@henry-hub
```

## 使用方法

```
/prd-review <PRD文件路径或需求描述>
```

### 输入格式

支持任意格式的输入：
- 文件路径（`.md`、`.txt`、`.pdf` 等）
- 直接粘贴的文本
- 截图路径
- URL
- 语音转文字内容
- 原型图描述

### 示例

```
/prd-review ./specs/user-auth-prd.md
/prd-review 我需要一个支持多租户的SaaS订单管理系统
```

## 工作流程

```
Phase 1: 输入处理 & PRD 生成
    ↓
Phase 2: 组建 14 人评审团 & 独立评审
    ↓
Phase 3: 红队压力测试
    ↓
Phase 4: 3 轮真实辩论（Agent 间消息传递）
    ↓
Phase 5: 风险矩阵 & 成本评估
    ↓
Phase 6: 必须修改项 & 修订 PRD
    ↓
Phase 7: 最终裁决（GO / CONDITIONAL GO / NO-GO）
    ↓
Phase 8: 综合报告 & 团队清理
```

## 专家评审团（14 位）

### 产品 & 技术核心
| 角色 | 经验 | 评审重点 |
|------|------|---------|
| PRD Writer | 18+ 年 | PRD 撰写与修订 |
| Principal PM | 15+ 年 | 产品市场匹配、用户价值 |
| Staff Architect | 20+ 年 | 架构可行性、技术债 |
| Distributed Systems | 15+ 年 | 分布式一致性、故障模式 |
| Backend Engineer | 12+ 年 | API 设计、数据建模 |
| Frontend Engineer | 10+ 年 | UI 实现、可访问性 |
| QA Director | 15+ 年 | 可测试性、质量策略 |

### AI & 数据
| 角色 | 经验 | 评审重点 |
|------|------|---------|
| AI Architect | 12+ 年 | AI 可行性、数据管道 |
| LLM Safety | 8+ 年 | 幻觉风险、提示注入防御 |

### 平台 & 可靠性
| 角色 | 经验 | 评审重点 |
|------|------|---------|
| DevOps/SRE | 12+ 年 | 部署策略、可观测性 |
| Performance Engineer | 10+ 年 | 性能瓶颈、容量规划 |

### 风险 & 商业
| 角色 | 经验 | 评审重点 |
|------|------|---------|
| Security & Compliance | 14+ 年 | 安全漏洞、合规要求 |
| FinOps | 10+ 年 | 成本预估、单位经济 |
| Business Strategist | 15+ 年 | 商业模式、市场定位 |

## 输出文件

```
{output-dir}/
├── 01-prd-v1.md              # 初版 PRD
├── 02-reviews/                # 13 份独立评审报告
├── 03-stress-test.md          # 红队压力测试
├── 04-debate-log.md           # 3 轮辩论记录
├── 05-risk-matrix.md          # 风险矩阵（≥10条）
├── 06-finops-assessment.md    # 成本与规模化评估
├── 07-required-changes.md     # 必须修改项（红/黄/绿）
├── 08-prd-v2-revised.md       # 修订版 PRD
├── 09-final-verdict.md        # 最终裁决
└── 10-comprehensive-report.md # 综合完整报告
```

## 注意事项

- 此工作流使用 Team Swarm，将创建 13+ 个并行 agent
- Token 消耗较大（评审专家使用 sonnet，PRD 撰写使用 opus）
- 整个流程可能需要 10-30 分钟
- 可随时中断
