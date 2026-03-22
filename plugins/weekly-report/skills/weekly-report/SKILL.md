---
name: weekly-report
description: 周报生成工具。从 Claude Code 的聊天记录、会话元数据和项目活动中自动提取本周工作内容，分类汇总后生成面向领导的会议周报。当用户提到"周报"、"生成周报"、"本周总结"、"工作汇报"、"weekly report"、"上周做了什么"、"这周干了什么"时触发。支持自定义时间范围（默认当前自然周，周一至周日）。
---

# 周报生成（Weekly Report）

从 Claude Code 聊天记录中自动提取工作数据，生成面向领导汇报的会议周报。

## 整体流程

```
参数解析 → 数据采集(并行) → 分析分类 → 用户确认 → 生成报告 → 用户审阅
```

---

## Phase 1: 参数解析

从用户输入中提取时间范围。**中国习惯：周一是一周的开始**。

| 用户输入 | 解析规则 |
|----------|----------|
| 无指定 / "本周" | 本周一 00:00 ~ 今天 |
| "上周" | 上周一 ~ 上周日 |
| 具体日期如 "3/10-3/16" | 按指定范围 |
| "最近两周" | 两周前的周一 ~ 今天 |

用 Bash 计算精确的日期范围（注意 macOS `date` 语法）：

```bash
# 获取本周一的日期（中国周一起始）
python3 -c "
from datetime import date, timedelta
today = date.today()
monday = today - timedelta(days=today.weekday())  # weekday(): Mon=0
print(f'周一: {monday}')
print(f'今天: {today}')
print(f'monday_ts: {int(monday.strftime(\"%s\")) * 1000}')
print(f'today_ts: {int((today + timedelta(days=1)).strftime(\"%s\")) * 1000}')
"
```

得到 `start_ts` 和 `end_ts`（毫秒时间戳），后续筛选数据用。

---

## Phase 2: 数据采集（三波多 Agent 架构）

采用 **三波采集 + 交叉校验** 架构，确保大信息量场景下不遗漏。

### 总体架构

```
Wave 1: 原始数据提取（3 Agents 并行）
  ├── Agent A: history.jsonl → 项目列表 + 命令统计
  ├── Agent B: session-meta → 会话统计 + first_prompt
  └── Agent C: 活跃目录扫描 → git log + 文件变动
         ↓ 合并得到「项目全集」
Wave 2: 按项目深入分析（N Agents 并行，每个负责 2-3 个项目）
  ├── Agent D: 项目群 1 的 git/文档/memory 深入分析
  ├── Agent E: 项目群 2 的 git/文档/memory 深入分析
  └── Agent F: 项目群 3 的 git/文档/memory 深入分析
         ↓
Wave 3: 交叉校验（1 Agent）
  └── Agent G: 合并 + 去重 + 补漏 + 分类
```

### Wave 1: 原始数据提取（并行启动 3 个 Explore Agent）

这三个 Agent 使用 Python 脚本做数据提取，**脚本保证遍历完整数据**，不受上下文窗口限制。

#### Agent A: 聊天记录提取

读取 `~/.claude/history.jsonl`（JSONL 格式，每行一个 JSON 对象）：

```json
{"display":"用户输入内容","timestamp":1742000000000,"project":"/Users/.../项目路径","sessionId":"uuid"}
```

用 Python 脚本完整遍历文件，按时间戳筛选后输出：
1. 按 `project` 分组的命令数统计（降序）
2. 每个项目的全部 `display` 内容（取前 20 条，每条截取前 150 字符，确保信息量）
3. 按天统计的命令数分布
4. 按 `sessionId` 统计的独立会话数

```bash
python3 << 'PYEOF'
import json, os
from datetime import datetime, date, timedelta
from collections import defaultdict

START_TS = $START_TS   # 替换为 Phase 1 计算的值
END_TS = $END_TS

projects = defaultdict(lambda: {"count": 0, "samples": [], "sessions": set(), "days": set()})

with open(os.path.expanduser("~/.claude/history.jsonl")) as f:
    for line in f:
        try:
            r = json.loads(line.strip())
            ts = r.get("timestamp", 0)
            if START_TS <= ts < END_TS:
                p = r.get("project", "unknown")
                projects[p]["count"] += 1
                projects[p]["sessions"].add(r.get("sessionId", ""))
                projects[p]["days"].add(datetime.fromtimestamp(ts / 1000).strftime("%m/%d"))
                if len(projects[p]["samples"]) < 20:
                    projects[p]["samples"].append(r.get("display", "")[:150])
        except:
            pass

# 输出完整统计
total_cmds = sum(p["count"] for p in projects.values())
total_sessions = len(set().union(*(p["sessions"] for p in projects.values())))
print(f"=== 总计: {total_cmds} 条命令, {total_sessions} 个会话, {len(projects)} 个项目 ===\n")

for path, data in sorted(projects.items(), key=lambda x: -x[1]["count"]):
    days_str = ", ".join(sorted(data["days"]))
    print(f"\n## {path}")
    print(f"   命令数: {data['count']} | 会话数: {len(data['sessions'])} | 活跃日: {days_str}")
    for i, s in enumerate(data["samples"]):
        print(f"   [{i+1}] {s}")
PYEOF
```

#### Agent B: 会话元数据提取

读取 `~/.claude/usage-data/session-meta/` 目录下的 JSON 文件，每个文件包含一个会话：

```json
{
  "session_id": "uuid", "project_path": "/path", "start_time": "2026-03-16T...",
  "duration_minutes": 12.5, "user_message_count": 8,
  "tool_counts": {"Read": 5, "Edit": 3}, "languages": ["python"],
  "lines_added": 150, "lines_removed": 30, "files_modified": 5,
  "first_prompt": "帮我..."
}
```

用 Python 脚本完整扫描目录：
1. 按 `start_time` 筛选本周会话
2. 按项目分组统计（时长、代码行数、文件修改数）
3. 提取所有 `first_prompt`（这是判断工作内容的关键线索）
4. 汇总全局统计数据

```bash
python3 << 'PYEOF'
import json, os, glob
from datetime import datetime
from collections import defaultdict

START_DATE = "$START_DATE"  # YYYY-MM-DD 格式
END_DATE = "$END_DATE"

meta_dir = os.path.expanduser("~/.claude/usage-data/session-meta/")
projects = defaultdict(lambda: {
    "sessions": 0, "duration": 0, "lines_added": 0, "lines_removed": 0,
    "files_modified": 0, "messages": 0, "first_prompts": []
})

total = {"sessions": 0, "duration": 0, "lines_added": 0, "lines_removed": 0, "files_modified": 0}

for f in glob.glob(os.path.join(meta_dir, "*.json")):
    try:
        with open(f) as fh:
            d = json.load(fh)
        st = d.get("start_time", "")[:10]
        if START_DATE <= st <= END_DATE:
            p = d.get("project_path", "unknown")
            proj = projects[p]
            proj["sessions"] += 1
            proj["duration"] += d.get("duration_minutes", 0)
            proj["lines_added"] += d.get("lines_added", 0)
            proj["lines_removed"] += d.get("lines_removed", 0)
            proj["files_modified"] += d.get("files_modified", 0)
            proj["messages"] += d.get("user_message_count", 0)
            fp = d.get("first_prompt", "")
            if fp and len(proj["first_prompts"]) < 15:
                proj["first_prompts"].append(fp[:200])
            for k in total:
                total[k] += d.get(k if k != "sessions" else "___", 0)
            total["sessions"] += 1
    except:
        pass

print(f"=== 全局统计 ===")
print(f"会话数: {total['sessions']}")
print(f"总时长: {total['duration']:.1f} 分钟 ({total['duration']/60:.1f} 小时)")
print(f"新增代码: {total['lines_added']} 行 | 删除: {total['lines_removed']} 行")
print(f"修改文件: {total['files_modified']} 个\n")

for path, data in sorted(projects.items(), key=lambda x: -x[1]["duration"]):
    print(f"\n## {path}")
    print(f"   会话: {data['sessions']} | 时长: {data['duration']:.0f}min | +{data['lines_added']}/-{data['lines_removed']} 行 | 文件: {data['files_modified']}")
    for i, fp in enumerate(data["first_prompts"]):
        print(f"   prompt[{i+1}]: {fp}")
PYEOF
```

#### Agent C: 活跃目录扫描

不依赖 history/session-meta，直接扫描文件系统寻找本周有变动的项目：
1. 扫描常用项目父目录（`~/Documents/1_Project/`、`~/dev/`、`~/SVN/`）
2. 查找本周内有文件修改的子目录
3. 对 git 仓库执行 `git log --oneline --after=START_DATE --before=END_DATE`
4. 扫描非 git 目录中本周新建/修改的文件

这个 Agent 能捕捉到 history.jsonl 和 session-meta 可能遗漏的活动（比如手动操作、其他工具产生的变更）。

### Wave 1 完成后：合并项目全集

三个 Agent 返回后，合并得到「项目全集」：
- **交叉比对**：检查是否有项目只在某一个数据源出现——这通常意味着其他源遗漏了
- **合并统计**：每个项目整合三个数据源的信息
- **按活跃度排序**：命令数 + 会话时长 + git 提交数 加权排序

### Wave 2: 按项目深入分析（并行启动 N 个 Explore Agent）

将项目全集按活跃度分组（每组 2-3 个项目），为每组启动一个 Agent 做深度分析。

每个 Agent 的任务：
1. **Git 分析**（如有）：读 git log 的完整提交信息（`git log --after=... --format="%h %s"`），理解做了什么
2. **文档扫描**：查看项目中本周新建/修改的关键文档（PRD、设计文档、README）
3. **Memory 读取**：读取项目对应的 `~/.claude/projects/{path}/memory/` 了解业务背景
4. **CLAUDE.md 读取**：了解项目技术栈和约定
5. **产出物盘点**：统计本周的实际交付物（文档数、页面数、API 数等）

每个 Agent 输出格式：
```
项目名: XXX
业务背景: 一句话描述
本周工作:
  - 工作项1: 描述 | 产出物: xxx | 状态: ✅/🔄
  - 工作项2: ...
关键数据: 新增 X 行代码, X 个文件, X 份文档
```

### Wave 3: 交叉校验与分类（1 个 Agent）

最后一个 Agent 负责质量保证：

1. **完整性检查**：对比 Wave 1 的项目全集与 Wave 2 的分析结果，确认没有项目被遗漏
2. **数据一致性**：对比不同数据源的统计数字，取最准确的值
3. **去重合并**：将同一业务下的多个子项目合并为一个工作项
4. **业务分类**：将所有工作项归入 3-5 个业务板块
5. **输出结构化数据**：为 Phase 3 提供完整的分类结果

> **为什么需要三波？** 单 Agent 处理一周数据量（1000+ 条命令、200+ 个会话、30+ 个项目）时，上下文窗口压力大，容易截断或遗漏小项目。三波架构让每个 Agent 只处理一部分数据，最后由校验 Agent 保证完整性。

---

## Phase 3: 分析与分类

合并三个 Agent 的数据后，进行智能分类。

### 3.1 项目去重与合并

同一个业务可能有多个子目录（如前后端分离），需要合并：
- 路径相似的项目合并为一个工作项
- 合并统计数据

### 3.2 业务主题分类

根据项目名称、命令内容、git 提交信息，将工作项归入业务板块。常见分类维度：

| 板块类型 | 典型特征 |
|----------|----------|
| 客户项目交付 | 项目名含客户名/地名，有 PRD/需求/原型 |
| 产品研发 | 有持续的 issue/PR/部署活动 |
| AI 能力建设 | 培训、工具开发、方法论整理 |
| 内部工具 | 公司内部使用的系统/工具 |
| 商务拓展 | 客户交流、演示材料准备 |
| 方案策划 | 立项方案、规划文档 |

不要硬套分类——根据实际工作内容灵活组织，让周报读起来自然。板块数量控制在 3-5 个。

### 3.3 工作项描述

为每个工作项生成面向领导的描述：
- **用业务语言**，不用技术术语（"完成 OA 系统全量设计文档" 而非 "写了 Vue3 组件"）
- **突出产出物**（文档 × 几份、页面 × 几个、系统 × 1 套）
- **标注状态**（✅ 已完成 / 🔄 进行中）

---

## Phase 4: 用户确认

生成初稿前，通过 AskUserQuestion 向用户确认关键信息：

### 第一轮确认（必问）

使用 AskUserQuestion 同时询问：

1. **项目筛选**："以下项目是否都纳入周报？有没有个人项目需要排除？"
   - 列出识别到的所有项目供用户勾选
2. **分类确认**："我把工作分成了以下 N 个板块：[板块列表]。分类是否合理？"

### 第二轮确认（生成初稿后）

1. **下周计划**："是否需要填写下周计划？"
   - 选项：我来口述补充 / 先不写 / 帮我根据进行中的工作推测
2. **风险项**："本周是否有风险或需协调事项？"
   - 选项：没有 / 有，我来补充

---

## Phase 5: 生成报告

### 5.1 报告结构

阅读 `references/report-template.md` 获取完整模板。核心结构：

```
标题 + 元信息
├── 本周概览（2-3 句话）
├── 重点工作（按板块，每项含状态+产出）
├── 数据摘要（表格）
├── 下周计划（表格，按优先级）
└── 风险与协调
```

### 5.2 写作原则

- **简洁**：整篇周报控制在 A4 两页以内，会议上能 3 分钟讲完
- **结果导向**：写"完成了什么"而非"做了什么"——"完成 OA 全量设计文档（15,000+ 行）"比"写了很多设计文档"好
- **数据说话**：用具体数字而非模糊描述——"处理 8 个 Issue"比"处理了多个问题"好
- **板块排序**：按业务重要性排序，不按时间顺序

### 5.3 输出

将报告保存为 Markdown 文件：
- **文件名格式**：`周报_{YYYY-MM-DD}_{YYYY-MM-DD}.md`（起止日期）
- **保存位置**：当前工作目录
- 保存后展示报告全文，并告知文件路径

---

## Phase 6: 用户审阅

展示报告后说：
> "周报已保存到 `{文件路径}`。需要调整什么吗？"

根据反馈用 Edit 工具精确修改，不重新生成整个文档。

---

## 附加资源

- **`references/report-template.md`**：完整的周报 Markdown 模板，包含格式说明和示例
