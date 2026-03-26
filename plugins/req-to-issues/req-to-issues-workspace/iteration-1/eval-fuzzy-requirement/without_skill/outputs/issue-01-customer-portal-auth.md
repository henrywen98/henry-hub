# Issue #1: 客户门户 - 认证与授权体系

## 类型
feat

## 标签
`customer-portal`, `backend`, `security`, `high-priority`

## 描述

### 背景
当前系统仅支持内部员工登录（基于 `User` 模型 + JWT），客户无法独立访问系统。为实现客户对账和在线付款功能，需要建立一套面向客户的认证体系。

### 目标
为客户（Customer）建立独立的认证通道，使客户能安全登录并查看自己的对账信息。

### 需求详情

#### 1. 客户账户模型
- 在 `identity` 限界上下文中新增 `CustomerAccount` 实体（或扩展现有 `Customer` 聚合根）
- 字段包含：`customer_id`（关联主数据 Customer）、`login_email`、`password_hash`、`is_active`、`last_login_at`
- 一个 Customer 可以有多个 CustomerAccount（支持客户公司多人使用）

#### 2. 客户认证 API
- `POST /api/v1/portal/login` — 客户登录，返回 JWT Token（Token 中标识身份类型为 `customer`）
- `GET /api/v1/portal/me` — 获取当前客户信息
- `POST /api/v1/portal/change-password` — 修改密码

#### 3. 权限隔离
- 客户 Token 与内部员工 Token 区分（JWT payload 增加 `account_type: "customer" | "staff"` 字段）
- 新增 `get_current_customer` 依赖注入，用于客户门户 API 的身份验证
- 客户只能查看与自己 `customer_id` 关联的数据，绝不可跨客户查看

#### 4. 后台管理客户账户
- 在现有客户管理页面增加"门户账户"管理功能
- 支持内部员工为客户创建/启用/停用门户账户
- 首次创建时自动生成随机密码，并支持邮件通知（预留接口，邮件发送可后续实现）

### 技术要点
- 复用现有 `infrastructure/security.py` 的 JWT 和密码哈希工具
- 客户门户 API 统一放在 `/api/v1/portal/` 前缀下
- 数据库新增 `customer_accounts` 表，需创建 Alembic 迁移
- 遵循 DDD 分层架构：domain 层定义实体，application 层编排，infrastructure 层实现

### 验收标准
- [ ] 客户可通过邮箱 + 密码登录门户
- [ ] 客户登录后获得的 Token 只能访问门户 API，不能访问内部管理 API
- [ ] 内部员工可以为客户创建、启用、停用门户账户
- [ ] 单元测试覆盖认证流程和权限隔离逻辑

### 相关文件
- `backend/app/domain/identity/` — 认证上下文
- `backend/app/infrastructure/security.py` — JWT 和密码工具
- `backend/app/interfaces/api/v1/auth.py` — 现有认证路由
- `backend/app/interfaces/deps.py` — 依赖注入
- `backend/app/domain/master_data/aggregates/customer.py` — 客户聚合根
