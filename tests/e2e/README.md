# E2E 测试

端到端测试覆盖登录、服务创建、服务编辑、删除和 403 拦截。推荐使用 Playwright，在本目录新增：

```text
tests/e2e/
└── auth-and-services.spec.ts
```

运行前需要：

```powershell
docker compose up -d --build
```

基础地址：`http://127.0.0.1:8080`。

当前版本以 57 项后端单元/集成测试与前端纯函数测试为合并门禁；浏览器测试作为后续增强项。
