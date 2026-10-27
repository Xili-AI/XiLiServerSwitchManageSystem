# 密码与凭据来源

每个密码只有一个配置来源；`credentials.txt` 只是人工快照，可能与当前配置不一致。

| 凭据 | 配置位置 | 生效时机 | 修改方式 |
| --- | --- | --- | --- |
| 面板管理员 | `dev.backend.env` 的 `ADMIN_USERNAME` / `ADMIN_PASSWORD` | **仅数据库首次初始化** | 面板内「修改密码」，或 `docker compose -f docker/app/docker-compose.yml exec backend python scripts/reset_admin_password.py "<new-password>"` |
| 隧道密钥 | `.env` 的 `TUNNEL_SECRET` | 重启 `tunnel` 和 `gateway` 后 | 编辑 `.env`，`docker compose -f docker/app/docker-compose.yml up -d tunnel gateway` |
| Portainer | 首次访问时设置，保存在 `portainer_data` 卷 | 首次 | Portainer 界面；忘记只能清空该卷重来 |
| File Browser | 空库时首次登录 `admin/admin`；之后是 bcrypt 哈希，存在 `docker/data/filebrowser/database/filebrowser.db`（Bolt） | 首次 | File Browser 界面，或下面的 CLI 重置 |
| SQLite | 无密码，位于 `backend_data` 卷 | — | — |

## 查看当前配置

```powershell
.\scripts\show-credentials.cmd
# 或
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\show-credentials.ps1
```

脚本只读取配置里的值，不会打印数据库里已经改过的密码。

Windows PowerShell 默认禁止运行 `.ps1`（`PSSecurityException`）。`.cmd` 包装已经带了
`-ExecutionPolicy Bypass`，直接从 `.cmd` 运行即可。

## 重置 File Browser 管理员

密码是 bcrypt 哈希，无法反查；全新部署（`docker/data/filebrowser` 为空）首次登录是 `admin/admin`。
忘记时在**运行 Docker 的那台服务器**上执行（Bolt 数据库运行中会被锁，必须先停容器）：

```powershell
cd <项目目录>
docker compose -f docker/app/docker-compose.yml stop filebrowser
docker compose -f docker/app/docker-compose.yml run --rm --entrypoint /bin/filebrowser `
  filebrowser -c /config/settings.json users update admin --password "NewPass"
docker compose -f docker/app/docker-compose.yml start filebrowser
```

`docker compose -f docker/app/docker-compose.yml run` 会复用服务的卷，不需要手写 `-v` 路径。如果提示服务未启用（profile），
在 `run` 前加 `--profile demo`。容器运行时 Bolt 数据库被锁，必须先 `stop`；
也可以在 File Browser 界面里改密码。

不要执行 `filebrowser config init`：它会在容器根目录新建一个 `/filebrowser.db`，
而实际数据库是 `/config/settings.json` 里指定的 `/database/filebrowser.db`。

## 重置面板管理员

```powershell
docker compose -f docker/app/docker-compose.yml exec backend python scripts/reset_admin_password.py "<new-password>"
```

## 常见误解

- 修改 `dev.backend.env` 的 `ADMIN_PASSWORD` **不会**改变已存在管理员的密码，
  它只在数据库为空、首次创建管理员时使用。
- 面板管理员密码改过之后，`credentials.txt` 里的记录就过期了；以面板登录结果为准。
- 隧道密钥泄露等于内网可达：`TUNNEL_SECRET` 同时是 wstunnel 的路径口令，
  轮换后旧客户端立即失效。
