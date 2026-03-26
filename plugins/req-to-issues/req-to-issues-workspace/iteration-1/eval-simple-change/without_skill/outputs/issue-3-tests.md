# Issue 3: 测试 - 销售订单导出 Excel 功能的单元测试和 E2E 测试

## 描述

为销售订单导出 Excel 功能编写后端单元测试和前端 E2E 测试，确保导出 API 和前端交互逻辑的正确性。

## 背景

Issue 1 和 Issue 2 实现了销售订单列表导出 Excel 的后端 API 和前端按钮。本 Issue 补充测试覆盖，保证功能的可靠性和可回归性。

## 需求详情

### 1. 后端单元测试

在 `backend/tests/unit/` 下新建 `test_sales_order_export.py`：

**Excel 生成测试**：
- 测试正常数据生成 XLSX 文件，验证文件可打开且包含正确的列头
- 测试空数据（无订单）时生成的 XLSX 文件只有表头行
- 测试状态值正确转换为中文标签
- 测试金额格式化（Decimal 精度保留）

**API 端点测试**（在 `backend/tests/` 中合适位置）：
- 测试无筛选条件时返回 200 且 Content-Type 为 xlsx
- 测试带筛选条件（status, customer_id, search）时正常返回
- 测试未认证请求返回 401
- 测试无权限用户返回 403
- 测试响应头中包含正确的文件名（Content-Disposition）

### 2. 前端 E2E 测试

在 `frontend/e2e/tests/` 下新建或扩展销售订单相关测试文件：

**导出按钮交互测试**：
- 验证导出按钮在列表页可见
- 验证点击导出按钮后触发下载（可通过拦截网络请求验证）
- 验证导出按钮在加载过程中显示 loading 状态

## 涉及文件

- `backend/tests/unit/test_sales_order_export.py` — 新建
- `frontend/e2e/tests/` 下相关测试文件 — 新建或扩展

## 依赖

- Issue 1（后端 API）
- Issue 2（前端按钮）

## 验收标准

- [ ] 后端 Excel 生成函数的单元测试全部通过
- [ ] 后端 API 端点测试覆盖正常和异常场景
- [ ] 前端 E2E 测试验证导出按钮的可见性和点击行为
- [ ] 所有测试可通过 `pytest` 和 `npm run e2e` 运行
