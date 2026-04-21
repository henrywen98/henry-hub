# ADHD-PM Base Schema · 硬编码坐标模板

> 本文件是**通用架构模板**。使用前必须按自己的飞书 Base 填入真实 id。  
> 关键稳定性约束:**填完后,禁止 AI 运行时用 `+field-list` / `+table-list` 去查结构** — 硬编码 id 是 skill 稳定的根本。  
> schema 漂移(加字段/改 option)时,回来更新本文件,不要让 AI 自动探测。

## 📝 首次使用:自建 Base + 抓 id

### Step 1 · 建 Base

用飞书多维表格搭 4 张表(字段结构见本文下方各表定义):

1. 📁 Projects
2. ✅ Tasks
3. 🧭 Daily Intention
4. 🍅 Pomodoros(可选)

可以参考 `skills/adhd-pm/SKILL.md` 的设计哲学,按每张表的字段列表逐个建。也可以用 `lark-cli` 按字段表一次性建好。

### Step 2 · 抓所有 id 填到本文件

建完后运行本文件**末尾**的 dump 脚本,它会输出所有 table/field/view/workflow id。把各处 `<PLACEHOLDER>` 替换成真实值。

## Base

| 项 | 值 |
|---|---|
| 名称 | `🧠 ADHD-Friendly PM`(可自行改) |
| base_token | `<YOUR_BASE_TOKEN>` |
| URL | `https://<your-tenant>.feishu.cn/base/<YOUR_BASE_TOKEN>` |
| Time zone | Asia/Shanghai(按需改) |
| 所有者 open_id | `<YOUR_OPEN_ID>`(通过 `lark-cli contact +get-user` 拿) |

## Tables · 速查

| 表名 | table_id | 用途 |
|---|---|---|
| 📁 Projects | `<TBL_PROJECTS>` | 大项目(≥3 任务 + 跨多周才进) |
| ✅ Tasks | `<TBL_TASKS>` | **主战场**(一切具体要做的事) |
| 🧭 Daily Intention | `<TBL_DAILY>` | 每日意图 · 今日 1 件关键事 |
| 🍅 Pomodoros | `<TBL_POMODORO>` | 番茄钟记录(可选) |

---

## 📁 Projects 表结构

### 字段

| 字段名 | field_id | type | 备注 |
|---|---|---|---|
| 项目名 | `<FLD_PROJ_NAME>` | text | **主列** · 必填 |
| 状态 | `<FLD_PROJ_STATUS>` | select(单选) | 见 options |
| 为什么做这个 | `<FLD_PROJ_WHY>` | text | ADHD 动机外化 |
| Canvas / 策略 | `<FLD_PROJ_CANVAS>` | text | Lean Canvas / SWOT |
| 计划开始 | `<FLD_PROJ_START>` | datetime | |
| 计划结束 | `<FLD_PROJ_END>` | datetime | |
| 关联任务 | `<FLD_PROJ_TASKS>` | link → Tasks | 单向 |
| 进度 | `<FLD_PROJ_PROGRESS>` | formula | **只读** · `COUNTIF(完成任务)/COUNTA(全部任务)` |
| 完成庆祝图 | `<FLD_PROJ_CELEBRATE>` | attachment | **只读**(走 `+record-upload-attachment`) |

### 状态 options

```
📥 构思  /  🚀 进行中  /  ⏸ 暂停  /  ✅ 完成  /  🗄 归档
```

### 视图

| view_id | 名字 | type | 筛选 |
|---|---|---|---|
| `<VIEW_PROJ_GRID>` | Grid View | grid | 默认全量 |
| `<VIEW_PROJ_ACTIVE>` | 🚀 进行中 | grid | 状态 = 🚀 进行中 |
| `<VIEW_PROJ_POOL>` | 📥 构思池 | grid | 状态 = 📥 构思 |
| `<VIEW_PROJ_HONOR>` | ✅ 荣誉墙 | kanban | 状态 = ✅ 完成,按结束日期降序 |
| `<VIEW_PROJ_GANTT>` | 📊 甘特 | gantt | 时间线 |

### 常驻项目速查(可选)

如你有固定长期项目,可维护它们的 record_id 做稳定引用:

```
<项目 A 名>: <rec_PROJ_A>
<项目 B 名>: <rec_PROJ_B>
```

> 💡 新项目 record_id 动态生成,可用 `+record-search` 动态定位。

---

## ✅ Tasks 表结构(主战场)

### 字段

| 字段名 | field_id | type | 备注 |
|---|---|---|---|
| 标题 | `<FLD_TASK_TITLE>` | text | **主列** · 必填 |
| 状态 | `<FLD_TASK_STATUS>` | select(单选) | 见 options |
| 估算 | `<FLD_TASK_EFFORT>` | select(单选) | GTD 2min 法则,见 options |
| 能量需求 | `<FLD_TASK_ENERGY>` | select(单选) | 匹配自己状态 |
| 计划开始 | `<FLD_TASK_START>` | datetime | 可空 |
| 计划结束 | `<FLD_TASK_END>` | datetime | 可空(不强制 deadline) |
| If-Then 触发 | `<FLD_TASK_IFTHEN>` | text | Implementation Intentions |
| 番茄钟数 | `<FLD_TASK_POMODORO>` | number | |
| 情绪反应 | `<FLD_TASK_REACTION>` | select(多选) | 见 options |
| 最后更新 | `<FLD_TASK_UPDATED>` | updated_at | **只读**系统字段 |
| 🎉 完成日期 | `<FLD_TASK_DONE_AT>` | formula | **只读** |
| 所属项目 | `<FLD_TASK_PROJECT>` | link → Projects | 可空 |
| 父任务 | `<FLD_TASK_PARENT>` | link → Tasks(self) | 拆子任务用 |

### 状态 options

```
📥 Inbox  /  🔜 Today  /  🏃 Doing  /  ✅ Done  /  🧊 Later
```

- 新建默认:`📥 Inbox`
- 用户说"今天要做":`🔜 Today`
- 正在进行:`🏃 Doing`
- 完成:`✅ Done`(建议触发 🎉 IM workflow)
- 搁置/以后再说:`🧊 Later`

### 估算 options(GTD 编码 · ADHD 核心)

```
⚡ < 2min  /  XS  /  S  /  M  /  L  /  XL  /  XXL
```

- `⚡ < 2min` = 2 分钟内搞定 → **别建任务,直接做**
- XS-S = 10-30 分钟
- M = 0.5-1 天
- L = 1-2 天
- XL = 3-5 天
- XXL = 一周+(**建议拆,不要建**)

### 能量需求 options

```
🔋 高  /  🪫 中  /  💤 低
```

### 情绪反应 options(多选)

```
👍 Like  /  🎉 Celebrate  /  💡 Insight  /  💯 Support  /  😡 Anger  /  😥 Sad
```

### 视图(有 filter/sort 预设)

| view_id | 名字 | type | filter 概要 |
|---|---|---|---|
| `<VIEW_TASK_GRID>` | Grid View | grid | 全量 |
| `<VIEW_TASK_TODAY>` | 📌 今日专注 | grid | 状态 ∈ [🔜 Today, 🏃 Doing] |
| `<VIEW_TASK_OVERDUE>` | ⏰ Overdue | grid | 计划结束 < Today AND 状态 ≠ ✅ Done |
| `<VIEW_TASK_QUICKSTART>` | 🥇 快速启动 (<2min) | grid | 估算 = ⚡ < 2min AND 状态 ≠ ✅ Done |
| `<VIEW_TASK_NODUEDATE>` | 🌫 无截止 | grid | 计划结束 empty AND 状态 ≠ ✅ Done |
| `<VIEW_TASK_BYENERGY>` | 🔋 按能量分组 | grid | 状态 ≠ ✅ Done, group by 能量需求 |
| `<VIEW_TASK_HONOR>` | ✅ 荣誉墙 | kanban | 状态 = ✅ Done |
| `<VIEW_TASK_GANTT>` | 📊 甘特 | gantt | 时间线 |
| `<VIEW_TASK_CAL>` | 📅 日历 | calendar | 按计划结束 |

---

## 🧭 Daily Intention 表结构

### 字段

| 字段名 | field_id | type | 备注 |
|---|---|---|---|
| 概要 | `<FLD_DI_SUMMARY>` | formula | **主列 · 只读** (`日期 — 今日 1 件关键事`) |
| 日期 | `<FLD_DI_DATE>` | datetime | 每天一条 |
| If-Then 计划 | `<FLD_DI_IFTHEN>` | text | 今天的 Implementation Intentions |
| 今日 1 件关键事 | `<FLD_DI_KEYTASK>` | link → Tasks | **ADHD 核心 · 入职第一屏原则** |
| 今日能量 | `<FLD_DI_ENERGY>` | number(rating,闪电 1-5) | |
| 自评 | `<FLD_DI_SELFRATE>` | select(单选) | 见 options |
| 晚间反思 | `<FLD_DI_REFLECT>` | text | 3 件顺利 + 1 件学到 |

### 自评 options

```
🌟 充实  /  😐 还行  /  😩 挣扎
```

### 视图

| view_id | 名字 | type |
|---|---|---|
| `<VIEW_DI_GRID>` | Grid View | grid |
| `<VIEW_DI_CAL>` | 📆 日历 | calendar |
| `<VIEW_DI_HISTORY>` | 📜 历史 | grid(按日期降序) |

---

## 🍅 Pomodoros 表结构(可选)

### 字段

| 字段名 | field_id | type |
|---|---|---|
| 做什么 | `<FLD_POMO_WHAT>` | text(**主列**) |
| 开始时间 | `<FLD_POMO_START>` | datetime |
| 时长(分) | `<FLD_POMO_DURATION>` | number |
| 完成 | `<FLD_POMO_DONE>` | checkbox |
| 关联任务 | `<FLD_POMO_TASK>` | link → Tasks |

---

## Dashboard(可选)

| 项 | 值 |
|---|---|
| 名称 | 🧠 ADHD 掌控中心 |
| dashboard_id | `<DASHBOARD_ID>` |

建议 block 配置(9 个):顶部 Markdown 提醒 / 🏃 在做 / 🔜 今日 / ⚡ <2min / 🎉 已完成 / 🔥 任务状态分布(pie) / 🔋 待办能量分布(column) / 📏 任务大小分布(column) / 📁 项目状态(pie)

## Workflows(均建议 enable)

| workflow_id | 标题 | 触发 | 动作 |
|---|---|---|---|
| `<WKF_DONE_IM>` | 🎉 任务完成发庆祝 IM | Tasks.状态 = ✅ Done | LarkMessage 给自己 |
| `<WKF_DAILY_GREETING>` | ☕ 每天 9:00 问候 & 定义今日 1 件事 | DAILY 09:00 | LarkMessage + 按钮直达 DI 表 |

## 常用 URL 速查

```
主入口(📌 今日专注):
  https://<your-tenant>.feishu.cn/base/<YOUR_BASE_TOKEN>?table=<TBL_TASKS>&view=<VIEW_TASK_TODAY>

⚡ 快速启动 (<2min):
  https://<your-tenant>.feishu.cn/base/<YOUR_BASE_TOKEN>?table=<TBL_TASKS>&view=<VIEW_TASK_QUICKSTART>

🧭 Daily Intention:
  https://<your-tenant>.feishu.cn/base/<YOUR_BASE_TOKEN>?table=<TBL_DAILY>

📊 Dashboard:
  https://<your-tenant>.feishu.cn/base/<YOUR_BASE_TOKEN>?table=<DASHBOARD_ID>
```

## 字段值格式速查(写记录时必遵守)

| 类型 | 格式 | 例 |
|---|---|---|
| text | 字符串 | `"写周报草稿"` |
| datetime | `YYYY-MM-DD HH:mm:ss` | `"2026-04-24 18:00:00"` |
| select 单选 | 字符串(option name) | `"🔜 Today"` |
| select 多选 | 字符串数组 | `["🎉 Celebrate","💡 Insight"]` |
| number | 数字 | `3` |
| checkbox | 布尔 | `true` |
| link | 对象数组 | `[{"id":"rec_xxx"}]`(必须是真数组,不是 JSON 字符串) |
| formula / updated_at / attachment | **不写入** | 跳过 |

## 维护脚本(首次填 id + schema 漂移时用)

把建好 Base 的 token 填进 `BASE` 变量,运行脚本 dump 所有 id:

```bash
BASE="<YOUR_BASE_TOKEN>"

echo "=== 基础信息 ==="
lark-cli --as user contact +get-user -q '.data.user | {name, open_id, tenant_key}'

echo ""
echo "=== 所有表 ==="
lark-cli --as user base +table-list --base-token "$BASE" -q '.data.tables | map({name, id})'

echo ""
echo "=== 每张表的字段 ==="
for TID in $(lark-cli --as user base +table-list --base-token "$BASE" -q '.data.tables[].id' 2>/dev/null); do
  echo "--- table $TID ---"
  lark-cli --as user base +field-list --base-token "$BASE" --table-id "$TID" | \
    python3 -c "
import json,sys
d=json.load(sys.stdin)
for f in d['data']['fields']:
    line = f\"  {f['id']} | {f['name']} | {f['type']}\"
    if f['type']=='select':
        opts = [o['name'] for o in f.get('options',[])]
        line += f' | opts={opts}'
    print(line)"
done

echo ""
echo "=== 每张表的视图 ==="
for TID in $(lark-cli --as user base +table-list --base-token "$BASE" -q '.data.tables[].id' 2>/dev/null); do
  echo "--- table $TID ---"
  lark-cli --as user base +view-list --base-token "$BASE" --table-id "$TID" -q '.data.views | map({id, name, type})'
done

echo ""
echo "=== Workflows ==="
lark-cli --as user base +workflow-list --base-token "$BASE" -q '.data.items | map({workflow_id, title, status})'

echo ""
echo "=== Dashboards ==="
lark-cli --as user base +dashboard-list --base-token "$BASE" -q '.data.dashboards | map({dashboard_id, name})'
```

拿到输出后,手工更新本文件里的 `<PLACEHOLDER>` 为真实 id。
