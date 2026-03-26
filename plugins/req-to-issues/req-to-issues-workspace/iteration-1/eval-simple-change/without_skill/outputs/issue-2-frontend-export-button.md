# Issue 2: 前端 - 销售订单列表页新增导出 Excel 按钮

## 描述

在销售订单列表页（`SalesOrderListView.vue`）的工具栏中新增一个"导出 Excel"按钮，点击后以当前筛选条件调用后端导出 API，下载 `.xlsx` 文件。

## 背景

后端已提供（或将提供，参见 Issue 1）`GET /api/v1/sales-orders/export` 接口。前端需要在列表页提供入口，让用户能够一键导出当前筛选条件下的全部订单数据。

## 需求详情

### 1. 新增 API 方法

在 `frontend/src/api/salesOrders.ts` 中新增导出函数：

```typescript
export async function exportSalesOrders(
  params: SalesOrderListParams
): Promise<Blob> {
  const response = await apiClient.get('/sales-orders/export', {
    params: { ... },
    responseType: 'blob',
  })
  return response.data
}
```

参数与 `getSalesOrders` 保持一致（去除分页参数 page/page_size）。

### 2. 列表页 UI 变更

在 `SalesOrderListView.vue` 的工具栏区域（`<template #extra>` 内，"新建订单"按钮左侧）新增导出按钮：

```html
<a-button @click="handleExport" :loading="exporting">
  <template #icon><DownloadOutlined /></template>
  导出 Excel
</a-button>
```

**按钮位置**：在搜索框和"新建订单"按钮之间。

**权限控制**：导出按钮对所有有 `SALES.READ` 权限的用户可见（即能看到列表页的用户都可以导出）。

### 3. 导出逻辑

在 `SalesOrderListView.vue` 中新增导出处理函数：

- 读取当前 store 中的筛选条件（`statusFilter`, `customerIdFilter`, `searchKeyword`, `dateFromFilter`, `dateToFilter`, `approvalStatusFilter`）
- 调用 `exportSalesOrders` API
- 将返回的 Blob 通过 `URL.createObjectURL` + 临时 `<a>` 标签触发下载
- 文件名格式：`销售订单_YYYY-MM-DD.xlsx`（使用当前日期）
- 导出过程中按钮显示 loading 状态
- 成功后显示 `message.success('导出成功')`
- 失败时显示 `message.error('导出失败')`

### 4. 参考实现

参考 `PaymentRequestListView.vue` 中的 `handleExport` 函数实现 blob 下载逻辑。

## 涉及文件

- `frontend/src/api/salesOrders.ts` — 新增 `exportSalesOrders` 函数
- `frontend/src/views/sales/SalesOrderListView.vue` — 新增导出按钮和处理逻辑

## 依赖

- Issue 1（后端导出 API）

## 验收标准

- [ ] 列表页工具栏中出现"导出 Excel"按钮，带下载图标
- [ ] 点击导出按钮后，按钮显示 loading 状态
- [ ] 导出使用当前页面的筛选条件（状态Tab、客户选择、日期范围、搜索关键词、审核状态）
- [ ] 成功下载 `.xlsx` 文件，文件名包含当前日期
- [ ] 导出失败时显示错误提示
- [ ] 无筛选条件时导出全部订单
- [ ] 导出完成后 loading 状态恢复
