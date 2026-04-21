# adhd-pm

ADHD 友好的个人项目管理 Skill 模板:基于飞书多维表格 Base 封装 10 种高频操作的稳定工作流。

## 安装

```
/plugins install adhd-pm@henry-hub
```

## 这是什么

把 ADHD 友好的项目管理流程固化成 Claude Code Skill,让 AI 在"加任务 / 关任务 / 查今日 / 周报导入 / 早晚安简报"这类高频场景上有**稳定、确定性的路径**,不再每次临场发挥。

底层:飞书多维表格 Base(Projects / Tasks / Daily Intention / Pomodoros 四表)+ 2 个自动化 workflow。

## 它解决什么问题

ADHD 大脑的两个典型痛点:

1. **启动困难** — 任务看着大,迟迟动不了
2. **时间盲(time blindness)** — 不知道今天该做什么 / 早些时候没做完的是什么 / 还有多久完成

这个 skill 把一套经验证的 ADHD 设计哲学(灵感来自 Leantime 的代码实现)落到飞书 Base 上:

- **2 分钟法则编码** — 估算最小粒度 `⚡ < 2min`,AI 识别到这种任务不建记录,直接催你做
- **5 桶时间分块** — 任务按"今日/早些时候/本周/稍后/无截止"分视图,避免长列表压迫
- **多巴胺反馈循环** — 完成任务触发 🎉 IM,完成项目有"荣誉墙"
- **Implementation Intentions** — 每个任务可以挂 If-Then 触发条件(Peter Gollwitzer 的循证策略)
- **柔化语言** — AI 不说"任务创建成功",说"✓ 加了:…"

## 首次使用

⚠️ **这是模板**,所有 `base_token` / `table_id` / `field_id` / `view_id` / `workflow_id` 都是 `<PLACEHOLDER>`。必须先完成 3 步:

### Step 1 · 建你自己的 Base

按 `skills/adhd-pm/references/schema.md` 的 **4 张表结构**(Projects / Tasks / Daily Intention / Pomodoros)在飞书多维表格里搭好。字段名、select options 严格按 schema.md 来(AI 写命令会精确匹配)。

建议**保留 emoji 和名字原样**(如 `📥 Inbox`、`⚡ < 2min`),skill 内部已硬编码这些字符串。

### Step 2 · 抓 id 填 schema.md

运行 `schema.md` 末尾的 dump 脚本,会打印所有 table/field/view/workflow id。把各处 `<PLACEHOLDER>` 替换成你的真实值。

### Step 3 · 建 2 个 workflow(可选但推荐)

- `🎉 任务完成发 IM`:Tasks.状态 = ✅ Done 时给自己发庆祝消息
- `☕ 每天 9:00 问候`:定时提醒定义今日 1 件关键事

schema.md 里有 workflow 标题和触发/动作的描述,照抄即可。

## 10 种操作

| 你说 | 操作 |
|---|---|
| 加任务 / 记一下 | 建 Task(<2min 建议直接做 / XXL 建议拆) |
| 完成了 X / 搞定 | 标 ✅ Done(触发 🎉 IM) |
| 改状态 / 移到 Today | 改状态(到 Today 前柔性追问估算) |
| 今天做什么 / 早安 | 今日 brief:今日专注 + Overdue + <2min 热身 |
| 晚上了 / 晚安 | 晚间复盘:今日完成 + 未收尾 + 明日清单 |
| 看看进度 | 项目状态 + 任务分布 |
| 累了 / 没劲 | 低能量模式:只推 <2min 和 💤 低能量任务 |
| 拆一下 X | 父子任务拆解 |
| 改估算 / 推日期 | 改任务属性 |
| 贴周报 | 按 ≥3 任务 + 跨多周 规则拆到 Projects / Tasks |

## 7 条 ADHD 行为规则(Skill 内嵌)

1. ⚡ `<2min` 不建任务,直接"现在就做"
2. 不追 deadline — 允许无截止
3. 状态到 Today 前先看估算 — 柔性追问,可跳过
4. XXL 主动建议拆
5. 项目门槛 = ≥3 任务 + 跨多周
6. 严禁冷语 — 必须柔化 + 🎉
7. 多巴胺反馈必触发

## 依赖

- `lark-cli`:`npx @larksuite/cli@latest install`
- 飞书 user 身份 + 必要 scope(`base` / `space` / `calendar` 等)
- 目标 Base 已按 schema.md 搭好

## 文件结构

```
plugins/adhd-pm/
├── .claude-plugin/plugin.json
├── README.md                      ← 本文件
└── skills/adhd-pm/
    ├── SKILL.md                   ← 入口 + 触发规则 + 汇报规范
    └── references/
        ├── schema.md              ← Base 坐标模板(填自己的 id)
        └── operations.md          ← 10 操作的决策树 + 命令模板
```

## 设计来源

- ADHD 设计哲学参考:[Leantime](https://leantime.io) 的源代码实现("Built with ADHD, dyslexia and autism in mind")
- Implementation Intentions:Peter Gollwitzer 的 If-Then 计划理论
- GTD 2 分钟法则:David Allen
- 5 桶时间分块:参考 Leantime 的 My ToDos widget

## 维护

Base schema 漂移时(加字段 / 改 option):

1. 运行 `skills/adhd-pm/references/schema.md` 文末的 dump 脚本,抓当前 Base 结构
2. 手工更新 `schema.md`(替换过时的 `<PLACEHOLDER>` 映射)
3. **不要**让 AI 运行时自动 `+field-list` 探测(破坏稳定性的根本)
