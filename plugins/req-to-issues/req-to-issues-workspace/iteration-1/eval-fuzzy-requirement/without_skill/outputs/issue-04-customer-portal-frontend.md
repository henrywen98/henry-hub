# Issue #4: 客户门户 - 前端页面（登录 + 对账单）

## 类型
feat

## 标签
`customer-portal`, `frontend`, `high-priority`

## 依赖
- Issue #1（客户门户认证体系）
- Issue #2（客户对账单 API）

## 描述

### 背景
客户需要一个独立的门户前端页面来登录、查看对账信息。该门户需要与内部管理系统保持 UI 一致性（复用 Ant Design Vue），但路由和布局独立。

### 目标
实现客户门户的前端页面，包含登录、对账单查看功能。

### 需求详情

#### 1. 路由体系
在现有 Vue Router 中增加 `/portal` 前缀的路由组：
```
/portal/login          — 客户登录页
/portal/dashboard      — 客户首页（对账总览）
/portal/statement      — 对账单明细
/portal/payments       — 付款记录
```
- 门户路由使用独立的布局组件 `PortalLayout.vue`（区别于内部管理的 `DashboardView.vue`）
- 路由守卫需区分客户 Token 和员工 Token

#### 2. 客户登录页
- `views/portal/PortalLoginView.vue`
- UI 参考现有 `LoginView.vue`，但标题改为"客户门户"
- 登录后跳转到 `/portal/dashboard`
- 登录凭证：邮箱 + 密码

#### 3. 对账总览页（Dashboard）
- `views/portal/PortalDashboardView.vue`
- 顶部汇总卡片：
  - 订单总数
  - 总金额（按币种分组显示）
  - 已付款金额
  - 待付款余额（醒目颜色标记）
- 最近待付款订单列表（最多 5 条，按余额降序排列）
- "查看完整对账单" 快捷入口

#### 4. 对账单明细页
- `views/portal/StatementView.vue`
- 筛选条件栏：
  - 日期范围选择器
  - 订单状态筛选（全部 / 进行中 / 已完成）
  - 仅显示有余额的订单（开关）
- 订单列表表格：
  | 订单号 | 下单日期 | 订单状态 | 订单总额 | 已付款 | 待付款 | 操作 |
  |-------|---------|---------|---------|-------|-------|------|
  - "操作" 列包含：查看付款记录、去付款（仅余额 > 0 时可用）
- 底部汇总行：显示筛选结果的总金额、已付、待付合计
- 支持导出功能（预留按钮，后续实现）

#### 5. 付款记录页
- `views/portal/PaymentHistoryView.vue`
- 展示该客户的所有付款记录
- 表格列：付款单号、关联订单号、付款金额、付款日期、付款方式（线下/在线）、状态
- 支持按日期范围筛选

#### 6. 门户布局
- `views/portal/PortalLayout.vue`
- 顶部导航栏：Logo + 客户名称 + 导航链接 + 退出登录
- 导航链接：对账总览 / 对账单 / 付款记录
- 响应式设计，支持平板和移动端基本可用

### 技术要点
- 新建 `stores/portalAuth.ts`（Pinia Store），管理客户 Token 和用户信息
- 新建 `api/portal.ts`，封装门户相关 API 调用
- Axios 拦截器需区分门户请求和内部管理请求（可通过 URL 前缀判断）
- 复用 Ant Design Vue 组件，保持 UI 一致性
- 支持中英文（客户可能是外国人），至少英文界面

### 验收标准
- [ ] 客户可通过 `/portal/login` 登录门户
- [ ] 登录后可查看对账总览，数据正确显示
- [ ] 对账单列表支持筛选和排序
- [ ] 付款记录页正确显示历史付款
- [ ] 门户页面与内部管理页面路由和权限完全隔离
- [ ] 页面在桌面端和平板端可正常使用
- [ ] 门户界面默认英文（外贸客户使用）

### 相关文件
- `frontend/src/router/index.ts` — 路由配置（需扩展）
- `frontend/src/views/auth/LoginView.vue` — 现有登录页（参考）
- `frontend/src/views/dashboard/DashboardView.vue` — 现有布局（参考）
- `frontend/src/stores/auth.ts` — 现有认证 Store（参考）
- `frontend/src/api/client.ts` — Axios 实例
