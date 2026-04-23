# code-to-prd

从现有代码库逆向生成完整 PRD（产品需求文档）。自动分析路由、组件、状态管理、API 和用户交互，为每个页面与接口产出可供工程师或 AI 重建的业务文档。

> 本插件基于社区作品 [alirezarezvani/claude-skills › product-team/code-to-prd](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/code-to-prd)（MIT License, © 2025 Alireza Rezvani）移植到 henry-hub marketplace。原始 LICENSE 见本目录 `LICENSE` 文件。

## 能做什么

- **3 阶段工作流**：全局扫描 → 逐页/逐接口分析 → 结构化文档生成
- **前端支持**：React / Vue / Angular / Svelte / Next.js（App + Pages Router） / Nuxt / SvelteKit / Remix
- **后端支持**：NestJS / Express / Django / Django REST Framework / FastAPI / Flask
- **全栈支持**：前后端合并扫描，输出统一 PRD
- **产物**：`prd/README.md` 总览 + `prd/pages/*.md` 每页/每接口文档 + 枚举字典 + 质量自检清单

## 安装

```text
/plugins install code-to-prd@henry-hub
```

## 使用方式

触发词（中英文都行）：生成 PRD、反推需求、code to documentation、extract product specs、analyze page fields、document API endpoints 等。

快速运行：

```bash
# skill 会引导 Claude 使用内置脚本
python3 scripts/codebase_analyzer.py /path/to/project -o analysis.json
python3 scripts/prd_scaffolder.py analysis.json -o prd/ -n "My App"
```

详细流程、支持的框架矩阵、产出示例见 `skills/code-to-prd/SKILL.md`。

## 目录结构

```
plugins/code-to-prd/
├── .claude-plugin/plugin.json
├── LICENSE                              # 上游 MIT 许可证（保留署名）
├── README.md                            # 本文件
└── skills/code-to-prd/
    ├── SKILL.md                         # 主入口（自动发现）
    ├── assets/sample-analysis.json      # 分析结果样例
    ├── expected_outputs/                # 产出样例：页面文档 / 枚举字典 / README
    ├── references/                      # 框架识别模式 + PRD 质量清单
    └── scripts/                         # codebase_analyzer.py + prd_scaffolder.py
```

## 归属与许可

- 上游：https://github.com/alirezarezvani/claude-skills
- 版权：© 2025 Alireza Rezvani，MIT License
- 本目录 `LICENSE` 为上游 MIT 许可证原文，henry-hub 仅做搬运与 Chinese README，未修改 skill 主体内容。
