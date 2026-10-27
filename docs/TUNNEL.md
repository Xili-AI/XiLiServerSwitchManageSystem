# 单隧道全协议入口（wstunnel）

目标：**只用 `frp-fog.com:27294` 这一条隧道**，在没有 DNS、没有额外端口的前提下，
访问内网全部服务（HTTP、SSH、RDP、数据库……），不再受「路径模式」和「应用不支持子路径」的限制。

## 原理

```mermaid
flowchart LR
    Client[wstunnel client<br/>本机] -->|"WSS /&lt;TUNNEL_SECRET&gt;/... "| Entry[frp-fog.com:27294<br/>唯一隧道]
    Entry --> Gateway[Nginx Gateway<br/>正则 /^[0-9a-f]{32}/]
    Gateway --> Server[wstunnel server<br/>容器内]
    Server -->|TCP| LAN[192.168.x.x:22 / :3389 / :3306 ...]
```

- 隧道入口和目标都不变，仍然只有一条隧道，仍然指向网关。
- 网关把 `/<TUNNEL_SECRET>/...` 的 WebSocket 升级请求转给 `tunnel` 容器。
- `tunnel` 容器按客户端指令直接连内网 `host:port`，所以不需要子域名、不需要泛解析。
- 客户端在本机开一个 SOCKS5（可选再加若干本地端口转发），浏览器/SSH/RDP 直接用。

## 服务端

1. 在 `.env` 里设置固定长度的密钥（**32 位小写十六进制**）：

   ```dotenv
   TUNNEL_SECRET=0123456789abcdef0123456789abcdef
   ```

   生成方式：

   ```powershell
   -join (1..16 | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })
   ```

2. 重建网关（`default.conf` 有改动）并启动隧道容器：

   ```powershell
   docker compose -f docker/app/docker-compose.yml up -d --build gateway
   docker compose -f docker/app/docker-compose.yml up -d tunnel
   docker compose -f docker/app/docker-compose.yml ps
   ```

3. 自检：

   ```powershell
   docker compose -f docker/app/docker-compose.yml logs --tail 50 tunnel
   docker exec xiliserverswitchmanagesystem-gateway nginx -t
   ```

`tunnel` 容器不发布任何宿主机端口，只在 Compose 网络内监听 `8080`。
`--restrict-http-upgrade-path-prefix` 让服务端只接受该密钥开头的连接，其他前缀一律 400。

## 客户端

在**仓库根目录**执行（`scripts\` 的相对路径只在这里成立）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tunnel-client.ps1 -Secret <TUNNEL_SECRET>
```

在其他目录执行会报 `The argument '.\scripts\tunnel-client.ps1' is not recognized...`，
改用绝对路径或下面的 `.cmd` 包装：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File E:\Projects\Other\XiLiServerSwitchManageSystem\scripts\tunnel-client.ps1 -Secret <TUNNEL_SECRET>
E:\Projects\Other\XiLiServerSwitchManageSystem\scripts\tunnel-client.cmd -Secret <TUNNEL_SECRET>
```

脚本会按需下载 `wstunnel.exe` 到 `%LOCALAPPDATA%\XiLiServerSwitchManageSystem\tunnel-client\`（走 `HTTPS_PROXY`/`HTTP_PROXY`），
然后在本机 `127.0.0.1:1080` 开 SOCKS5。也可以把密钥放进环境变量：

```powershell
$env:WSTUNNEL_SECRET = "<TUNNEL_SECRET>"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tunnel-client.ps1
```

同时映射固定端口（目标地址由网关侧解析，可以是内网 IP 或容器名）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tunnel-client.ps1 `
  -Forward 2222:192.168.1.10:22 `
  -Forward 13389:192.168.1.10:3389 `
  -Forward 13306:192.168.1.20:3306
```

### 常见用法

| 需求 | 做法 |
| --- | --- |
| 浏览器访问任意内网 Web | 代理设为 `SOCKS5 127.0.0.1:1080`，勾选「远程 DNS / socks5h」 |
| SSH | `-Forward 2222:192.168.1.10:22`，然后 `ssh -p 2222 user@127.0.0.1` |
| RDP | `-Forward 13389:192.168.1.10:3389`，然后 `mstsc /v:127.0.0.1:13389` |
| MySQL / Redis 等 | `-Forward 13306:192.168.1.20:3306`，客户端连 `127.0.0.1:13306` |
| 网关所在主机 | 目标写 `host`（脚本会换成 `host.docker.internal`） |
| 容器内服务 | 目标写 Compose 服务名：`portainer:9000`、`filebrowser:80`、`backend:5000`、`gateway:80` |

### 访问网关所在的机器

隧道服务端里的 `host.docker.internal` 指向运行 Docker 的这台机器，可以直达只监听
`127.0.0.1` 的服务（Docker Desktop 会把它转发到宿主机回环，已在本机实测）。

| 需求 | 做法 |
| --- | --- |
| 远程桌面到主机 | `-Forward 13389:host:3389`，然后 `mstsc /v:127.0.0.1:13389` |
| SSH 到主机 | `-Forward 2222:host:22`，然后 `ssh -p 2222 user@127.0.0.1` |
| 主机上的 Web 服务 | SOCKS 里访问 `http://host.docker.internal:8181` |
| 网关自身 | SOCKS 里访问 `http://host.docker.internal:8080` 或 `http://gateway/` |

能连到主机就意味着 RDP/SSH 暴露在隧道之后：隧道密钥是唯一门槛，请给主机账号设置强口令或密钥登录，
并关闭不需要的服务。

### 本地入口（每个服务一个独立 origin）

客户端启动时会带 `TUNNEL_SECRET` 请求 `GET /api/tunnel/endpoints`，为每个启用的服务
自动建立一条 `127.0.0.1:18100+N` 的本地转发，并打印端口表：

```text
[tunnel] local     http://127.0.0.1:18102/  -> pdf (192.168.1.6:8099)
```

应用在自己的根路径运行，`/assets`、`/api`、`/login` 全部落在 origin 内，不需要 base path，
也不依赖 Referer 兜底。面板卡片上的「本地」按钮直接打开这个地址。端口只监听 `127.0.0.1`；
起始端口可用 `.env` 的 `TUNNEL_LOCAL_PORT_BASE` 调整，`-NoAutoForwards` 可关闭该行为。

`-Insecure` 会关闭证书校验；默认开启 `--tls-verify-certificate`，隧道入口使用正常证书时不要加。

## 新机器部署

### 只作为客户端（最常见）

不需要 Docker，也不需要克隆整个仓库：

1. 把 `scripts\tunnel-client.ps1` 和 `scripts\tunnel-client.cmd` 拷到新机器任意目录；
2. 只需要 Windows 自带的 Windows PowerShell 5.1（`powershell.exe`）和 `curl.exe`（Win10+ 自带），不依赖 PowerShell 7；
3. 首次运行会从 GitHub 下载 `wstunnel.exe` 到 `%LOCALAPPDATA%\XiLiServerSwitchManageSystem\tunnel-client\v11.1.0\`。
   GitHub 不稳时先设代理：
   ```powershell
   $env:HTTPS_PROXY = "http://127.0.0.1:7897"
   ```
4. 在脚本所在目录运行：
   ```powershell
   .\tunnel-client.cmd -Secret <TUNNEL_SECRET>
   ```

   如果入口是自签名证书（`curl: (60) SEC_E_UNTRUSTED_ROOT`），加 `-Insecure`：

   ```powershell
   .\tunnel-client.cmd -Secret <TUNNEL_SECRET> -Insecure
   ```

   `-Insecure` 只跳过对端身份校验，流量仍然是 TLS 加密的；能修证书就优先修证书。
5. 控制台会打印端口表；浏览器打开面板后点卡片上的「本地」，或直接打开
   `http://127.0.0.1:18100+N/`。

保持这个窗口运行；关掉窗口本地入口就消失。服务端不需要任何改动，仍然只有一条隧道。

### 作为服务端（整套 XiLiServerSwitchManageSystem）

按 [DEPLOYMENT.md](DEPLOYMENT.md)：安装 Docker Desktop → 获取仓库 → 复制 `.env` 并填写
`TUNNEL_SECRET`（32 位小写十六进制）→ `docker compose -f docker/app/docker-compose.yml up -d --build` → 把 SakuraFrp
隧道的本地目标指向 `127.0.0.1:8080` → 确认 `https://<入口>/api/health` 返回 200。

## 安全

- `TUNNEL_SECRET` 就是访问凭证，等同于密码：不要提交到 Git，公开截图前先打码。
- 轮换密钥：修改 `.env` 的 `TUNNEL_SECRET` 后 `docker compose -f docker/app/docker-compose.yml up -d tunnel` 即可，网关无需重建。
- 隧道服务端默认允许连任意外部地址（内网穿透需要），所以密钥泄露等于内网可达；建议同时只在本机监听 SOCKS 端口（脚本已如此）。
- 隧道加密由 frp 入口的 TLS 提供；客户端默认校验证书。

## 排障

| 现象 | 检查 |
| --- | --- |
| 客户端报 `Invalid status code: 4xx` | frp-fog 的 HTTP vhost 没有透传 WebSocket Upgrade，或密钥不匹配 |
| 客户端连不上、超时 | 隧道是否在线、`https://frp-fog.com:27294/api/health` 是否 200 |
| 网关 502 | `docker compose -f docker/app/docker-compose.yml ps` 看 `tunnel` 是否在跑；`docker compose -f docker/app/docker-compose.yml logs tunnel` |
| 改完 `default.conf` 不生效 | 网关是构建进镜像的：`docker compose -f docker/app/docker-compose.yml up -d --build gateway` |
| 连接几分钟后断 | 客户端默认 30s 一次 WS ping；若入口有更短的 idle 超时，调小 `--websocket-ping-frequency` |
| `curl: (60) SEC_E_UNTRUSTED_ROOT` | 入口是自签名证书或证书链不完整。加 `-Insecure` 跳过校验，或给入口换成受信任的证书 |
| 客户端启动后 SOCKS 一直超时 | 同上：证书校验失败时 wstunnel 不会报错，只会反复握手。加 `-Insecure` 重试 |
