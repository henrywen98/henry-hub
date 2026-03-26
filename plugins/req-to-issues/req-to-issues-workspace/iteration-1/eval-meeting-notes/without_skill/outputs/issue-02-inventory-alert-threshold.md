# feat: 库存预警功能 — 安全库存与低库存告警

## 背景

当前系统缺乏库存预警机制，库存水位完全依赖人工关注，经常出现断货情况，影响订单交付。系统目前有按产品规格汇总的库存查询（`search_summary`），但没有安全库存阈值设定和主动告警能力。

## 需求描述

为每个产品规格设置安全库存阈值，当实际库存低于阈值时触发预警，在仪表盘和库存列表中醒目提示，并支持邮件/系统通知。

## 详细设计

### 1. 主数据层 — 安全库存阈值配置

**修改产品规格（ProductSpecification）**：
- 新增 `safety_stock` 字段（Decimal, 默认 0，表示不启用预警）
- 新增 `reorder_point` 字段（Decimal, 可选，补货点，默认等于 safety_stock）

**产品管理界面**：
- 在产品规格编辑中增加"安全库存"和"补货点"输入框
- 支持批量设置安全库存（导入/导出 Excel）

### 2. 领域层 — 库存预警判定

**新增领域服务** `domain/inventory/services/stock_alert_service.py`：
- `check_stock_level(product_spec_id, current_quantity, safety_stock)` → 返回预警级别
- 预警级别：`NORMAL`（正常）、`LOW`（低于补货点）、`CRITICAL`（低于安全库存）、`STOCKOUT`（零库存）

**新增领域事件**：
- `StockLevelCritical` — 库存低于安全库存事件
- `StockLevelRestored` — 库存恢复正常事件

### 3. 应用层 — 库存预警查询与事件处理

**新增查询**：
- `ListStockAlertsQuery` + `ListStockAlertsHandler`：查询所有低于安全库存的产品规格列表，支持按预警级别筛选
- 返回字段：产品信息、当前库存、安全库存、缺口数量、预警级别

**事件处理器** `application/inventory/event_handlers.py`：
- 监听 `InventoryInbounded` 和 `InventoryDeducted` 事件
- 入库/出库后检查库存水位，触发 `StockLevelCritical` 或 `StockLevelRestored` 事件

### 4. 接口层

**新增 API 端点**：
- `GET /api/v1/inventory/alerts` — 库存预警列表（权限：`Module.INVENTORY, Action.READ`）
- `GET /api/v1/inventory/alerts/summary` — 预警概要（各级别数量统计，用于仪表盘）

**修改现有端点**：
- `GET /api/v1/inventory`（库存列表）— 响应中增加 `safety_stock`、`alert_level` 字段
- `GET /api/v1/dashboard/stats`（如有仪表盘接口）— 增加库存预警统计

### 5. 前端改造

**库存列表 `InventoryListView.vue`**：
- 库存数量列增加预警标识（红色/橙色/绿色图标）
- 新增"仅显示预警"筛选按钮
- 预警行高亮显示

**新增库存预警页面 `views/inventory/StockAlertView.vue`**：
- 预警汇总看板：断货数量、低库存数量
- 预警明细列表：产品信息、当前库存、安全库存、缺口、建议补货数量
- 支持导出预警报表

**仪表盘集成**：
- Dashboard 增加库存预警卡片：显示断货/低库存产品数量
- 点击可跳转到预警详情页

### 6. 数据库迁移

- `product_specifications` 表新增字段：`safety_stock`（decimal, 默认 0）、`reorder_point`（decimal, nullable）
- 可选：新建 `stock_alert_logs` 表记录预警历史

## 验收标准

- [ ] 可为产品规格设置安全库存阈值
- [ ] 库存低于安全库存时，库存列表中对应行出现红色预警标识
- [ ] 预警列表页正确显示所有低库存产品及缺口数量
- [ ] 出库后库存降至安全库存以下时触发预警
- [ ] 入库后库存恢复到安全库存以上时预警自动解除
- [ ] 仪表盘正确显示预警统计数据
- [ ] 零库存产品标记为"断货"状态

## 影响范围

- 后端：`domain/inventory/services/`、`domain/master_data/`（ProductSpecification）、`application/inventory/`、`interfaces/api/v1/inventory.py`、数据库迁移
- 前端：`views/inventory/InventoryListView.vue`、新增 `StockAlertView.vue`、Dashboard 组件
- 关联模块：产品管理（主数据）、仪表盘

## 标签

`feat`, `inventory`, `backend`, `frontend`, `database`, `high-priority`
