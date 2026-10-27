# 本系统 Docker 资产（docker/app）

本目录只放矽励科技服务网关管理系统自己的 Docker 资产。外部依赖（Portainer、File Browser）
作为 demo profile 一起编排，但它们的代码不在本仓库。

## 文件

| 文件 | 说明 |
| --- | --- |
| `docker-compose.yml` | 本系统 compose（gateway/backend/tunnel + demo profile） |
| `Dockerfile.backend` | 后端镜像；构建上下文是仓库根目录 |
| `Dockerfile.frontend` | 前端构建 + Nginx 网关镜像；构建上下文是仓库根目录 |
| `../nginx/` | 网关配置、热加载入口、路径/子域名模板（与 `app/` 平级） |
| `.env` / `.env.sample` | Compose 变量（端口、镜像、`TUNNEL_SECRET`、demo 目录） |
| `../../dev.backend.env` | 后端运行时变量（Flask/JWT/管理员种子） |

## 用法

```powershell
# 在仓库根目录
copy docker\app\.env.sample docker\app\.env   # 首次
docker compose -f docker/app/docker-compose.yml up -d --build
docker compose -f docker/app/docker-compose.yml ps

# 或者进入本目录（.env 会被自动读取）
cd docker/app
docker compose up -d --build
```

`docker-compose.yml` 里的相对路径都以本目录为基准：
- 构建上下文 `../..`（仓库根）
- 日志 `../logs`
- 动态路由 `../runtime/nginx`
- demo 数据 `../data/filebrowser/...`

## Profiles

| profile | 服务 |
| --- | --- |
| （默认） | `gateway`、`backend`、`tunnel` |
| `demo` | `portainer`、`filebrowser`（`.env` 的 `COMPOSE_PROFILES=demo`） |

## 端口

- 只有 `gateway` 发布到宿主机：`${GATEWAY_BIND:-0.0.0.0}:${GATEWAY_PORT:-8080}->80`。
- `tunnel` 不发布端口，只在 Compose 网络内监听 `8080`。
- 隧道入口应指向 `127.0.0.1:8080`。
