# feat: 出库单批量操作支持

## 背景

当前系统的出库操作通过发货单（Shipment）触发库存扣减（`DeductInventoryHandler`），每次出库需要逐条处理。`OutboundRecord` 实体是关联到单个发货单的出库记录，不支持独立的批量出库操作。仓库管理人员在处理多笔出库时效率低下。

## 需求描述

为出库操作增加批量能力，支持批量选择出库单进行确认、导出、打印等操作，并支持脱离发货单的独立出库场景。

## 详细设计

### 1. 领域层改造

**增强 `OutboundRecord` 实体**：
- 当前 `OutboundRecord` 是 `Entity`（非聚合根），仅作为发货出库的附属记录
- 提升为 `AggregateRoot`，支持独立生命周期
- 新增 `status` 字段：`PENDING`（待确认）→ `CONFIRMED`（已确认/已出库）→ `CANCELLED`（已取消）
- 新增 `confirm()` 方法：确认出库，触发库存扣减
- 新增 `cancel()` 方法：取消出库，触发库存恢复
- 新增 `remark` 字段

**新增领域事件**：
- `OutboundConfirmed` — 出库确认事件
- `OutboundCancelled` — 出库取消事件

### 2. 应用层 — 批量操作命令

**新增命令**：
- `BatchConfirmOutboundCommand`：批量确认出库
  - 参数：`outbound_ids: list[int]`、`confirmed_by_id: int`
  - 逻辑：遍历所有出库单，逐一校验状态并确认，收集成功/失败结果
- `BatchExportOutboundCommand`：批量导出出库单
  - 参数：筛选条件（日期范围、产品、状态等）
  - 输出：Excel 文件

**新增查询**：
- `ListOutboundRecordsQuery` + `ListOutboundRecordsHandler`：出库记录列表查询
  - 支持按状态、日期范围、产品、发货单号等筛选
  - 支持分页

### 3. 接口层

**新增 API 端点**：
- `GET /api/v1/inventory/outbound` — 出库记录列表（权限：`Module.INVENTORY, Action.READ`）
- `POST /api/v1/inventory/outbound/batch-confirm` — 批量确认出库（权限：`Module.INVENTORY, Action.UPDATE`）
  - 请求体：`{ "outbound_ids": [1, 2, 3] }`
  - 响应：`{ "success_count": 2, "fail_count": 1, "failures": [{"id": 3, "reason": "..."}] }`
- `POST /api/v1/inventory/outbound/batch-export` — 批量导出出库单为 Excel（权限：`Module.INVENTORY, Action.READ`）
- `POST /api/v1/inventory/outbound/{id}/cancel` — 取消单条出库（权限：`Module.INVENTORY, Action.UPDATE`）

### 4. 前端改造

**新增出库管理页面 `views/inventory/OutboundView.vue`**：
- 出库记录列表（表格），支持多选
- 顶部操作栏：
  - "批量确认" 按钮：选中多条待确认出库单后点击
  - "批量导出" 按钮：按当前筛选条件导出 Excel
  - "批量打印" 按钮：选中多条后生成打印视图
- 筛选器：状态、日期范围、产品关键词、关联发货单
- 单行操作：查看详情、确认、取消

**改造路由**：
- 在库存管理导航下新增"出库管理"子菜单

### 5. 仓储层

**扩展 `OutboundRecordRepository` 接口**：
- `get_by_id(id: int)` — 根据 ID 获取
- `get_by_ids(ids: list[int])` — 批量获取
- `search(...)` — 搜索出库记录（支持分页、筛选）

### 6. 数据库迁移

- `outbound_records` 表新增字段：`status`（varchar, 默认 `confirmed`）、`remark`（text, nullable）、`confirmed_by_id`（integer, nullable）、`confirmed_at`（timestamp, nullable）
- 存量数据：已有出库记录 status 设为 `confirmed`

## 验收标准

- [ ] 出库管理页面可查看所有出库记录
- [ ] 支持勾选多条出库记录后一键批量确认
- [ ] 批量确认返回成功/失败明细，部分失败不影响其他记录
- [ ] 支持按筛选条件批量导出 Excel
- [ ] 支持取消未确认的出库单，库存自动恢复
- [ ] 批量操作有操作确认弹窗，防止误操作

## 影响范围

- 后端：`domain/inventory/entities/outbound_record.py`（升级为聚合根）、`application/inventory/commands.py`、`interfaces/api/v1/inventory.py`、`infrastructure/persistence/repositories/`、数据库迁移
- 前端：新增 `OutboundView.vue`、路由配置
- 关联模块：发货管理（Shipment）中原有的出库调用逻辑需保持兼容

## 标签

`feat`, `inventory`, `backend`, `frontend`, `database`
