---
name: prototype
description: "生成符合杭州产投系统设计规范的HTML原型。当用户提到「原型」「prototype」「HTML原型」「UI原型」「Mock」「界面原型」「生成页面」「画一个页面」，或要求生成Modal、表单、系统界面、前端页面模型时触发。适用于杭州产投投资管理系统(二期)的所有UI原型输出。"
---

# 杭州产投 HTML 原型生成

## 核心规则

1. **单文件HTML**：纯HTML + CSS + JS 内嵌，不使用任何框架
2. **双色系**：根据界面类型自动选择配色
   - **Modal/表单** → 橙棕色 `#d4730f`
   - **完整应用界面** → 深红色 `#8B0000`
3. **直角风格**：border-radius 统一 `2px`，非圆角
4. **中文界面**：所有标签、提示、日期(YYYY-MM-DD)均为中文

## 工作流程

1. 确认用户需求属于哪种界面类型（Modal 或 应用系统）
2. 读取完整设计规范：`references/design-spec.md`
3. 按规范生成单文件 HTML 原型
4. 输出文件保存到 `01-需求文档/` 对应模块目录下

## 快速参考

### 配色

| 用途 | Modal模式 | 应用系统模式 |
|------|-----------|-------------|
| 主色 | `#d4730f` | `#8B0000` |
| 主色hover | `#b8600d` | `#A52A2A` |
| Header | 白底+底边框 | `linear-gradient(90deg, #8B0000, #A52A2A)` |

**通用色**: 背景 `#f5f5f5` · 边框 `#d9d9d9` · 文本 `#333/#666/#999` · 成功 `#52c41a` · 错误 `#ff4d4f`

### 字体

```css
font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
```

标题 16-18px/500 · 正文 14px · 辅助 12-13px · 行高 1.5

### 组件速查

- **Input**: 36px高, padding 0 12px, border 1px solid #d9d9d9, radius 2px
- **主按钮**: bg #d4730f, white text, padding 7px 15px, radius 2px
- **次按钮**: white bg, border 1px solid #d4730f, color #d4730f
- **AI标签**: inline-block, bg #fff7e6, color #d4730f, 12px, padding 2px 8px
- **上传区**: border 2px dashed #d9d9d9, hover → border #d4730f + bg #fffbf5
- **Toast**: 固定顶部中央, 成功 #52c41a / 错误 #ff4d4f

### 详细规范

完整的配色、布局、组件、交互规范见 [references/design-spec.md](references/design-spec.md)。
