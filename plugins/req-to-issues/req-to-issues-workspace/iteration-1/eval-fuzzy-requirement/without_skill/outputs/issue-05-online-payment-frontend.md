# Issue #5: 在线付款 - 前端支付流程

## 类型
feat

## 标签
`customer-portal`, `frontend`, `payment`, `medium-priority`

## 依赖
- Issue #3（在线付款后端 API）
- Issue #4（客户门户前端页面）

## 描述

### 背景
后端已集成支付网关（Issue #3），前端需要实现付款交互流程，让客户可以在对账单页面发起在线付款。

### 目标
在客户门户中实现在线付款的前端交互，集成 Stripe 支付组件。

### 需求详情

#### 1. 付款入口
在对账单明细页（`StatementView.vue`）的订单列表中：
- 有待付余额的订单行显示"付款"按钮
- 点击后打开付款弹窗

#### 2. 付款弹窗
- `components/portal/PaymentModal.vue`
- 显示信息：
  - 订单号
  - 订单总额
  - 已付款金额
  - 本次最大可付金额（= 余额）
- 表单输入：
  - 付款金额（默认填充全部余额，允许部分付款）
  - 金额验证：> 0 且 <= 余额
- 付款方式选择：
  - 信用卡/借记卡（Stripe Elements）
  - 后续可扩展 PayPal 等
- 提交流程：
  1. 调用 `POST /api/v1/portal/payments/initiate` 获取 `client_secret`
  2. 使用 Stripe.js `confirmCardPayment(client_secret)` 完成支付
  3. 显示支付结果（成功/失败）
  4. 成功后自动刷新对账单数据

#### 3. 支付状态展示
- 付款中（Loading 状态）：显示进度指示器，禁止重复提交
- 付款成功：绿色成功提示，自动刷新对账数据
- 付款失败：红色错误提示，显示失败原因，允许重试
- 处理中（Webhook 未回调）：黄色提示"付款处理中，请稍后刷新查看"

#### 4. Stripe 集成
- 安装 `@stripe/stripe-js` 包
- 在 `frontend/.env` 增加 `VITE_STRIPE_PUBLISHABLE_KEY` 配置
- 封装 `composables/useStripe.ts`，提供 Stripe Elements 初始化和支付方法
- Stripe Elements 样式与 Ant Design Vue 保持协调

#### 5. 付款记录页增强
在 `PaymentHistoryView.vue` 中：
- 在线付款记录显示"在线付款"标签
- 支付中的记录显示黄色"处理中"状态
- 失败的记录显示红色"失败"状态，附带重试入口

### 技术要点
- Stripe.js 需以 ESM 方式加载（`loadStripe()`）
- `client_secret` 不存储于前端，仅用于当次支付流程
- 支付过程中需处理网络异常和页面刷新场景（Stripe 自带恢复机制）
- 金额计算使用 Decimal 精度处理，避免浮点误差

### 验收标准
- [ ] 客户可从对账单页面发起在线付款
- [ ] 付款金额验证正确（不超过余额、大于 0）
- [ ] 信用卡信息通过 Stripe Elements 安全采集（PCI 合规）
- [ ] 支付成功后对账数据实时更新
- [ ] 支付失败有明确的错误提示
- [ ] 支付过程中有 Loading 状态，不可重复提交

### 相关文件
- `frontend/src/views/portal/StatementView.vue` — 对账单页（Issue #4 新增）
- `frontend/src/views/portal/PaymentHistoryView.vue` — 付款记录页（Issue #4 新增）
- `frontend/src/api/portal.ts` — 门户 API 模块（Issue #4 新增）
