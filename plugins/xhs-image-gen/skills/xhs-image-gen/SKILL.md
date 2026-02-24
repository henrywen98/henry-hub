---
name: xhs-image-gen
description: "将文案或文章内容生成小红书风格的图文卡片（HTML 文件，可截图分享）。当用户提到生成小红书图文、小红书卡片、小红书封面、XHS 图片、RedNote 图文时触发。支持从文件或直接输入文案，生成 1-10 张风格化卡片。"
---

# 小红书图文卡片生成器

将文案、文章或主题内容转化为 1-10 张小红书风格的 HTML 图文卡片。

## 触发条件

- 用户提到「小红书图文」「小红书卡片」「小红书图片」「XHS 图片」「RedNote 图」
- 用户想把文案/文章变成适合小红书发布的视觉内容
- 用户输入文件路径或直接输入文案内容

## 工作流

### Step 1：解析输入

**支持以下输入形式：**
- 文件路径：读取文件内容（markdown、txt、文章）
- 直接文案：用户直接输入文字内容
- 主题词：如「今日星座运势」，根据主题自行发挥内容

**参数解析：**
- `--style <风格名>` 指定视觉风格（见风格列表）
- `--layout <布局名>` 指定布局方式（见布局列表）
- 无参数时，根据内容智能选择最适合的风格和布局

### Step 2：内容规划

将内容分解为 1-10 个卡片，每张卡片对应一个核心点：
- **第 1 张**：封面卡（标题 + 副标题 + 吸睛元素）
- **中间张**：内容卡（每张聚焦 1 个核心观点）
- **最后 1 张**（可选）：总结/行动卡

**分卡原则：**
- 内容短（200字内）→ 1-2 张
- 内容中等（500字内）→ 3-5 张
- 内容长（500字以上）→ 5-10 张
- 保持每张卡片信息量适中，避免文字过密

### Step 3：生成 HTML 卡片

为每张卡片生成一个独立 HTML 文件，命名为 `xhs_card_01.html`、`xhs_card_02.html`……

**卡片尺寸**：宽 375px × 高 500px（标准小红书竖版比例）

**生成要求：**
1. 使用选定的风格和布局（见下方详细说明）
2. 所有样式内联（`<style>` 标签内）
3. 使用 emoji 增加活泼感
4. 包含小红书常见元素：话题标签、互动引导语

**输出路径**：在当前工作目录下生成，或用户指定的目录。

### Step 4：生成完毕提示

告知用户：
1. 共生成了几张卡片，文件路径在哪里
2. 建议用浏览器打开预览效果
3. 可用截图工具或浏览器打印保存为图片
4. 提示可用 `--style` 和 `--layout` 参数重新生成不同风格

---

## 风格（Style）列表

选择一种与内容气质匹配的视觉风格：

| 风格名 | 中文名 | 适合内容 | 主色调参考 |
|--------|--------|----------|-----------|
| `cute` | 可爱萌系 | 生活日常、美食、萌宠 | 粉色系、圆角大、插画感 |
| `fresh` | 清新简约 | 健康生活、植物、旅行 | 绿色系、白底、留白多 |
| `warm` | 温暖橙系 | 情感、美食、秋冬 | 橙褐色系、暖光感 |
| `bold` | 大字报风 | 干货知识、职场、励志 | 高对比、大字体、醒目 |
| `minimal` | 极简黑白 | 商务、设计、科技 | 黑白灰、线条感 |
| `retro` | 复古杂志 | 音乐、电影、文艺 | 米黄+暗红、纸张质感 |
| `pop` | 波普艺术 | 时尚、潮流、娱乐 | 高饱和多色、几何拼接 |
| `notion` | Notion 风 | 笔记、学习、效率 | 白底黑字、图标化、结构清晰 |
| `chalkboard` | 黑板报 | 教育、科普、学生 | 深色背景、粉笔字感 |

**默认选择逻辑：**
- 干货/知识类 → `bold` 或 `notion`
- 生活/美食类 → `cute` 或 `warm`
- 旅行/自然类 → `fresh`
- 文艺/复古类 → `retro`

---

## 布局（Layout）列表

| 布局名 | 中文名 | 特点 |
|--------|--------|------|
| `sparse` | 疏朗型 | 大留白，重点突出，视觉轻松 |
| `balanced` | 均衡型 | 图文平衡，标准卡片布局 |
| `dense` | 密集型 | 信息量大，适合干货列表 |
| `list` | 列表型 | 竖向列举，步骤感强 |
| `comparison` | 对比型 | 左右对比，适合 before/after |
| `flow` | 流程型 | 上下流程图感，适合教程 |

**默认选择逻辑：**
- 列举型内容 → `list` 或 `dense`
- 步骤/教程类 → `flow`
- 故事/情感类 → `sparse` 或 `balanced`

---

## HTML 卡片设计规范

### 基础结构

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 375px;
    height: 500px;
    overflow: hidden;
    font-family: /* 根据风格选择 */;
    background: /* 根据风格选择 */;
  }
</style>
</head>
<body>
  <!-- 卡片内容 -->
</body>
</html>
```

### 各风格 CSS 规范

**cute（可爱萌系）**
```css
font-family: 'Segoe UI', sans-serif;
background: linear-gradient(135deg, #FFE4F0 0%, #FFF0F5 100%);
/* 主色：#FF6B9D，辅色：#FFD3E8，圆角：16px，emoji 多 */
```

**fresh（清新简约）**
```css
font-family: 'Segoe UI', sans-serif;
background: #F7FBF5;
/* 主色：#52B788，辅色：#D8F3DC，圆角：12px，留白充足 */
```

**warm（温暖橙系）**
```css
font-family: Georgia, serif;
background: linear-gradient(160deg, #FFF8F0 0%, #FFF3E8 100%);
/* 主色：#E8823A，辅色：#FFD9B3，圆角：8px */
```

**bold（大字报风）**
```css
font-family: 'Arial Black', sans-serif;
background: #FFFEF5;
/* 主色：#FF3B30，辅色：#FFE600，无圆角或小圆角，字体超大 */
```

**minimal（极简黑白）**
```css
font-family: 'Helvetica Neue', sans-serif;
background: #FFFFFF;
/* 主色：#1A1A1A，辅色：#F5F5F5，边框线条感，细字重 */
```

**retro（复古杂志）**
```css
font-family: Georgia, 'Times New Roman', serif;
background: #F5F0E8;
/* 主色：#8B2E2E，辅色：#C9A96E，纸张纹理感，斜体装饰 */
```

**pop（波普艺术）**
```css
font-family: 'Arial Black', Impact, sans-serif;
background: #FFE500;
/* 多色交替：#FF006E, #FB5607, #3A86FF，黑色描边，几何感 */
```

**notion（Notion 风）**
```css
font-family: ui-sans-serif, system-ui, sans-serif;
background: #FFFFFF;
/* 主色：#37352F，辅色：#F1F0EE，图标化列表，卡片嵌套感 */
```

**chalkboard（黑板报）**
```css
font-family: 'Segoe UI', sans-serif;
background: #2D4A3E;
/* 主色：#FFFFFF，辅色：#A8D5C2，粉笔字感（text-shadow 模拟）*/
```

### 必含元素

**封面卡（第 1 张）必须包含：**
- 醒目大标题（主要内容/吸引眼球的钩子）
- 1-2 行副标题或摘要
- 装饰性 emoji 或图形元素
- 底部作者标签区（可写 `@用户名` 或留空）

**内容卡（中间张）必须包含：**
- 卡片序号（如 `02/05`）
- 小标题 + 正文内容
- 适量 emoji 点缀
- 分隔线或图形装饰

**总结卡（最后 1 张，可选）包含：**
- 核心要点总结（3 条以内）
- 互动引导语（如「你有什么想法？评论区见 👇」）
- 话题标签（如 `#主题 #生活分享`）

---

## 示例调用

```
/xhs-image-gen 今日番茄炒蛋完美做法

/xhs-image-gen posts/ai-future.md --style notion --layout list

/xhs-image-gen 3个职场沟通技巧 --style bold

/xhs-image-gen content.txt --style cute --layout sparse
```

---

## 生成后的使用建议

生成完毕后，告知用户：
1. 用 **Chrome/Safari** 打开 HTML 文件预览效果
2. 截图保存为图片（推荐使用系统截图工具框选卡片区域）
3. 或用浏览器「打印 → 另存为 PDF → 截图」工作流
4. 若需批量截图，可使用 `puppeteer` 或 `playwright` 脚本自动化
