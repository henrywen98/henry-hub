# docker-dev

Docker 与容器开发助手：Dockerfile 优化、docker-compose 编排、多阶段构建与容器安全审计。

## 功能特色

- **Dockerfile 静态分析**: `dockerfile_analyzer.py` 检测 `:latest` 标签、root 用户、未合并的 layer、硬编码 secrets 等 8 类反模式，支持 `--security` 深度扫描
- **docker-compose 校验**: `compose_validator.py` 检查 healthcheck 缺失、网络隔离、端口冲突、环境变量与 secrets 管理
- **多阶段构建模板**: Go/Rust/C++ distroless、Node.js Alpine、Python slim 三类完整示例
- **安全加固清单**: 非 root 用户、只读 FS、BuildKit secret mount、capability drops、health check 模板
- **双模输出**: 所有脚本支持 `--output json`，方便接入 CI 流水线做机器消费
- **零依赖**: 所有脚本只依赖 Python 3 标准库，无需 `pip install`

## 使用场景

触发词示例：

- "优化这个 Dockerfile"
- "Docker 镜像太大怎么办"
- "检查 docker-compose 配置"
- "容器安全审计"
- "写一个多阶段构建"
- "optimize Dockerfile" / "dockerfile best practices" / "container security"

## 安装

```bash
/plugins install docker-dev@henry-hub
```

## 脚本用法

```bash
# Dockerfile 分析
python3 scripts/dockerfile_analyzer.py Dockerfile
python3 scripts/dockerfile_analyzer.py Dockerfile --security --output json

# docker-compose 校验
python3 scripts/compose_validator.py docker-compose.yml
python3 scripts/compose_validator.py docker-compose.yml --strict --output json
```

## 文件结构

```
docker-dev/
├── .claude-plugin/plugin.json
├── skills/docker-dev/
│   ├── SKILL.md
│   ├── references/
│   │   ├── dockerfile-best-practices.md
│   │   └── compose-patterns.md
│   └── scripts/
│       ├── dockerfile_analyzer.py
│       └── compose_validator.py
├── NOTICE.md
└── README.md
```

## 致谢

本插件改编自 [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 的 `docker-development` skill，原项目基于 MIT License 发布。详细署名与修改说明见 `NOTICE.md`。
