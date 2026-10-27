# Docker 资产

所有容器相关的东西都在本目录，按用途分组，互不嵌套：

```text
docker/
├── app/                  # 本系统的 Compose、镜像、环境变量
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── .env / .env.sample
│   └── README.md
├── nginx/                # 网关 Nginx 配置（由 app/Dockerfile.frontend 复制进镜像）
│   ├── nginx.conf
│   ├── default.conf
│   ├── 00-dynamic-hosts.conf
│   └── entrypoint.sh
├── runtime/              # 网关动态路由缓存（挂载进容器，可再生成）
├── data/                 # demo 服务数据（File Browser 等）
├── logs/                 # 容器日志
└── legacy/               # 旧版迁移素材（不参与构建）
```

## 为什么 `.dockerignore` 还在仓库根目录

Docker 只从**构建上下文根目录**读取 `.dockerignore`。本项目的构建上下文是仓库根目录
（compose 里 `context: ../..`），所以 `.dockerignore` 必须留在根目录，不能移进 `docker/`。

## 常用命令

```powershell
# 仓库根目录
docker compose -f docker/app/docker-compose.yml up -d --build
docker compose -f docker/app/docker-compose.yml ps

# 或进入 app 目录（该目录的 .env 会被自动读取）
cd docker/app
docker compose up -d --build
```
