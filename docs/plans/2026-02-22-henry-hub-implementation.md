# Henry Hub Marketplace Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Claude Code plugin marketplace at `henrywen98/henry-hub` with 15 plugins, each with Chinese README.md.

**Architecture:** Git repo with `.claude-plugin/marketplace.json` at root, all plugins under `plugins/` directory. Each plugin is self-contained with its own `.claude-plugin/plugin.json`.

**Tech Stack:** Git, GitHub CLI (`gh`), SSH, shell commands for file migration.

---

### Task 1: Initialize repository and create marketplace.json

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `.gitignore`

**Step 1: Initialize git repo**

Run: `cd /Users/henry/dev/henry-marketplace && git init`

**Step 2: Create .gitignore**

```
.DS_Store
__pycache__/
*.pyc
node_modules/
```

**Step 3: Create marketplace.json**

```json
{
  "name": "henry-hub",
  "description": "Henry's personal plugin marketplace for Claude Code",
  "plugins": [
    { "name": "doc-coauthoring", "description": "文档协作工作流", "source": "./plugins/doc-coauthoring" },
    { "name": "docx", "description": "Word 文档处理", "source": "./plugins/docx" },
    { "name": "pdf", "description": "PDF 文档处理", "source": "./plugins/pdf" },
    { "name": "pptx", "description": "PPT 文档处理", "source": "./plugins/pptx" },
    { "name": "ssot-prompt-engineer", "description": "SSOT 驱动的提示词工程", "source": "./plugins/ssot-prompt-engineer" },
    { "name": "xlsx", "description": "Excel 文档处理", "source": "./plugins/xlsx" },
    { "name": "batch-commit", "description": "批量智能提交工具", "source": "./plugins/batch-commit" },
    { "name": "test-case-generator", "description": "测试用例生成器", "source": "./plugins/test-case-generator" },
    { "name": "comprehensive-test-generation", "description": "全面测试生成策略", "source": "./plugins/comprehensive-test-generation" },
    { "name": "prd-workflow", "description": "PRD 需求规格文档工作流", "source": "./plugins/prd-workflow" },
    { "name": "gen-requirement-doc", "description": "需求确认单生成器", "source": "./plugins/gen-requirement-doc" },
    { "name": "ai-pm-feedback-collector", "description": "AI产品经理反馈收集器", "source": "./plugins/ai-pm-feedback-collector" },
    { "name": "github-issue-generator", "description": "GitHub Issue 生成器", "source": "./plugins/github-issue-generator" },
    { "name": "code-simplifier", "description": "代码简化与优化", "source": "./plugins/code-simplifier" },
    { "name": "superpowers", "description": "核心技能库：TDD、调试、协作", "source": "./plugins/superpowers" }
  ]
}
```

**Step 4: Commit**

```bash
git add .gitignore .claude-plugin/marketplace.json
git commit -m "feat: initialize henry-hub marketplace with plugin registry"
```

---

### Task 2: Migrate skill-based plugins from ~/.claude/skills/ (6 plugins)

Migrate: doc-coauthoring, docx, pdf, pptx, ssot-prompt-engineer, xlsx

**Step 1: Create plugin structures and copy files**

For each skill, create `.claude-plugin/plugin.json` and copy skill files into `skills/<name>/`.

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins
SRC=/Users/henry/.claude/skills

# doc-coauthoring
mkdir -p $BASE/doc-coauthoring/.claude-plugin $BASE/doc-coauthoring/skills
cp -r $SRC/doc-coauthoring $BASE/doc-coauthoring/skills/

# docx
mkdir -p $BASE/docx/.claude-plugin $BASE/docx/skills
cp -r $SRC/docx $BASE/docx/skills/

# pdf
mkdir -p $BASE/pdf/.claude-plugin $BASE/pdf/skills
cp -r $SRC/pdf $BASE/pdf/skills/

# pptx
mkdir -p $BASE/pptx/.claude-plugin $BASE/pptx/skills
cp -r $SRC/pptx $BASE/pptx/skills/

# ssot-prompt-engineer
mkdir -p $BASE/ssot-prompt-engineer/.claude-plugin $BASE/ssot-prompt-engineer/skills
cp -r $SRC/ssot-prompt-engineer $BASE/ssot-prompt-engineer/skills/

# xlsx
mkdir -p $BASE/xlsx/.claude-plugin $BASE/xlsx/skills
cp -r $SRC/xlsx $BASE/xlsx/skills/
```

**Step 2: Create plugin.json for each**

Each needs a `.claude-plugin/plugin.json` with name, version, description read from the corresponding SKILL.md frontmatter.

**Step 3: Create Chinese README.md for each**

Read SKILL.md to extract purpose, triggers, and write a Chinese README.md in each plugin root.

**Step 4: Commit**

```bash
git add plugins/doc-coauthoring plugins/docx plugins/pdf plugins/pptx plugins/ssot-prompt-engineer plugins/xlsx
git commit -m "feat: add 6 document/workflow skill plugins"
```

---

### Task 3: Migrate existing plugins (batch-commit, test-case-generator)

**Step 1: Copy and restructure batch-commit**

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins
SRC=/Users/henry/.claude/plugins

mkdir -p $BASE/batch-commit/.claude-plugin
cp -r $SRC/batch-commit/commands $BASE/batch-commit/
cp -r $SRC/batch-commit/references $BASE/batch-commit/
# Move plugin.json into .claude-plugin/
cp $SRC/batch-commit/plugin.json $BASE/batch-commit/.claude-plugin/
```

**Step 2: Copy and restructure test-case-generator**

```bash
mkdir -p $BASE/test-case-generator/.claude-plugin
cp -r $SRC/test-case-generator/skills $BASE/test-case-generator/
cp $SRC/test-case-generator/convert_to_xlsx.py $BASE/test-case-generator/
cp $SRC/test-case-generator/requirements.txt $BASE/test-case-generator/
cp $SRC/test-case-generator/plugin.json $BASE/test-case-generator/.claude-plugin/
```

**Step 3: Create Chinese README.md for each**

**Step 4: Commit**

```bash
git add plugins/batch-commit plugins/test-case-generator
git commit -m "feat: add batch-commit and test-case-generator plugins"
```

---

### Task 4: Migrate comprehensive-test-generation

**Step 1: Copy files**

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins
SRC=/Users/henry/dev/skills-marketplace/comprehensive-test-generation

mkdir -p $BASE/comprehensive-test-generation/.claude-plugin
mkdir -p $BASE/comprehensive-test-generation/skills/comprehensive-test-generation
cp $SRC/SKILL.md $BASE/comprehensive-test-generation/skills/comprehensive-test-generation/
cp -r $SRC/examples $BASE/comprehensive-test-generation/
cp -r $SRC/references $BASE/comprehensive-test-generation/
```

**Step 2: Create plugin.json and Chinese README.md**

**Step 3: Commit**

```bash
git add plugins/comprehensive-test-generation
git commit -m "feat: add comprehensive-test-generation plugin"
```

---

### Task 5: Migrate prd-workflow (from zip)

**Step 1: Extract and restructure**

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins/prd-workflow
mkdir -p $BASE/.claude-plugin $BASE/commands $BASE/scripts $BASE/templates

# Extract from zip
cd /tmp && unzip -o /Users/henry/dev/skills-marketplace/prd-workflow.zip

# Copy commands
cp /tmp/.claude/commands/prd.create.md $BASE/commands/
cp /tmp/.claude/commands/prd.clarify.md $BASE/commands/

# Copy scripts
cp /tmp/.prd/scripts/bash/* $BASE/scripts/

# Copy templates
cp /tmp/.prd/templates/* $BASE/templates/
```

**Step 2: Create plugin.json and Chinese README.md**

**Step 3: Commit**

```bash
git add plugins/prd-workflow
git commit -m "feat: add prd-workflow plugin"
```

---

### Task 6: Migrate gen-requirement-doc (from zip)

**Step 1: Extract and restructure**

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins/gen-requirement-doc
mkdir -p $BASE/.claude-plugin $BASE/skills/gen-requirement-doc

cd /tmp && unzip -o /Users/henry/dev/skills-marketplace/gen-requirement-doc.zip
cp /tmp/gen-requirement-doc/SKILL.md $BASE/skills/gen-requirement-doc/
```

**Step 2: Create plugin.json and Chinese README.md**

**Step 3: Commit**

```bash
git add plugins/gen-requirement-doc
git commit -m "feat: add gen-requirement-doc plugin"
```

---

### Task 7: Migrate SSH skills (ai-pm-feedback-collector, github-issue-generator)

**Step 1: SCP files from henry machine**

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins
SRC=henry:~/.openclaw/workspace/skills

# ai-pm-feedback-collector
mkdir -p $BASE/ai-pm-feedback-collector/.claude-plugin $BASE/ai-pm-feedback-collector/skills
scp -r $SRC/ai-pm-feedback-collector $BASE/ai-pm-feedback-collector/skills/

# github-issue-generator
mkdir -p $BASE/github-issue-generator/.claude-plugin $BASE/github-issue-generator/skills
scp -r $SRC/github-issue-generator $BASE/github-issue-generator/skills/
```

**Step 2: Create plugin.json and Chinese README.md for each**

**Step 3: Commit**

```bash
git add plugins/ai-pm-feedback-collector plugins/github-issue-generator
git commit -m "feat: add ai-pm-feedback-collector and github-issue-generator plugins"
```

---

### Task 8: Fork official plugins (code-simplifier, superpowers)

**Step 1: Copy code-simplifier**

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins/code-simplifier
SRC=/Users/henry/.claude/plugins/cache/claude-plugins-official/code-simplifier/1.0.0

mkdir -p $BASE
cp -r $SRC/.claude-plugin $BASE/
cp -r $SRC/agents $BASE/
```

**Step 2: Copy superpowers**

```bash
BASE=/Users/henry/dev/henry-marketplace/plugins/superpowers
SRC=/Users/henry/.claude/plugins/cache/claude-plugins-official/superpowers/4.3.1

mkdir -p $BASE
cp -r $SRC/.claude-plugin $BASE/
cp -r $SRC/skills $BASE/
cp -r $SRC/agents $BASE/
cp -r $SRC/commands $BASE/
cp -r $SRC/hooks $BASE/
cp -r $SRC/lib $BASE/
cp -r $SRC/docs $BASE/
cp -r $SRC/tests $BASE/
cp $SRC/LICENSE $BASE/
cp $SRC/RELEASE-NOTES.md $BASE/
```

**Step 3: Create Chinese README.md for each**

**Step 4: Commit**

```bash
git add plugins/code-simplifier plugins/superpowers
git commit -m "feat: fork code-simplifier and superpowers from official marketplace"
```

---

### Task 9: Create root README.md

**Step 1: Write Chinese README.md at repo root**

Include: marketplace overview, plugin list table, installation instructions, usage guide.

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add Chinese README for marketplace"
```

---

### Task 10: Create GitHub repo and push

**Step 1: Create remote repo**

```bash
cd /Users/henry/dev/henry-marketplace
gh repo create henrywen98/henry-hub --public --source=. --push
```

**Step 2: Verify**

```bash
gh repo view henrywen98/henry-hub
```
