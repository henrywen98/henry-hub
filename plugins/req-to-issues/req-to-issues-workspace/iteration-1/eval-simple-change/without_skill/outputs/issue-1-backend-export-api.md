# Issue 1: 后端 - 新增销售订单列表导出 Excel API

## 描述

在销售订单模块新增一个导出 Excel 的 API 端点，支持按当前筛选条件（状态、客户、搜索关键词、日期范围、审核状态）查询所有匹配的订单数据并生成 `.xlsx` 文件返回给前端下载。

## 背景

目前销售订单列表页支持按状态、客户、日期范围、订单号/PO号搜索等条件筛选，但不支持将筛选结果导出为 Excel 文件。业务上需要将订单数据导出用于内部报表、客户对账等场景。

## 需求详情

### 1. 新增 API 端点

在 `backend/app/interfaces/api/v1/sales_orders.py` 中新增：

```
GET /api/v1/sales-orders/export
```

**查询参数**（与列表接口保持一致）：
- `status`: 订单状态筛选 (created/purchasing/picked_up/in_warehouse/shipping/completed)
- `customer_id`: 客户ID筛选
- `search`: 搜索关键词（订单号/PO号）
- `date_from`: 起始日期 (YYYY-MM-DD)
- `date_to`: 截止日期 (YYYY-MM-DD)
- `approval_status`: 审核状态筛选 (pending/approved/rejected)

**权限**：`require_permission(Module.SALES, Action.READ)`

**响应**：`StreamingResponse`，MIME 类型为 `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

### 2. 查询逻辑

- 复用现有的 `SalesQueryHandler.list_orders()` 查询方法
- 导出时不分页，一次性获取所有匹配数据（设置 `limit` 为较大值，如 10000，并在注释中说明上限）
- 复用 `_fetch_order_extra_fields()` 获取客户名称、创建人等关联数据

### 3. Excel 生成

在 `backend/app/interfaces/templates/` 下新建 `sales_order_export.py`，参考已有的 `payment_request_export.py` 风格，使用 `openpyxl` 生成 XLSX 文件。

**导出列**：
| 列名 | 字段 |
|------|------|
| 订单流水号 | order_no |
| PO号 | po_number |
| 客户 | customer_name |
| 状态 | status（显示中文标签） |
| 审核状态 | approval_status（显示中文标签） |
| 币种 | currency |
| 订单金额 | total_amount |
| 已收款 | paid_amount |
| 未收款 | total_amount - paid_amount |
| 创建人 | created_by_name |
| 创建时间 | created_at（格式化为 YYYY-MM-DD HH:mm） |

**样式要求**：
- 表头行加粗，带背景色
- 金额列右对齐，保留 2 位小数
- 列宽自适应内容
- 状态值使用中文标签（如 "已创建"、"采购中"）

### 4. 文件命名

响应头中的文件名格式：`销售订单_{导出日期}.xlsx`，如 `销售订单_2026-03-23.xlsx`

## 涉及文件

- `backend/app/interfaces/api/v1/sales_orders.py` — 新增 export 端点
- `backend/app/interfaces/templates/sales_order_export.py` — 新建，Excel 生成逻辑
- `backend/app/application/sales/queries.py` — 可能需要新增导出专用查询（或复用 ListOrdersQuery）

## 参考实现

- `backend/app/interfaces/api/v1/payment_requests.py` 中的 `export_payment_request` 端点
- `backend/app/interfaces/templates/payment_request_export.py` 中的 openpyxl 使用方式

## 验收标准

- [ ] `GET /api/v1/sales-orders/export` 在无筛选条件时导出全部订单
- [ ] 支持所有筛选参数（status, customer_id, search, date_from, date_to, approval_status）
- [ ] 导出的 Excel 文件可正常打开，列名和数据正确
- [ ] 状态值显示为中文标签
- [ ] 金额格式正确（2位小数）
- [ ] 需要 `SALES.READ` 权限，未授权返回 403
- [ ] 大数据量（1000+订单）导出性能可接受（< 5秒）
