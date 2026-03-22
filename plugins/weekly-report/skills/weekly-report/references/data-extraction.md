# 数据提取脚本参考

Wave 1 的三个 Agent 使用以下脚本做数据提取。脚本保证完整遍历数据，不受上下文窗口限制。

使用前将 `$START_TS`、`$END_TS`、`$START_DATE`、`$END_DATE` 替换为 Phase 1 计算的实际值。

---

## Agent A: 聊天记录提取脚本

```bash
python3 << 'PYEOF'
import json, os
from datetime import datetime, date, timedelta
from collections import defaultdict

START_TS = $START_TS   # 毫秒时间戳
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

---

## Agent B: 会话元数据提取脚本

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

---

## Agent C: 活跃目录扫描命令

```bash
# 1. 创建时间标记文件
touch -t $(date -j -v-${DAYS_BACK}d +%Y%m%d0000) /tmp/week_start_marker

# 2. 扫描 git 仓库的本周提交
for dir in ~/Documents/1_Project/*/ ~/dev/*/ ~/SVN/*/; do
  if [ -d "$dir/.git" ]; then
    commits=$(cd "$dir" && git log --oneline --after="$START_DATE" --before="$END_DATE_NEXT" 2>/dev/null | head -30)
    if [ -n "$commits" ]; then
      echo "=== $dir ==="
      echo "$commits"
      echo ""
    fi
  fi
done

# 3. 扫描非 git 目录的新建/修改文件
find ~/Documents/1_Project/ ~/dev/ ~/SVN/ \
  -maxdepth 3 -newer /tmp/week_start_marker \
  \( -name "*.md" -o -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.vue" -o -name "*.docx" \) \
  2>/dev/null | head -100
```
