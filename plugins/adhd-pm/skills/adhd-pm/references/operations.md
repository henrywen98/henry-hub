# ADHD-PM 10 种操作 · Command Playbook

> 每个操作都有固定命令模板。不要临场发挥。  
> 所有命令以 `--as user` 执行。base_token 从 `schema.md` 取。  
> 常量用 `$BASE` / `$TASKS` / `$PROJ` / `$DI` / `$POMO` 代表(见 schema.md)

```bash
BASE="<YOUR_BASE_TOKEN>"
TASKS="<TBL_TASKS>"
PROJ="<TBL_PROJECTS>"
DI="<TBL_DAILY>"
POMO="<TBL_POMODORO>"
```

---

## 1. ADD_TASK · 加任务

### 触发
- "加任务" / "记一下" / "新建任务" / "要做 X" / "把 X 加进去" / "待办:X"
- 冒出想法想捕获(Brain Dump 语义)

### 决策树

```
用户说"要做 X"
  ↓
① 估算有无线索?
    - "2 分钟能搞" / "很快" / "一下子" → 估算 = ⚡ < 2min
    - "一两天" → L; "半天" → M; "很小事" → S
    - 没线索 → 不主动问,默认不填(允许空)
  ↓
② 估算是 ⚡ < 2min?
    是 → 不建任务,先说:"2 分钟的事 — 现在就做,做完告诉我再记。" 等用户反馈
    否 → 继续 ③
  ↓
③ 估算 XXL?
    是 → 不建,说:"一周+的事建议拆 2-3 条 XL — 大脑对大块启动困难。要我帮你拆吗?"
    否 → 继续 ④
  ↓
④ 状态:用户说"今天要做"=🔜 Today;否则 📥 Inbox
  ↓
⑤ 所属项目:用关键词匹配 schema.md 里维护的"常驻项目速查"表
           无匹配 = 空
  ↓
⑥ 能量需求(可选):"累" → 💤 低;"难" / "需要专注" → 🔋 高;其它 → 空
  ↓
⑦ If-Then:如果用户说了"如果…就…" 模式,填进 If-Then 触发
  ↓
⑧ 执行命令 → 汇报
```

### 命令模板

```bash
lark-cli --as user base +record-batch-create --base-token "$BASE" --table-id "$TASKS" --json '{
  "fields":["标题","状态","估算","能量需求","计划结束","If-Then 触发","所属项目"],
  "rows":[["<标题>","<状态>","<估算或null>","<能量或null>","<YYYY-MM-DD HH:mm:ss 或 null>","<If-Then 或 \"\">",<link 数组或 []>]]
}'
```

**link 字段格式**:
- 有项目:`[{"id":"<rec_PROJ_X>"}]`(从 schema.md 常驻项目速查找 record_id)
- 无项目:`[]`

### 汇报

```
✓ 加了:{标题} [{估算}] → {状态}
```

例:`✓ 加了:写 Q2 OKR 草稿 [M] → 📥 Inbox`

---

## 2. CLOSE_TASK · 完成任务

### 触发
- "完成了 X" / "搞定 X" / "关掉 X" / "做完 X 了"

### 决策树

```
① 搜 X 定位任务
   lark-cli --as user base +record-search --base-token "$BASE" --table-id "$TASKS" \
     --query "<关键词>" --limit 5
  ↓
② 结果处理:
   - 1 条 → 用 record_id 直接更新
   - ≥ 2 条 → 列编号让用户选
   - 0 条 → 反问"没找到,你指的是?"
  ↓
③ 更新状态 = ✅ Done(会自动触发 IM workflow)
  ↓
④ 汇报 🎉
```

### 命令模板

```bash
lark-cli --as user base +record-batch-update --base-token "$BASE" --table-id "$TASKS" --json '{
  "record_id_list":["<rec_id>"],
  "patch":{"状态":"✅ Done"}
}'
```

### 汇报

```
🎉 完成 {标题}
```

如果用户连续完成 3 个以上,加一句鼓励:"今天节奏不错 ⚡"

---

## 3. CHANGE_STATUS · 改状态

### 触发
- "把 X 放到 Today" / "X 开做了" / "X 先搁置"
- "开始做 X" → 🏃 Doing

### 状态映射(用户口语 → 官方 option)

| 用户口语 | 目标状态 |
|---|---|
| "开做了" / "开始做" / "在做" | 🏃 Doing |
| "今天做" / "放 Today" | 🔜 Today |
| "先放一放" / "搁置" / "以后再说" | 🧊 Later |
| "收回 Inbox" / "不确定了" | 📥 Inbox |
| "做完了" / "完成了" → 用 CLOSE_TASK 操作 | — |

### 特殊规则(ADHD 保护)

- 📥 Inbox → 🔜 Today 时,**如果没估算字段**:柔性提示"这事大概多大?(S/M/L 选一个,或者说 <2min 直接做)"。用户忽略也不强迫,可以让它 Today。
- 🏃 Doing → 📥 Inbox(回退):正常,不需要追问
- ✅ Done → 任何非 Done:说 "重开 {标题}?改成 {新状态} 了"

### 命令模板

同 CLOSE_TASK 的 batch-update,把 patch.状态 改成目标值。

### 汇报

```
{old icon} → {new icon} : {标题}
```

---

## 4. TODAY_BRIEF · 今日简报

### 触发
- "今天做什么" / "今日待办" / "早安" / "帮我 brief 下" / "今天的事"

### 决策树

```
并行读 3 组数据:
  ① 📌 今日专注视图 (Tasks)
  ② ⏰ Overdue 视图 (Tasks)
  ③ 🥇 快速启动 (<2min) 视图 (Tasks)
并额外读:
  ④ Daily Intention 今天那条(若有)
  ↓
组合成 3 段汇报
```

### 命令模板

```bash
# 读某视图的所有记录
lark-cli --as user base +record-list --base-token "$BASE" --table-id "$TASKS" \
  --view-id <view_id> --limit 50

# 关键 view_id(从 schema.md 取):
#   📌 今日专注 = <VIEW_TASK_TODAY>
#   ⏰ Overdue = <VIEW_TASK_OVERDUE>
#   🥇 快速启动 = <VIEW_TASK_QUICKSTART>
```

### 汇报模板

```
☕ {问候}

📌 今日专注({N} 件):
  • {标题} [估算] {能量}
  • ...
  (最多列 5 条,更多说 "还有 N 件")

⏰ 早些时候没来得及的({M} 件):
  (只列前 3 条,没有的话跳过整段)

🥇 热身用的 <2min({K} 件,随手做):
  (列所有,最多 5 条)

{如果 DI 有今天记录:} 🧭 今日关键事:{link 的 task 标题}
{如果 DI 无:} 还没定义今日关键事 — 要不要现在想一件?
```

**问候轮换**:早 / 新的一天 / 今天也辛苦了(依时间)

**不要说**:"以下是今日任务清单"(冷语)

---

## 5. EVENING_REVIEW · 晚间复盘

### 触发
- "晚上了" / "收工" / "晚安" / "今天结束" / "回顾一下今天"

### 决策树

```
读 3 组:
  ① Tasks 中今天 updated 且 状态=✅ Done 的(今日完成)
     — 筛选条件复杂,直接列所有 Done 然后按 最后更新 = 今天过滤
  ② Tasks 状态=🏃 Doing(没收尾的)
  ③ Tasks 状态=🔜 Today AND 计划结束 = today 或 tomorrow
```

### 汇报

```
🌙 今天:

🎉 完成 {N} 件:
  • {标题}
  ...

🏃 还在做的({M} 件):
  • {标题} — 是收尾还是明天接?
  ...

🔜 明天的({K} 件):
  • {标题}
  ...

今天 1 件学到的?(晚间反思)
今天感觉:🌟 充实 / 😐 还行 / 😩 挣扎?
```

如果用户答了反思/自评,写回 DI 今天那条记录:

```bash
# 先找今天的 DI 记录(或创建)
# 用 record-search --query <yyyy-MM-dd>
# 然后 batch-update 加 晚间反思 / 自评
```

---

## 6. PROJECT_STATUS · 项目状态

### 触发
- "看看进度" / "项目状态" / "<某项目名>怎么样" / "<某项目名>的进展"

### 决策树

```
① 用户指定项目? → 读该项目
② 没指定 → 列所有 🚀 进行中 项目
  ↓
③ 对每个项目输出:
   - 名字 / 状态 / 进度 %
   - 关联任务按状态分组列
   - 是否有 Overdue 任务(高亮警示)
   - 下一步(第一个非 Done 任务)
```

### 命令模板

```bash
# 所有进行中项目
lark-cli --as user base +record-list --base-token "$BASE" --table-id "$PROJ" \
  --view-id <VIEW_PROJ_ACTIVE> --limit 20

# 单项目:先搜名字拿 record_id, 然后
lark-cli --as user base +record-get --base-token "$BASE" --table-id "$PROJ" \
  --record-id <rec_id>
```

### 汇报

```
🚀 {项目名} · 进度 {X}%
  Why: {为什么做这个}
  
  任务({N}):
    ✅ Done {a}: {标题}...
    🏃 Doing {b}: {标题}...
    🔜 Today {c}: {标题}...
    📥 Inbox {d}
    🧊 Later {e}
  
  下一步:{非 Done 的第一个 task}
  
  {如果有 Overdue} ⚠️ 注意:{M} 件早些没完成的任务
```

---

## 7. LOW_ENERGY · 低能量模式

### 触发
- "累" / "没劲" / "打不起精神" / "脑子不转" / "只想做 2min 的"

### 决策树

```
① 读 🥇 快速启动 视图(已 filter <2min + 未完成)
② 读 能量需求 = 💤 低 的任务
合并去重,列出来
```

### 命令模板

```bash
lark-cli --as user base +record-list --base-token "$BASE" --table-id "$TASKS" \
  --view-id <VIEW_TASK_QUICKSTART> --limit 20
```

### 汇报

```
🪫 低能量也能干的({N} 件):

  ⚡ <2min 的:
    • {标题}
    ...
  
  💤 低能量:
    • {标题}
    ...

挑一件最轻松的开干 — 启动后惯性就来了 🧠
```

---

## 8. SPLIT_TASK · 拆子任务

### 触发
- "拆一下 X" / "X 太大了分几步" / "给我分解下"

### 决策树

```
① 找到父任务 X(搜索 + 选一)
② 向用户提议拆分清单(AI 主动给 2-5 条建议)
③ 用户确认/修改
④ 批量建子任务,每条的 父任务 字段 = X 的 record_id
⑤ 改父任务估算(如果拆完能算出更准确估算)
```

### 命令模板

```bash
lark-cli --as user base +record-batch-create --base-token "$BASE" --table-id "$TASKS" --json '{
  "fields":["标题","状态","估算","父任务","所属项目"],
  "rows":[
    ["{子任务1}","📥 Inbox","S",[{"id":"<父 record_id>"}],<父任务的所属项目数组>],
    ["{子任务2}","📥 Inbox","S",[{"id":"<父 record_id>"}],<...>]
  ]
}'
```

### 汇报

```
✓ 拆了 {父标题} → {N} 子任务:
  • {子1} [S]
  • {子2} [M]
  ...
父任务保留,你想什么时候推哪个都行
```

---

## 9. UPDATE_TASK · 改任务属性

### 触发
- "X 改成 L" / "X 推到明天" / "X 改高能量"

### 字段映射

| 用户口语 | 改什么字段 |
|---|---|
| "改估算为 L" | 估算 = "L" |
| "推到明天" / "改日期" | 计划结束 = `<YYYY-MM-DD> 18:00:00` |
| "高能量" / "低能量" | 能量需求 |
| "关联到 <项目名>" | 所属项目 = `[{"id":"<rec_PROJ_X>"}]` |
| "加一条 If-Then:..." | If-Then 触发 = "..." |

### 命令模板

```bash
lark-cli --as user base +record-batch-update --base-token "$BASE" --table-id "$TASKS" --json '{
  "record_id_list":["<rec_id>"],
  "patch":{"<字段名>":<值>}
}'
```

### 汇报

```
✓ {标题}:{字段} → {新值}
```

---

## 10. IMPORT_WEEKLY · 周报导入

### 触发
- 用户贴入周报文本(有明显段落结构如"上周完成/本周计划/阻塞")
- "帮我把这周报拆进去" / "同步周报"

### 决策树

```
① 解析周报结构,识别:
   - 已完成事项 → Tasks, 状态=✅ Done
   - 在做/本周计划 → Tasks, 状态=🏃 Doing 或 🔜 Today
   - 阻塞 → Tasks 标注 + If-Then 触发 = 阻塞条件
   - 大目标(≥3 子事项 + 跨多周) → Projects
  ↓
② 按"项目门槛规则"(≥3 任务 + 跨多周)判定:
   - 满足 → 建 Project 并挂任务
   - 不满足 → 只建任务,不建项目
  ↓
③ 跟用户确认拆分方案(不要直接写入)
  ↓
④ 确认后 batch create
```

### 汇报(导入前确认)

```
我准备这么拆周报:

🚀 新项目({N} 个):
  • {项目名} ({X} 任务)
  • ...

✅ 独立任务({M} 条):
  • {标题} | {状态} | {估算}
  • ...

有问题吗?确认就写入。
```

### 命令模板

依次 batch-create Projects(若有)→ batch-create Tasks(带 所属项目 link)→ batch-update 回填 Projects.关联任务

---

## 附录 A · 常见错误恢复

| 错误 | 原因 | 恢复 |
|---|---|---|
| `field not found` | schema.md 过期 | 停下来告知用户,按 schema.md 文末脚本 dump 最新结构并更新 |
| `option not valid` | select option 错拼(emoji/空格不对) | 严格按 schema.md 的字符串复制粘贴 |
| `record not found` | 搜不到目标任务 | 用 +record-search 搜关键词,列结果让用户选 |
| `permission denied` | scope 不全 | 参考 lark-shared skill 处理,不要自己建尝试 |
| link 字段传错 | 用了 JSON 字符串而不是真数组 | 必须是 `[{"id":"..."}]` JSON array,不能是字符串化版本 |
| 所有 `<PLACEHOLDER>` 没替换 | 没做首次 schema.md 填充 | 按 schema.md 的"首次使用"流程把所有 id 填进去 |

## 附录 B · 禁止项

- ❌ 不要去 `+field-list` / `+table-list` 查结构(schema.md 已硬编码)
- ❌ 不要建新表(需要时用户会明确说)
- ❌ 不要删字段/视图/workflow(破坏性,需显式授权)
- ❌ 不要批量 `--yes` 超过 3 条记录(逐条确认)
- ❌ 不要贴 record_id / field_id 给用户(纯内部数据)
- ❌ 不要用 Overdue / Deadline 字眼 — 改用 "早些时候" / "计划结束"
- ❌ 不要在完成任务时冷冰冰说 "已完成" — 必须有 🎉 和鼓励

## 附录 C · 时间处理约定

| 用户说 | 转换为 |
|---|---|
| "今天" | `YYYY-MM-DD 18:00:00`(当天下班) |
| "明天" | `(tomorrow) 18:00:00` |
| "本周" / "这周" | `(周五) 18:00:00` |
| "下周" | `(下周五) 18:00:00` |
| "月底" | `(本月最后一天) 18:00:00` |
| 具体日期 | `<YYYY-MM-DD> 18:00:00` |

(默认 18:00 下班时间作为截止;用户明确说时间则保留)
