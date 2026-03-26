# feat: 入库单审批流程

## 背景

当前系统的入库操作（`InboundRecord`）创建后立即生效，没有审批环节。仓库人员提交入库单后直接更新库存批次（`InventoryBatch`）和采购订单状态，缺乏管理层审核机制，存在数据录入错误难以追溯、责任不清等风险。

## 需求描述

为入库单增加审批流程，入库记录创建后进入"待审批"状态，审批通过后才实际更新库存和采购订单进度。

## 详细设计

### 1. 领域层改造

**新增入库状态值对象** `domain/inventory/value_objects/inbound_status.py`：
- `PENDING_APPROVAL` — 待审批（入库单创建后的初始状态）
- `APPROVED` — 已审批（审批通过，触发库存变更）
- `REJECTED` — 已驳回（审批不通过，可备注原因）

**修改 `InboundRecord` 聚合根**：
- 新增 `status` 字段，默认值为 `PENDING_APPROVAL`
- 新增 `approve()` 方法：校验当前状态为 `PENDING_APPROVAL`，状态转换到 `APPROVED`，发布 `InboundApproved` 领域事件
- 新增 `reject(reason: str)` 方法：校验当前状态为 `PENDING_APPROVAL`，状态转换到 `REJECTED`，记录驳回原因
- 新增 `rejection_reason`、`approved_by_id`、`approved_at` 字段

**新增领域事件**：
- `InboundApproved` — 入库审批通过事件（携带 inbound_record_id、product_spec_id、quantity、batch_number 等）

### 2. 应用层改造

**拆分现有 `CreateInboundHandler` 逻辑**：
- `CreateInboundHandler`：仅创建入库记录（状态为 PENDING_APPROVAL），不再直接更新库存批次和库存流水
- 新增 `ApproveInboundCommand` + `ApproveInboundHandler`：审批通过后执行库存批次创建/更新 + 库存流水记录 + 采购订单状态更新
- 新增 `RejectInboundCommand` + `RejectInboundHandler`：驳回入库单

### 3. 接口层改造

**新增 API 端点**：
- `POST /api/v1/inventory/inbound/{id}/approve` — 审批通过（权限：`Module.INVENTORY, Action.APPROVE`）
- `POST /api/v1/inventory/inbound/{id}/reject` — 驳回（权限：`Module.INVENTORY, Action.APPROVE`）

**修改现有端点**：
- `GET /api/v1/inventory/inbound` — 列表接口增加 `status` 筛选参数
- `InboundRecordResponse` 增加 `status`、`rejection_reason`、`approved_by_name`、`approved_at` 字段

### 4. 权限配置

在 `permissions.py` 的 `PERMISSION_MATRIX` 中为 `Module.INVENTORY` 增加 `Action.APPROVE`：
- `CEO` / `MANAGER`：具有审批权限
- `SUPPLY_CHAIN`：具有审批权限
- `SALES` / `STAFF`：无审批权限

### 5. 前端改造

- `InboundView.vue`：入库列表增加状态列和状态筛选器，待审批状态显示审批/驳回按钮
- 审批弹窗：确认审批或填写驳回原因
- 入库创建后提示"入库单已提交，等待审批"

### 6. 数据库迁移

- `inbound_records` 表新增字段：`status`（varchar, 默认 `pending_approval`）、`rejection_reason`（text, nullable）、`approved_by_id`（integer, nullable, FK -> users.id）、`approved_at`（timestamp, nullable）
- 存量数据迁移：已有入库记录的 status 设为 `approved`

## 验收标准

- [ ] 创建入库单后状态为"待审批"，库存不变
- [ ] 审批通过后库存批次正确更新，采购订单状态正确变更
- [ ] 驳回后入库单状态为"已驳回"，库存不变，驳回原因可查看
- [ ] 无审批权限的用户看不到审批/驳回按钮
- [ ] 入库列表可按状态筛选
- [ ] 存量数据迁移后系统正常运行

## 影响范围

- 后端：`domain/inventory/`、`application/inventory/`、`interfaces/api/v1/inventory.py`、`core/permissions.py`、数据库迁移
- 前端：`views/inventory/InboundView.vue`
- 关联模块：采购订单状态更新逻辑需延迟到审批通过后执行

## 标签

`feat`, `inventory`, `backend`, `frontend`, `database`
