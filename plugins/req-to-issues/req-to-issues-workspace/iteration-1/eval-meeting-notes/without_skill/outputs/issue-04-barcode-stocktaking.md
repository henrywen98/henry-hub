# feat: 扫码盘点功能 — 库存盘点模块

## 背景

当前系统没有盘点功能，仓库盘点完全依赖手动操作（纸质记录后手动核对系统数据），效率低、易出错。系统现有 `InventoryBatch` 聚合根管理库存批次数据，但缺乏与实物核对的盘点流程支撑。

## 需求描述

新增库存盘点模块，支持创建盘点任务、通过扫描产品条码/批次条码快速录入实盘数量、自动计算盘盈盘亏、审批后自动调整库存。

## 详细设计

### 1. 领域层 — 新增盘点限界上下文

考虑到盘点是库存域的一个子流程，建议在 `domain/inventory/` 下扩展：

**新增聚合根 `StocktakingOrder`**（盘点单）：
- 字段：`id`、`stocktaking_no`（盘点单号）、`status`、`stocktaking_date`、`remark`、`created_by_id`、`approved_by_id`、`approved_at`
- 状态流转：`DRAFT`（草稿）→ `IN_PROGRESS`（盘点中）→ `PENDING_APPROVAL`（待审批）→ `APPROVED`（已审批）/ `REJECTED`（已驳回）
- 方法：
  - `start()` — 开始盘点
  - `add_item(product_spec_id, batch_number, system_quantity, actual_quantity)` — 添加盘点明细
  - `submit()` — 提交审批
  - `approve()` — 审批通过，发布 `StocktakingApproved` 事件
  - `reject(reason)` — 驳回

**新增实体 `StocktakingItem`**（盘点明细）：
- 字段：`id`、`stocktaking_order_id`、`product_id`、`product_spec_id`、`batch_number`、`system_quantity`（系统库存）、`actual_quantity`（实盘数量）、`difference`（差异 = 实盘 - 系统）、`remark`
- 自动计算 `difference` 属性

**新增领域事件**：
- `StocktakingApproved` — 盘点审批通过，触发库存调整

### 2. 应用层

**命令**：
- `CreateStocktakingCommand` — 创建盘点单（可选范围：全部产品 / 指定产品 / 指定库位）
- `ScanStocktakingItemCommand` — 扫码录入盘点明细
  - 参数：`stocktaking_order_id`、`barcode`（产品条码或批次条码）、`actual_quantity`
  - 逻辑：解析条码 → 查找产品规格/批次 → 获取系统库存 → 创建盘点明细
- `SubmitStocktakingCommand` — 提交盘点单
- `ApproveStocktakingCommand` — 审批盘点单
- `RejectStocktakingCommand` — 驳回盘点单

**事件处理器**：
- `StocktakingApprovedHandler`：监听 `StocktakingApproved`
  - 遍历盘点明细，对有差异的项执行库存调整
  - 盘盈（difference > 0）：增加库存，记录流水类型 `STOCKTAKING_IN`
  - 盘亏（difference < 0）：减少库存，记录流水类型 `STOCKTAKING_OUT`

**查询**：
- `ListStocktakingOrdersQuery` — 盘点单列表
- `GetStocktakingOrderDetailQuery` — 盘点单详情（含明细和差异统计）

### 3. 条码支持

**条码解析服务** `domain/inventory/services/barcode_service.py`：
- `parse_barcode(barcode: str)` → `BarcodeInfo(product_id, product_spec_id, batch_number)`
- 支持的条码格式：
  - 产品 SKU 条码：直接匹配 `Product.sku` 或 `Product.barcode`
  - 批次条码：格式如 `{SKU}-{BATCH_NUMBER}`，拆分后匹配
  - 自定义格式：支持配置条码规则

**产品主数据扩展**：
- `Product` 模型增加 `barcode` 字段（用于存储 EAN/UPC 等标准条码）
- 产品管理界面增加条码字段

### 4. 接口层

**新增 API 端点**：
- `POST /api/v1/inventory/stocktaking` — 创建盘点单（权限：`INVENTORY, CREATE`）
- `GET /api/v1/inventory/stocktaking` — 盘点单列表（权限：`INVENTORY, READ`）
- `GET /api/v1/inventory/stocktaking/{id}` — 盘点单详情（权限：`INVENTORY, READ`）
- `POST /api/v1/inventory/stocktaking/{id}/scan` — 扫码录入（权限：`INVENTORY, UPDATE`）
- `PUT /api/v1/inventory/stocktaking/{id}/items/{item_id}` — 修改盘点明细（权限：`INVENTORY, UPDATE`）
- `POST /api/v1/inventory/stocktaking/{id}/submit` — 提交审批（权限：`INVENTORY, UPDATE`）
- `POST /api/v1/inventory/stocktaking/{id}/approve` — 审批通过（权限：`INVENTORY, APPROVE`）
- `POST /api/v1/inventory/stocktaking/{id}/reject` — 驳回（权限：`INVENTORY, APPROVE`）

### 5. 前端

**新增盘点管理页面 `views/inventory/StocktakingView.vue`**：
- 盘点单列表：状态筛选、日期范围
- 创建盘点单：选择盘点范围

**新增盘点作业页面 `views/inventory/StocktakingDetailView.vue`**：
- 顶部：盘点单信息和状态
- 扫码输入区：
  - 条码输入框（支持扫码枪自动输入，回车触发）
  - 扫码后自动弹出数量输入框，填写实盘数量后保存
- 盘点明细表格：
  - 列：产品编码、产品名称、规格、批次号、系统数量、实盘数量、差异（盘盈绿色/盘亏红色）
  - 支持手动编辑实盘数量（兼容无扫码枪场景）
- 底部汇总：已盘点项数、盘盈项数、盘亏项数、未盘点项数
- 操作按钮：提交审批、导出盘点报告

**路由配置**：
- 库存管理导航下新增"盘点管理"子菜单

### 6. 库存流水类型扩展

在 `TransactionType` 枚举中新增：
- `STOCKTAKING_IN = "stocktaking_in"` — 盘盈入库
- `STOCKTAKING_OUT = "stocktaking_out"` — 盘亏出库

在 `ReferenceType` 枚举中新增：
- `STOCKTAKING = "stocktaking"` — 盘点单

### 7. 数据库迁移

**新建表**：
- `stocktaking_orders`：`id`、`stocktaking_no`、`status`、`stocktaking_date`、`remark`、`created_by_id`、`approved_by_id`、`approved_at`、`created_at`、`updated_at`
- `stocktaking_items`：`id`、`stocktaking_order_id`（FK）、`product_id`、`product_spec_id`、`batch_number`、`system_quantity`、`actual_quantity`、`difference`、`remark`、`scanned_at`

**修改表**：
- `products` 表新增 `barcode` 字段（varchar, nullable, unique）

## 验收标准

- [ ] 可创建盘点单，选择盘点范围
- [ ] 扫码输入条码后自动识别产品并加载系统库存
- [ ] 支持手动输入实盘数量（兼容无扫码枪场景）
- [ ] 盘点明细自动计算差异，盘盈/盘亏颜色区分
- [ ] 盘点单提交后进入审批流程
- [ ] 审批通过后库存自动调整，库存流水正确记录
- [ ] 审批驳回后可修改后重新提交
- [ ] 盘点报告可导出 Excel
- [ ] 扫码输入框支持扫码枪连续扫描

## 影响范围

- 后端：`domain/inventory/`（新增聚合根 + 实体 + 事件 + 服务）、`application/inventory/`（新增命令 + 查询 + 事件处理器）、`interfaces/api/v1/`（新增路由）、`models/`（新增 ORM 模型）、`infrastructure/persistence/`（新增仓储实现 + mapper）、数据库迁移
- 前端：新增 `StocktakingView.vue` + `StocktakingDetailView.vue`、路由配置、产品管理增加条码字段
- 关联模块：产品主数据（barcode 字段）、库存流水（新增类型）

## 标签

`feat`, `inventory`, `backend`, `frontend`, `database`, `high-effort`
