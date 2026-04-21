---
name: adhd-pm
description: "ADHD 友好的个人项目管理工作流(基于飞书多维表格 Base)。用户提到加任务/关任务/改任务/查今日/查进度/早安/晚安/周报导入/Brain Dump 捕获时触发。触发词:加任务、新建任务、记一下、捕获想法、完成了、搞定、关闭任务、改状态、今天做什么、今日待办、早安、晚安、周报、看看进度、拆子任务、追日程、ADHD PM、我的 Base。不要用于无关的任务/项目讨论(如代码里的 task queue、第三方项目管理工具)。"
---

# ADHD-PM Skill · ADHD 友好的项目管理工作流

把 ADHD 友好的个人项目管理流程固化到飞书多维表格 + Claude Code Skill,目标是让 AI 在"加任务/关任务/查日程"这类高频操作上**有稳定、确定性的路径**,不再每次从零发挥。

## 🚀 主入口

```
https://<your-tenant>.feishu.cn/base/<YOUR_BASE_TOKEN>?table=<TBL_TASKS>&view=<VIEW_TASK_TODAY>
```
= ✅ Tasks 表 → 📌 今日专注视图

> 首次使用请先按 [references/schema.md](references/schema.md) 的"首次使用"流程搭好 Base 并把所有 `<PLACEHOLDER>` 替换成你自己的真实 id。

## 1. 使用流程(每次都按这个走)

```
用户消息
  ↓
① 判定意图(看下方"10 种操作速查")
  ↓
② 查 references/schema.md 拿坐标(不要去 API 查 field-list — 全部硬编码)
  ↓
③ 查 references/operations.md 的对应操作模板
  ↓
④ 按模板出 lark-cli 命令(用 --as user)
  ↓
⑤ 执行
  ↓
⑥ 按 ADHD 柔化语言汇报(见下方"汇报规范")
```

## 2. 10 种操作速查

| 用户说 | 意图码 | 见 operations.md 章节 |
|---|---|---|
| 加任务 / 记一下 / 新建 / 要做 X | `ADD_TASK` | [1. ADD_TASK](references/operations.md#1-add_task--加任务) |
| 完成了 / 搞定 / 关掉 X | `CLOSE_TASK` | [2. CLOSE_TASK](references/operations.md#2-close_task--完成任务) |
| 改状态 / 移到 Today / 开做 | `CHANGE_STATUS` | [3. CHANGE_STATUS](references/operations.md#3-change_status--改状态) |
| 今天做什么 / 早安 / brief | `TODAY_BRIEF` | [4. TODAY_BRIEF](references/operations.md#4-today_brief--今日简报) |
| 晚上了 / 收工 / 晚安 | `EVENING_REVIEW` | [5. EVENING_REVIEW](references/operations.md#5-evening_review--晚间复盘) |
| 看看进度 / 项目状态 | `PROJECT_STATUS` | [6. PROJECT_STATUS](references/operations.md#6-project_status--项目状态) |
| 累了 / 没劲 / 2min 的 | `LOW_ENERGY` | [7. LOW_ENERGY](references/operations.md#7-low_energy--低能量模式) |
| 拆一下这任务 | `SPLIT_TASK` | [8. SPLIT_TASK](references/operations.md#8-split_task--拆子任务) |
| 改估算 / 改日期 / 改能量 | `UPDATE_TASK` | [9. UPDATE_TASK](references/operations.md#9-update_task--改任务属性) |
| 贴入周报 / 同步周报 | `IMPORT_WEEKLY` | [10. IMPORT_WEEKLY](references/operations.md#10-import_weekly--周报导入) |

## 3. ADHD 核心行为规则(必须遵守)

这些是 ADHD 友好的设计原则,不是"拟人化包装" — 是真实要执行的行为约束:

1. **⚡ <2min 优先级最高** — 用户说"要做 X"且估算 ≤ 2 分钟,不要"加进去",直接"现在就做,2 分钟的事" + 等用户确认后再标 Done(不要先建任务再让用户点)。
2. **不追 deadline** — 允许无截止。状态是"🔜 Today" 且计划结束为空是合法的,不要催用户填。
3. **状态到 Today 前先看估算** — 如果从 📥 Inbox 直接拖 🔜 Today 而**没有估算字段**,柔性提示"这事大概多大?(S/M/L 选一个,或者说<2min 直接做)"。用户拒绝填也不强求,可以让它 Today。
4. **XXL 不建议** — 用户要建 XXL 任务,先问"能不能拆 2-3 条 XL?"。坚持要建也尊重,但提醒 ADHD 大脑对大块任务启动困难。
5. **项目门槛 = ≥3 任务 + 跨多周** — 用户要建"项目",先问"这事会有 ≥3 件事要做吗?会持续超过 1 周吗?"。否则直接建单 Task(可以没 `所属项目`)。
6. **柔化语言 · 严禁冷语** — 禁止说 "任务创建成功"、"已添加"、"状态更新成功"。改用:
   - 成功建任务:"✓ 加了:{标题}"
   - 完成:"🎉 完成 {标题} — 下一件?"
   - Overdue 不叫 Overdue 叫"早些时候没来得及的"
   - Done 后不要问下一件事的语气太急,用"要不要休一下"
7. **多巴胺反馈必触发** — 完成任务、完成项目、连做 3 个<2min 等时机,加 🎉 / ⚡ emoji + 一句鼓励。别省。

## 4. 汇报规范(执行完命令后怎么回用户)

**短。不罗列 API 返回。不贴 record_id 给用户看。**

模板:

| 场景 | 格式 | 例 |
|---|---|---|
| 加任务 | `✓ 加了:{标题} [{估算}] → {状态}` | `✓ 加了:回复客户邮件 [⚡ <2min] → 🔜 Today` |
| 完成 | `🎉 完成 {标题}` + 可选 `— 下一件是 {next}?` | `🎉 完成 回复客户邮件` |
| 改状态 | `{old} → {new}:{标题}` | `📥 Inbox → 🔜 Today:写方案邮件` |
| 今日 brief | 3 段(今日 N 件 / Overdue / <2min 热身)每段不超 3 条 | 见 operations.md |
| 报错 | 说人话,不贴 JSON | `没改成 — 找不到叫"xxx"的任务,你要的是哪条?` |

## 5. 查找任务的启发式(用户给关键词时)

用户常用不完整名称指代任务,比如"完成了那个评审"、"关掉邮件那条"。查找策略:

1. 先用 `+record-search --query "<关键词>"` 在 Tasks 表搜
2. 结果 = 1 条:直接执行
3. 结果 ≥ 2 条:列出让用户选(**给编号,不给 record_id**),如:
   ```
   找到 2 条:
     1. 发邮件: 方案 A (🔜 Today)
     2. 发邮件: 方案 B (🔜 Today)
   要哪个?
   ```
4. 结果 = 0:不要立刻建新的,先反问"没找到,是要新建还是你指的是?"

## 6. 识别边界(什么时候不该触发这个 skill)

- 用户在说代码里的 "task queue" / "job" / "worker" → 不是这里的任务,不要动 Base
- 用户聊第三方工具(Linear / Notion / Jira)→ 不是这里的任务
- 用户讨论理论或概念(ADHD 是什么、项目管理方法论)→ 只聊天,不操作 Base
- 用户明显在问 CLI 命令怎么写(不是要做动作) → 是 lark-base skill 的事

遇到不确定的,**宁可问一句"是在说你的 ADHD PM Base 吗?"也不要直接动 Base**。

## 7. 前置 & 依赖

- lark-cli 已安装(`npx @larksuite/cli@latest install`)
- 用户的飞书 user 身份已认证,scope 已覆盖(空间+任务+事件等)
- 本 skill 不依赖 lark-shared(已内化所需约束);但如遇 permission 错误,参考 lark-shared 的权限流程
- 所有 base/table/field id **必须**硬编码在 [references/schema.md](references/schema.md),**不要调用 +field-list / +table-list 去查**(稳定性的根本 — 每次都查容易慢或拿到新字段出错)
- 首次使用前,必须按 [references/schema.md](references/schema.md) 的"首次使用"流程把 `<PLACEHOLDER>` 全部替换成真实 id

## 8. Schema 漂移时怎么办

如果用户新加/改了字段而 schema.md 没同步,命令会失败(字段名/选项不存在)。处理:

1. 遇到 "field not found" / "option not valid" 错误 → 停下来告诉用户:"schema 可能漂移了,要我更新 schema.md 吗?"
2. 不要悄悄 fallback 去查 API(那就破坏了稳定性约束)
3. 用户确认后,执行 `+field-list` 抓最新结构,更新 [references/schema.md](references/schema.md),再重试

## 参考

- [references/schema.md](references/schema.md) — 完整 Base 坐标(base/table/field id + select options + view id)
- [references/operations.md](references/operations.md) — 10 种操作的 CLI 命令模板 + 交互细节
- 上游 lark-base skill: `~/.claude/skills/lark-base/SKILL.md`(底层 CLI 能力,本 skill 是其个人化封装)
