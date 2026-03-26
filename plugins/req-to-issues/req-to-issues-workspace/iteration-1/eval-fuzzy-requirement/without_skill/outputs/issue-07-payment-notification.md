# Issue #7: 付款通知与提醒机制

## 类型
feat

## 标签
`customer-portal`, `backend`, `notification`, `low-priority`

## 依赖
- Issue #1（客户门户认证体系）
- Issue #3（在线付款后端 API）

## 描述

### 背景
客户付款后，内部员工需要及时知悉；同样，对于长期未付款的客户，系统需要能自动提醒。此功能为对账体系的辅助增强。

### 目标
建立付款相关的通知机制，包括内部通知和客户邮件提醒。

### 需求详情

#### 1. 在线付款成功内部通知
- 监听 `OnlinePaymentCompleted` 领域事件
- 事件处理器生成内部通知：
  - 通知目标：CEO 和 SALES 角色用户
  - 通知内容："{客户名} 在线付款 {金额} {币种}，订单号 {订单号}"
- 首期：在 Dashboard 页面以消息提示方式展示（可使用 Ant Design 的 Notification 组件）
- 后续可扩展为 WebSocket 实时推送

#### 2. 欠款提醒邮件（预留）
- 定义 `PaymentReminderService` 接口
- 业务规则：
  - 订单超过预计交货日 30 天仍有余额 → 生成提醒
  - 同一订单每 7 天最多提醒一次
- 邮件内容：对账单摘要 + 门户登录链接
- 首期仅实现逻辑框架和接口定义，实际邮件发送后续集成 SMTP/第三方邮件服务

#### 3. 付款确认回执
- 客户在线付款成功后，门户页面显示付款成功回执
- 回执包含：付款单号、金额、日期、订单号
- 支持打印/下载（PDF 格式，预留接口）

### 技术要点
- 复用现有 `EventBus` 事件发布/订阅机制
- 通知记录可暂时不落库，仅内存级通知（MVP 阶段）
- 邮件服务预留 `infrastructure/external/email_service.py` 接口

### 验收标准
- [ ] 客户在线付款成功后，内部管理系统有通知提示
- [ ] 付款提醒服务接口定义完成
- [ ] 客户付款后可查看付款回执
- [ ] 事件处理不影响主流程（静默失败 + 日志）

### 相关文件
- `backend/app/infrastructure/messaging/event_bus.py` — 事件总线
- `backend/app/domain/payment/events/` — 付款领域事件
- `frontend/src/views/dashboard/DashboardHomeView.vue` — 内部 Dashboard（通知展示）
