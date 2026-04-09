# cicd-dev

CI/CD 流水线生成器：从项目技术栈信号自动生成 GitHub Actions / GitLab CI 流水线，拒绝盲目复制粘贴。

## 功能特色

- **技术栈自动检测**: `stack_detector.py` 基于 lockfile、manifest、script 命令优先级扫描 repo，识别 Node.js / Python / Go / Java / Rust 等技术栈
- **流水线 YAML 生成**: `pipeline_generator.py` 产出 lint / test / build / deploy 分阶段流水线，自动附带依赖缓存和矩阵构建策略
- **双平台支持**: 同一份 stack 检测结果可生成 **GitHub Actions** 或 **GitLab CI** 两种流水线
- **渐进式发布**: 内置 CI-only → staging → prod（带手动 gate）的安全部署模式，避免未经验证就上生产
- **机器可消费输出**: `--format json` 方便在更大的自动化流程中串联
- **零依赖**: 纯 Python 标准库，无需 `pip install`

## 使用场景

触发词示例：

- "生成 CI 流水线"
- "GitHub Actions 配置"
- "GitLab CI 怎么写"
- "检测项目技术栈"
- "加一个 staging 部署阶段"
- "bootstrap ci" / "pipeline" / "ci/cd" / "stack detection"

## 安装

```bash
/plugins install cicd-dev@henry-hub
```

## 脚本用法

```bash
# 1. 检测技术栈
python3 scripts/stack_detector.py --repo . --format text
python3 scripts/stack_detector.py --repo . --format json > detected-stack.json

# 2. 生成流水线（从检测结果）
python3 scripts/pipeline_generator.py \
  --input detected-stack.json \
  --platform github \
  --output .github/workflows/ci.yml

# 或一步到位（直接从 repo 生成）
python3 scripts/pipeline_generator.py --repo . --platform gitlab --output .gitlab-ci.yml
```

## 文件结构

```
cicd-dev/
├── .claude-plugin/plugin.json
├── skills/cicd-dev/
│   ├── SKILL.md
│   ├── references/
│   │   ├── deployment-gates.md
│   │   ├── github-actions-templates.md
│   │   └── gitlab-ci-templates.md
│   └── scripts/
│       ├── stack_detector.py
│       └── pipeline_generator.py
├── NOTICE.md
└── README.md
```

## 不适用场景

- ❌ 部署到具体云平台的 SDK 操作（AWS / GCP / Azure）
- ❌ 基础设施即代码（Terraform / Pulumi / CloudFormation）
- ❌ 应用级代码实现与 bug 修复

## 致谢

本插件改编自 [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 的 `ci-cd-pipeline-builder` skill，原项目基于 MIT License 发布。详细署名与修改说明见 `NOTICE.md`。
