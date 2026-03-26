# Issue #2: 客户对账单 - 后端 API

## 类型
feat

## 标签
`customer-portal`, `backend`, `reconciliation`, `high-priority`

## 依赖
- Issue #1（客户门户认证体系）

## 描述

### 背景
客户需要能够查看自己所有订单的欠款情况，包括每笔订单的总额、已付款、应收余额，以及汇总统计。当前系统虽有 `PaymentSummary`（按单笔订单汇总），但缺乏面向客户维度的对账单聚合能力。

### 目标
提供客户维度的对账单查询 API，支持按客户汇总所有订单的应收/已收/余额信息。

### 需求详情

#### 1. 对账单查询服务（Application 层）
在 `application/` 下新建 `reconciliation`（或扩展 `payment`）模块：
- `CustomerStatementQuery` — 按客户查询对账单
- `CustomerStatementDTO` — 对账单数据传输对象

#### 2. API 端点（客户门户）
- `GET /api/v1/portal/statement` — 获取当前客户的对账单
  - 自动根据 Token 中的 `customer_id` 筛选
  - 支持参数：`start_date`、`end_date`（按订单创建日期筛选）、`status`（筛选订单状态）
  - 返回数据结构：
    ```json
    {
      "customer_name": "ABC Trading Co.",
      "statement_date": "2026-03-23",
      "currency": "USD",
      "summary": {
        "total_orders": 15,
        "total_amount": 150000.00,
        "total_paid": 120000.00,
        "total_balance": 30000.00
      },
      "orders": [
        {
          "order_no": "SO-2026-001",
          "order_date": "2026-01-15",
          "status": "shipping",
          "total_amount": 10000.00,
          "paid_amount": 8000.00,
          "balance": 2000.00,
          "currency": "USD",
          "payments": [
            {
              "payment_no": "PAY-2026-001",
              "amount": 5000.00,
              "payment_date": "2026-01-20",
              "bank_reference": "TT20260120"
            }
          ]
        }
      ]
    }
    ```

#### 3. API 端点（内部管理）
- `GET /api/v1/reconciliation/customers` — 获取所有客户的应收汇总列表
  - 支持搜索客户名称、按余额排序
  - 权限要求：`Module.PAYMENT, Action.READ`
- `GET /api/v1/reconciliation/customers/{customer_id}/statement` — 获取指定客户的对账单
  - 与门户端返回相同数据结构，供内部员工查看

#### 4. 对账单导出（预留）
- 预留 PDF/Excel 导出接口 `GET /api/v1/portal/statement/export`
- 具体实现可作为后续迭代

### 技术要点
- 复用现有 `PaymentMatchingService.calculate_summary()` 逻辑
- 查询需要跨 `sales_orders`、`payments` 表联合查询，注意性能优化（考虑数据库索引）
- 对账单按币种分组（同一客户可能有 USD 和 CNY 订单）
- 遵循 CQRS 模式：对账单为纯查询，不涉及命令

### 验收标准
- [ ] 客户登录门户后可查看自己的所有订单及付款情况
- [ ] 对账单数据准确：每笔订单的 `total_amount - paid_amount = balance`
- [ ] 汇总数据正确：`summary.total_balance = sum(orders[].balance)`
- [ ] 支持按日期范围和订单状态筛选
- [ ] 内部员工可查看任意客户的对账单
- [ ] API 响应时间 < 500ms（常规数据量）

### 相关文件
- `backend/app/domain/payment/services/payment_matching.py` — 收款核销服务（含 PaymentSummary）
- `backend/app/interfaces/api/v1/payments.py` — 现有收款 API
- `backend/app/domain/sales/aggregates/sales_order.py` — 销售订单（含 balance、paid_amount）
- `backend/app/infrastructure/persistence/repositories/payment_repository.py` — 收款仓储
