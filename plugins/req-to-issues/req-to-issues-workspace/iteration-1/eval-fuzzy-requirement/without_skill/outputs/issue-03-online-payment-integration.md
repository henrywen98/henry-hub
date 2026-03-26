# Issue #3: 在线付款 - 支付网关集成（后端）

## 类型
feat

## 标签
`customer-portal`, `backend`, `payment`, `high-priority`

## 依赖
- Issue #1（客户门户认证体系）
- Issue #2（客户对账单 API）

## 描述

### 背景
当前系统的收款流程是内部员工手工录入银行到账记录（`Payment` 聚合根），客户无法自助在线付款。需要集成第三方支付网关，使客户可以在对账页面直接在线支付欠款。

### 目标
在 Payment 限界上下文中引入在线付款能力，集成支付网关（如 Stripe），支持客户通过门户在线付款。

### 需求详情

#### 1. 领域层扩展
- `Payment` 聚合根增加字段：
  - `payment_method`: 值对象，枚举值 `BANK_TRANSFER`（线下转账，现有模式）| `ONLINE`（在线支付）
  - `payment_channel`: 字符串，记录支付渠道（如 `stripe`、`paypal`）
  - `channel_transaction_id`: 第三方交易 ID
  - `payment_status`: 值对象，枚举值 `PENDING` | `COMPLETED` | `FAILED` | `REFUNDED`
  - 现有的 Payment 记录默认 `payment_method=BANK_TRANSFER`, `payment_status=COMPLETED`
- 新增领域事件：`OnlinePaymentInitiated`、`OnlinePaymentCompleted`、`OnlinePaymentFailed`

#### 2. 支付网关适配器（Infrastructure 层）
- 在 `infrastructure/external/` 下新增 `payment_gateway/` 模块
- 定义抽象接口 `PaymentGateway`（策略模式，便于切换支付渠道）：
  ```python
  class PaymentGateway(ABC):
      async def create_payment_intent(self, amount: Decimal, currency: str, metadata: dict) -> PaymentIntent
      async def verify_webhook(self, payload: bytes, signature: str) -> WebhookEvent
  ```
- 首期实现 `StripeGateway`（Stripe 在外贸场景中广泛使用，支持多币种）
- 配置通过环境变量注入：`STRIPE_SECRET_KEY`、`STRIPE_WEBHOOK_SECRET`

#### 3. 客户门户付款 API
- `POST /api/v1/portal/payments/initiate` — 发起在线付款
  - 请求体：`{ "sales_order_id": int, "amount": Decimal, "currency": str }`
  - 业务规则：
    - 付款金额不超过该订单应收余额
    - 币种与订单币种一致
  - 返回：`{ "payment_id": int, "client_secret": str }`（供前端调起支付组件）
- `POST /api/v1/portal/payments/webhook` — 支付网关回调
  - 接收支付结果通知（Webhook）
  - 验签后更新 Payment 状态
  - 成功则触发 `OnlinePaymentCompleted` 事件，自动更新销售订单 `paid_amount`
- `GET /api/v1/portal/payments` — 查看自己的付款记录
  - 按客户 `customer_id` 筛选

#### 4. 数据库迁移
- `payments` 表新增字段：`payment_method`、`payment_channel`、`channel_transaction_id`、`payment_status`
- 存量数据默认值：`payment_method='BANK_TRANSFER'`、`payment_status='COMPLETED'`
- 需确保向后兼容，不影响现有内部收款流程

### 技术要点
- 支付网关回调需幂等处理（重复 Webhook 不重复入账）
- 回调接口无需认证（由 Webhook 签名验证保障安全）
- 在线付款状态为 `PENDING` 时不计入 `paid_amount`，仅 `COMPLETED` 才计入
- 遵循依赖倒置：domain 层定义接口，infrastructure 层实现
- 支付配置（API Key 等）通过 `core/config.py` 的 Pydantic Settings 管理

### 验收标准
- [ ] 客户可在门户发起在线付款请求
- [ ] 支付网关回调正确更新付款状态
- [ ] 付款成功后自动更新销售订单已收金额和状态
- [ ] 存量线下收款数据不受影响
- [ ] Webhook 幂等：相同事件重复推送不会重复入账
- [ ] 单元测试覆盖支付流程（Mock 支付网关）
- [ ] 集成测试验证 Webhook 签名验证

### 相关文件
- `backend/app/domain/payment/aggregates/payment.py` — Payment 聚合根（需扩展）
- `backend/app/domain/payment/events/` — 领域事件（需新增）
- `backend/app/infrastructure/external/` — 外部服务适配器（需新增支付网关）
- `backend/app/core/config.py` — 配置管理
- `backend/app/interfaces/api/v1/payments.py` — 现有收款 API（参考）
