# API 文档

## 约定

- Base URL：`/api`
- 认证：`Authorization: Bearer <JWT>`
- 请求/响应：`application/json; charset=utf-8`
- 统一响应结构：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

- HTTP 状态码与 `code` 保持一致：200/201/400/401/403/404/409/429/500。
- 错误响应：

```json
{
  "code": 400,
  "message": "目标地址只支持 http:// 或 https://"
}
```

## 公开接口

### GET /api/health

无需认证，供隧道探活与登录页状态显示。

```json
{
  "code": 200,
  "message": "服务正常",
  "data": {
    "status": "ok",
    "version": "1.0.0",
    "site_name": "矽励科技服务网关管理系统",
    "time": "2026-10-26T15:30:00"
  }
}
```

### GET /api/public/info

无需认证，返回站点与入口元数据。

```json
{
  "code": 200,
  "data": {
    "site_name": "矽励科技服务网关管理系统",
    "version": "1.0.0",
    "base_domain": "localhost",
    "public_scheme": "http",
    "public_port": "8080"
  }
}
```

## 认证

### POST /api/auth/login

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 管理员账号 |
| password | string | 是 | 密码 |

成功：

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "<JWT>",
    "user": {
      "id": 1,
      "username": "admin",
      "display_name": "系统管理员",
      "is_admin": true
    }
  }
}
```

失败：

- `400`：用户名或密码为空
- `401`：账号或密码错误 / 账号锁定
- `429`：登录尝试过于频繁

### POST /api/auth/logout

需要认证。递增 `token_version`，当前及所有旧令牌立即失效。

### GET /api/auth/profile

需要认证。返回当前用户资料（不包含密码哈希）。

### POST /api/auth/change-password

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| old_password | string | 是 | 当前密码 |
| new_password | string | 是 | 至少 8 位，含字母和数字 |

成功后旧令牌全部失效，需要重新登录。

## 服务注册表

### GET /api/services

需要认证。管理员看到全部服务；普通用户只看到被授权且已启用的服务，`stats` 也按可见范围统计。

```json
{
  "code": 200,
  "data": {
    "services": [
      {
        "id": "8d6e...",
        "name": "Portainer",
        "slug": "portainer",
        "target_url": "http://portainer:9000",
        "entry_path": "",
        "description": "容器启停、日志与终端",
        "color": "#13b5ea",
        "icon": "container",
        "mode": "auto",
        "is_enabled": true,
        "sort_order": 10,
        "is_online": true,
        "last_checked_at": "2026-10-26T15:31:00+08:00",
        "latency_ms": 2,
        "last_error": null,
        "public_url": "http://portainer.localhost:8080/",
        "path_url": "/p/portainer/"
      }
    ],
    "stats": {
      "total": 2,
      "enabled": 2,
      "online": 2,
      "offline": 0,
      "unknown": 0,
      "average_latency_ms": 2
    },
    "settings": {}
  }
}
```

### POST /api/services

需要管理员。

```json
{
  "name": "Internal API",
  "slug": "internal-api",
  "target_url": "http://host.docker.internal:8181",
  "entry_path": "",
  "description": "内网 API",
  "color": "#5fd3f3",
  "icon": "server",
  "mode": "auto",
  "is_enabled": true
}
```

- `target_url` 只允许协议、主机和端口，不能带路径、查询参数或锚点。
- `entry_path` 可选，用于打开位于子路径的 UI，例如 Qdrant 的 `/dashboard`；必须以单个 `/` 开头。
- `slug` 唯一，保留字（`api`、`p`、`static` 等）不可用。
- 成功返回 `201`，并附带 `gateway.synced` 状态。

### GET /api/services/{id}

需要认证。

### PUT /api/services/{id}

需要管理员，字段同创建。

### DELETE /api/services/{id}

需要管理员。只删除面板记录，不会停止或删除实际容器。

```json
{
  "code": 200,
  "data": {
    "deleted_id": "8d6e...",
    "gateway": { "synced": true }
  }
}
```

### POST /api/services/{id}/check

需要认证。立即探测一次目标服务。

### PUT /api/services/reorder

需要管理员。

```json
{ "ordered_ids": ["id-1", "id-2"] }
```

## 用户与授权

### GET /api/users

需要管理员。返回所有账号及服务授权：

```json
{
  "code": 200,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "admin",
        "display_name": "系统管理员",
        "is_admin": true,
        "is_active": true,
        "service_ids": [],
        "last_login_at": "2026-10-27T12:00:00+08:00"
      },
      {
        "id": 2,
        "username": "tzgml",
        "display_name": "TZGML",
        "is_admin": false,
        "is_active": true,
        "service_ids": ["8d6e..."],
        "last_login_at": null
      }
    ]
  }
}
```

管理员的 ``service_ids`` 恒为空数组（默认拥有全部服务）。

### POST /api/users

需要管理员。密码至少 8 位且同时包含字母和数字。

```json
{
  "username": "tzgml",
  "display_name": "TZGML",
  "email": "tzgml@example.com",
  "password": "Tz12345678",
  "is_admin": false,
  "is_active": true,
  "service_ids": ["8d6e..."]
}
```

### PUT /api/users/{id}

需要管理员。字段同上；``password`` 留空表示不修改，修改密码会让该用户已签发的令牌立即失效。
最后一个启用的管理员不能被降级或停用。

### DELETE /api/users/{id}

需要管理员。不能删除当前登录用户，也不能删除最后一个启用的管理员。

### 授权规则

- 普通用户的 ``GET /api/services`` 只返回 ``service_ids`` 中的服务，``GET /api/services/{id}`` 对未授权服务返回 404。
- 非管理员调用服务的创建、修改、删除、检测、排序接口返回 403。
- 网关 ``/p/<标识>/`` 路由本身不参与面板鉴权，仍由服务自身登录保护。

## 系统

### GET /api/system/info

需要认证。返回服务、统计、设置、网关状态和最近 12 条审计记录。

### GET /api/system/settings

需要认证。

### PUT /api/system/settings

需要管理员。字段均可选：

```json
{
  "base_domain": "example.com",
  "public_scheme": "https",
  "public_port": "",
  "health_interval": 30,
  "skip_tls_verify": false,
  "site_name": "矽励科技服务网关管理系统"
}
```

### POST /api/system/gateway/sync

需要管理员。强制重新生成 Nginx 路由片段。

### GET /api/system/gateway/config

需要管理员。返回生成的 `hosts` / `paths` 文本，用于设置页预览与排障。

### GET /api/system/audit-logs?limit=20

需要管理员。返回最近的审计记录。

```json
{
  "code": 200,
  "data": {
    "logs": [
      {
        "id": 12,
        "username": "admin",
        "action": "service.create",
        "resource_type": "service",
        "resource_id": "8d6e...",
        "detail": "name=Portainer, slug=portainer",
        "ip_address": "127.0.0.1",
        "created_at": "2026-10-26T15:31:00+08:00"
      }
    ]
  }
}
```

## 错误码

| HTTP | 场景 |
| --- | --- |
| 400 | 参数缺失、格式错误、密码强度不足 |
| 401 | 未登录、令牌过期/撤销、账号或密码错误 |
| 403 | 需要管理员权限 |
| 404 | 服务/接口不存在 |
| 409 | 服务标识冲突 |
| 429 | 登录限流 |
| 500 | 未预期异常；查看后端日志 |
