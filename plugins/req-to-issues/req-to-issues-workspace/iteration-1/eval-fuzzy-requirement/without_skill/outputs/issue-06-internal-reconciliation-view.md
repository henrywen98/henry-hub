# Issue #6: 内部管理 - 客户应收对账视图

## 类型
feat

## 标签
`backend`, `frontend`, `reconciliation`, `medium-priority`

## 依赖
- Issue #2（客户对账单 API）

## 描述

### 背景
当前系统的收款管理（`/finance`）是按收款记录维度展示，缺乏按客户维度的应收汇总视图。内部员工（尤其是财务和业务人员）需要快速了解每个客户的欠款情况，便于催款和对账。

### 目标
在内部管理系统中新增客户应收对账页面，供内部员工查看所有客户的欠款汇总和明细。

### 需求详情

#### 1. 客户应收汇总页
- 路由：`/finance/reconciliation`
- `views/finance/ReconciliationView.vue`
- 顶部汇总卡片：
  - 总应收客户数（有未结清余额的客户数）
  - 总应收金额（按币种分组）
  - 已逾期金额（超过预计交货日 30 天仍有余额的）
- 客户应收列表表格：
  | 客户名称 | 订单数 | 总金额(USD) | 已付款 | 应收余额 | 最近付款日 | 操作 |
  |---------|-------|------------|-------|---------|----------|------|
  - 支持按客户名称搜索
  - 支持按余额排序（默认余额降序）
  - "操作" 列：查看对账单明细
- 点击客户名称或"查看"按钮 → 进入该客户的对账单明细页

#### 2. 单客户对账明细页
- 路由：`/finance/reconciliation/:customerId`
- `views/finance/CustomerStatementView.vue`
- 页面顶部：客户名称 + 联系信息
- 汇总卡片：总额、已付、余额
- 订单明细表格（同 Issue #4 的对账单表格结构）
- 每个订单可展开查看付款记录明细
- 支持打印对账单（复用 `components/print/` 打印组件体系）

#### 3. 路由配置
```typescript
{
  path: '/finance/reconciliation',
  name: 'reconciliation',
  children: [
    { path: '', name: 'reconciliation-list' },
    { path: ':customerId', name: 'customer-statement' }
  ]
}
```
- 权限控制：`module: 'payment'`（复用收款模块的 READ 权限）

#### 4. 侧边栏导航
- 在"财务管理"导航组下新增"客户对账"菜单项
- 位于"收款核销"之后

### 技术要点
- 复用 Issue #2 提供的 `/api/v1/reconciliation/` 内部管理 API
- 对账明细页的打印功能复用 `components/print/PrintPageLayout` 等公共组件
- 列表页金额显示需使用千分位格式化
- 考虑多币种场景：同一客户的 USD 和 CNY 订单分别汇总显示

### 验收标准
- [ ] 内部员工可在"客户对账"页面看到所有客户的应收汇总
- [ ] 可按客户名称搜索、按余额排序
- [ ] 点击客户可查看该客户的对账单明细
- [ ] 对账单明细支持展开查看付款记录
- [ ] 对账单支持打印
- [ ] 权限控制正确：需要 PAYMENT.READ 权限

### 相关文件
- `frontend/src/router/index.ts` — 路由配置（需扩展 `/finance` 子路由）
- `frontend/src/views/finance/PaymentListView.vue` — 现有收款列表（参考样式）
- `frontend/src/components/print/` — 打印组件（复用）
- `backend/app/interfaces/api/v1/payments.py` — 现有收款 API（参考）
