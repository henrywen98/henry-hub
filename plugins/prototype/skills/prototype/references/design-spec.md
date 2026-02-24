# 杭州产投系统原型完整设计规范

## 技术规范

- 纯HTML + CSS + JavaScript，不使用任何框架（无Bootstrap、无Ant Design）
- 使用原生Flexbox布局
- 单文件HTML（CSS和JS内嵌）

## 配色体系

### Modal/表单类界面 — 橙棕色系

- 主色: `#d4730f`（橙棕色，用于按钮、链接、焦点状态）
- 主色hover: `#b8600d`
- AI标签背景: `#fff7e6`, 文字: `#d4730f`

### 完整应用系统界面 — 深红色系

- 主色: `#8B0000`（深红色）
- 渐变Header: `linear-gradient(90deg, #8B0000 0%, #A52A2A 100%)`

### 通用色

- 背景: `#f5f5f5`（浅灰）
- 白色容器: `#ffffff`
- 边框: `#d9d9d9`（常规）、`#e8e8e8`（淡）
- 文本: `#333`（主）、`#666`（次）、`#999`（提示）
- 成功: `#52c41a`
- 错误/删除: `#ff4d4f`

## 字体

```css
font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
```

- 标题: 16-18px, font-weight: 500
- 正文: 14px
- 辅助文字: 12-13px
- 行高: 1.5

## 表单组件规范

- Input高度: 36px
- Padding: 0 12px
- Border: 1px solid #d9d9d9
- Border-radius: 2px（直角风格，非圆角）
- Focus状态: `border-color: #d4730f; box-shadow: 0 0 0 2px rgba(212,115,15,0.1)`
- 必填项标记: `color: #d4730f`

## 按钮规范

- 主按钮: `background: #d4730f; color: white; border: none; padding: 7px 15px;`
- 次按钮/轮廓按钮: `background: white; border: 1px solid #d4730f; color: #d4730f;`
- 危险按钮: `background: #ff4d4f; color: white;`
- 圆角: 2px
- Hover过渡: `transition: all 0.2s`

## 布局模式

### Modal对话框布局

- 全屏遮罩: `background: rgba(0,0,0,0.5)`
- 对话框: `max-width: 1300px; background: white; border-radius: 4px`
- Header: `padding: 16px 24px; border-bottom: 1px solid #e8e8e8; font-size: 18px; font-weight: 500`
- Body: `padding: 24px; background: #f5f5f5`
- Footer: `padding: 16px 24px; border-top: 1px solid #e8e8e8;` 按钮右对齐

### 应用系统布局

- 顶部Header: 50px高，渐变背景，白色文字
- 左侧Sidebar: 180px宽，白色背景
- 主内容区: `flex: 1`

## 特色组件

### 1. AI生成标签

```css
display: inline-block;
background: #fff7e6;
color: #d4730f;
padding: 2px 8px;
border-radius: 2px;
font-size: 12px;
margin-left: 8px;
```

### 2. 字符计数

位于textarea右下角，`color: #999; font-size: 12px`

### 3. 文件上传区

```css
border: 2px dashed #d9d9d9;
text-align: center;
padding: 20px;
cursor: pointer;
/* Hover */
border-color: #d4730f;
background: #fffbf5;
```

### 4. Loading状态

- 旋转spinner: `border: 2px solid #d4730f; border-top-color: transparent; animation: spin 1s linear infinite`
- 全屏遮罩loading: 半透明白色背景 + 居中spinner

### 5. Toast通知

固定顶部中央，`background: #52c41a`（成功）或 `#ff4d4f`（错误），白色文字

## 交互规范

- 所有transition: 0.2s ease
- 按钮hover有明显反馈
- 表单focus有边框变色+阴影
- 支持基本的表单验证提示

## 中文友好

- 使用中文标签和提示
- 支持中文输入
- 日期格式: YYYY-MM-DD
