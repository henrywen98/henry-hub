# xhs-image-gen

将文案、文章或主题内容一键生成小红书风格图文卡片（HTML 格式，可截图分享）。支持 9 种视觉风格 × 6 种布局，生成 1-10 张卡片，覆盖封面、内容、总结全流程。

## 使用场景

当用户需要进行以下操作时触发：

- 把一篇文章或文案转化为小红书图文
- 生成小红书封面图、内容卡片
- 输入主题词，自动生成图文内容
- 制作 XHS / RedNote 风格的可视化内容

## 安装

```bash
/plugins install xhs-image-gen@henry-hub
```

## 使用示例

```
# 直接输入主题
/xhs-image-gen 今日番茄炒蛋完美做法

# 传入文章文件
/xhs-image-gen posts/ai-future.md

# 指定风格
/xhs-image-gen 3个职场沟通技巧 --style bold

# 指定风格和布局
/xhs-image-gen content.txt --style notion --layout list
```

## 支持的风格

| 参数 | 风格名 | 适合内容 |
|------|--------|----------|
| `cute` | 可爱萌系 | 生活日常、美食、萌宠 |
| `fresh` | 清新简约 | 健康生活、植物、旅行 |
| `warm` | 温暖橙系 | 情感、美食、秋冬 |
| `bold` | 大字报风 | 干货知识、职场、励志 |
| `minimal` | 极简黑白 | 商务、设计、科技 |
| `retro` | 复古杂志 | 音乐、电影、文艺 |
| `pop` | 波普艺术 | 时尚、潮流、娱乐 |
| `notion` | Notion 风 | 笔记、学习、效率 |
| `chalkboard` | 黑板报 | 教育、科普、学生 |

## 支持的布局

| 参数 | 布局名 | 特点 |
|------|--------|------|
| `sparse` | 疏朗型 | 大留白，重点突出 |
| `balanced` | 均衡型 | 图文平衡，标准布局 |
| `dense` | 密集型 | 信息量大，干货列表 |
| `list` | 列表型 | 竖向列举，步骤感强 |
| `comparison` | 对比型 | 左右对比，before/after |
| `flow` | 流程型 | 上下流程图感，适合教程 |

## 输出

- 生成 `xhs_card_01.html` ～ `xhs_card_N.html`
- 卡片尺寸：375px × 500px（小红书竖版比例）
- 用浏览器打开后截图即可发布
