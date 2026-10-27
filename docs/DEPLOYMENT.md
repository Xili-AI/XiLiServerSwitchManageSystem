# 部署指南

## 1. 前置条件

- Docker 24+ 与 Docker Compose v2
- 一条可用的内网穿透 HTTPS 隧道
- 生产环境建议拥有一个可设置泛解析的域名
- 可选：公司内网 PyPI / npm 镜像

## 2. 配置文件

```powershell
Copy-Item .env.example .env
Copy-Item dev.backend.env.sample dev.backend.env
```

### 2.1 `.env`（Compose）

```dotenv
APP_ENV=dev
GATEWAY_PORT=8080
COMPOSE_PROFILES=demo
```

- `GATEWAY_PORT` 是隧道要指向的本机端口。
- `COMPOSE_PROFILES=demo` 会同时启动 Portainer / File Browser 示例；不需要可留空。
- 国内环境可保留 `.env.example` 中的镜像与包源配置。

### 2.2 `dev.backend.env` / `pro.backend.env`

生成密钥：

```powershell
# 任意 64 位十六进制
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Min 0 -Max 16) })
```

至少修改：

```dotenv
JWT_SECRET_KEY=<64 位随机值>
ADMIN_PASSWORD=<强密码>
CORS_ORIGINS=https://你的控制台域名
BASE_DOMAIN=example.com
PUBLIC_SCHEME=https
PUBLIC_PORT=
```

- `PUBLIC_PORT` 留空表示按协议使用 443 / 80。
- 生产环境务必设置 `SEED_DEMO_SERVICES=false`。
- `debugmode` 仅用于本地：`1` 加载 dev，`0` 加载 pro；Docker 内忽略该文件，使用 Compose 注入的环境变量。

## 3. 启动

```powershell
docker compose -f docker/app/docker-compose.yml up -d --build
docker compose -f docker/app/docker-compose.yml ps
docker compose -f docker/app/docker-compose.yml logs -f backend gateway
```

首次启动会自动：

1. 创建 SQLite 数据库（Docker volume `backend_data`）；
2. 创建管理员；
3. 可选写入 Portainer / File Browser 示例服务；
4. 生成 `docker/runtime/nginx/hosts.conf` 与 `paths.conf`；
5. 启动健康检查线程。

面板地址：

```text
http://localhost:8080
```

## 4. 隧道与域名

### 4.1 隧道

把唯一一条隧道的本地目标设置为：

```text
127.0.0.1:8080
```

如果使用其他端口，同时修改 `.env` 的 `GATEWAY_PORT`，然后：

```powershell
docker compose -f docker/app/docker-compose.yml up -d gateway
```

### 4.2 子域名（推荐）

1. 在 DNS 服务商处添加泛解析：`*.example.com` -> 隧道入口节点；
2. 在控制台「系统设置」把 `BASE_DOMAIN` 设置为 `example.com`；
3. 把 `PUBLIC_SCHEME` 设置为 `https`，`PUBLIC_PORT` 留空；
4. 保存后访问 `https://portainer.example.com`。

泛解析不会新增隧道，仍然是一条隧道。

### 4.3 没有泛解析时

使用路径模式：`https://example.com/p/<标识>/`。

网关对路径模式做了统一兼容处理，不需要为每个服务手写 nginx 配置：

- 默认剥离前缀（`strip_prefix=true`），并用 `Referer` 把应用发出的根绝对 URL（`/static/...`、`/api/...`）补回前缀；
- 上游 `Location` 统一改写为带前缀的相对地址，`Set-Cookie` 的 `Path=/` 改写为 `Path=/p/<标识>/`；
- 网关输出相对重定向（`absolute_redirect off`），`:27294` 这类非标准端口不会丢端口或协议；
- 自带前端路由的单页应用建议 `strip_prefix=false`，并把应用 base path 设为 `/p/<标识>`
  （File Browser `-b`、code-server `--server-base-path`）；
- 一个应用实例只能有一个 base path；同一应用要挂两个入口时需要两个实例；
- 仍不适配的应用把访问模式改为「直连」（origin）：不生成路由，卡片直接打开源站地址；
  远程访问需要 wstunnel 客户端（SOCKS 或端口转发）；
- 或者直接用 wstunnel 客户端按 origin 访问。

路径模式不改写响应体（不做 `sub_filter`），所以 JS 字符串里拼接的绝对路径不会被替换。

## 5. TLS

- 如果隧道服务商已经提供 HTTPS（推荐），网关只监听 HTTP，不需要证书。
- 如果希望网关自己终结 TLS，请在 `gateway` 前增加 TLS 层，或使用公司统一的反向代理；本仓库默认不处理证书，避免与隧道证书重复。

## 6. 首次登录与示例服务

1. 打开面板；
2. 使用 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 登录；
3. 进入「个人资料」立即修改密码；
4. 如果启用了 demo profile，Portainer / File Browser 会自动在线；
5. 在「服务注册表」添加其余内网服务。

目标地址示例：

| 场景 | 地址 |
| --- | --- |
| 同 Compose 网络容器 | `http://my-service:8080` |
| 宿主机服务 | `http://host.docker.internal:8181` |
| 局域网机器 | `http://192.168.1.10:8181` |

## 7. 本地开发

```powershell
# 后端
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:PYTHONPATH = "$PWD\src\backend"
python src\backend\server.py

# 前端
cd src\frontend
npm install
npm run dev
```

- 前端：`http://localhost:3000`
- 后端：`http://localhost:5000`
- 网关端口：`8080`（服务子域名入口）
- `debugmode` 决定本地加载 dev 还是 pro。

## 8. 备份与恢复

数据库在 Docker volume `backend_data`：

```powershell
docker run --rm `
  -v xiliserverswitchmanagesystem_backend_data:/data `
  -v "${PWD}:/backup" `
  alpine tar czf /backup/serverswitchmanagesystem-backend-data.tgz -C /data .
```

恢复：

```powershell
docker compose -f docker/app/docker-compose.yml down
docker run --rm `
  -v xiliserverswitchmanagesystem_backend_data:/data `
  -v "${PWD}:/backup" `
  alpine sh -c "rm -rf /data/* && tar xzf /backup/serverswitchmanagesystem-backend-data.tgz -C /data"
docker compose -f docker/app/docker-compose.yml up -d
```

`docker/runtime/nginx` 是可再生成的路由缓存，不需要备份；`docker/logs/` 可视需要归档。

## 9. 升级

```powershell
docker compose -f docker/app/docker-compose.yml build --pull
docker compose -f docker/app/docker-compose.yml up -d
```

升级前备份 `backend_data`。路由文件会由新版后端自动重新生成。

## 10. 故障排查

### 面板 502 / 网关不健康

```powershell
docker compose -f docker/app/docker-compose.yml ps
docker compose -f docker/app/docker-compose.yml logs --tail=100 backend gateway
```

- 后端不健康：检查 `dev.backend.env` / `pro.backend.env` 是否存在、JWT 密钥是否为空、数据库卷是否可写。
- 网关不健康：检查 `docker/runtime/nginx` 是否挂载、Nginx 配置是否通过 `nginx -t`。

### 新增服务后 404

1. 控制台右下角是否显示 `GATEWAY SYNCED`；
2. 点击「同步网关」；
3. 查看 `docker compose -f docker/app/docker-compose.yml logs gateway` 是否有 `routing table reloaded`；
4. 排查 `docker/runtime/nginx/hosts.conf` 是否包含目标主机名。

### 子域名无法访问

- `*.BASE_DOMAIN` 是否解析到同一条隧道；
- 服务商是否只绑定了唯一主机名；
- 浏览器是否因为证书不匹配拦截；
- 先切换到路径模式验证目标本身是否可用。

### 502 Bad Gateway

- 目标容器是否运行；
- 目标地址是否写错端口；
- 容器名是否在同一个 Compose 网络；
- 宿主机服务是否监听 `0.0.0.0`（不是仅 `127.0.0.1`）；
- Linux 下 `host.docker.internal` 依赖 `extra_hosts`，本仓库已为 backend 与 gateway 配置。

### 路径模式页面空白

- 看控制台里 404 的 URL：如果是 `/static/...`、`/api/...`，新版网关会按 `Referer` 自动兜底，先确认网关已重建；
- `strip_prefix=false` 时，应用自身的 base path 必须等于 `/p/<标识>`（File Browser `-b`、code-server `--server-base-path`）；
- 同一应用实例只能绑定一个 base path，两个入口需要两个实例；
- 应用把根路径写死在 JS 里时，路径模式无法通用修复：改用子域名模式，或用 wstunnel 客户端按 origin 访问；
- 未知的 `/p/*` 直接返回 404，不再回落面板；写死根路径的 SPA 改用「直连」模式 + 客户端本地入口。

### 登录被锁定

默认 5 次失败锁 15 分钟。等待锁定结束，或在后端容器内重置管理员密码：

```powershell
docker compose -f docker/app/docker-compose.yml exec backend python scripts/reset_admin_password.py "<new-password>"
```

### 数据库磁盘 I/O 错误

Docker Desktop 的 Windows bind mount 对 SQLite WAL 不稳定。本项目默认把数据库放在 named volume `backend_data`，不要改回 `./data:/app/data`。

## 11. 生产安全检查

- [ ] 修改初始管理员密码
- [ ] `JWT_SECRET_KEY` 使用随机 64 位值
- [ ] `SEED_DEMO_SERVICES=false`
- [ ] `CORS_ORIGINS` 限制为实际控制台域名
- [ ] 只暴露 `127.0.0.1:${GATEWAY_PORT}`，由隧道访问
- [ ] 为 Portainer / File Browser 等服务设置独立强密码
- [ ] 定期备份 `backend_data`
- [ ] 关注 `docker/logs/backend.log` 与网关访问日志
