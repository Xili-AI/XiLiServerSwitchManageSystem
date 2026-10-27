# 贡献指南

## 分支与提交

- 分支：`feat/<scope>`、`fix/<scope>`、`docs/<scope>`、`refactor/<scope>`、`test/<scope>`、`chore/<scope>`。
- 提交信息：`<type>(<scope>): <subject>`，例如：
  - `feat(services): add path routing fallback`
  - `fix(auth): revoke tokens after password change`
  - `docs(deploy): document wildcard DNS`
- 一次提交只做一件事；不要提交 `.env`、真实密钥、运行日志、数据库文件。
- 禁止强推主分支；合并前必须通过测试与评审。

## 本地检查

```powershell
# 后端
$env:PYTHONPATH = "$PWD\src\backend"
pytest

# 前端
cd src\frontend
npm run build
npm run test:unit
```

## 后端规范

- 分层：`api/` 只做参数、鉴权、调用 Service、返回 JSON；`services/` 负责业务与事务；`utils/` 负责通用工具与外部客户端；`models/` 只做 ORM 与序列化。
- 配置只从 `app.config` 读取，禁止在业务代码直接访问 `os.environ`。
- 禁止嵌套函数（装饰器除外）；禁止 `_` / `__` 前缀命名普通标识符（dunder 与 `_` 占位符除外）。
- Service 中只调用一次的逻辑直接内联；通用逻辑移到 Utils。
- API 响应统一 `{code, message, data}`；错误用自定义异常 + 全局处理器。
- 所有新增接口必须有参数校验、权限判断和审计（涉及写操作时）。

## 前端规范

- `<template>` → `<script setup lang="ts">` → `<style scoped>`。
- 组件文件 PascalCase；页面按模块放在 `views/<module>/`；公共组件放在 `components/`。
- 请求统一走 `src/api/`，页面不直接调用 axios/fetch。
- 业务状态放 Pinia；页面只做展示与交互编排。
- 样式优先使用 `styles/tokens.css` 的变量；不要在组件里硬编码品牌色。
- 新增动效必须在 `prefers-reduced-motion` 下可关闭。

## 新功能流程

新模块先进入 `sandbox/test_<模块名>/`，完成 API 文档、测试与评审后再迁入正式目录，并在 `tests/` 补充长期测试。详见 `sandbox/README.md`。

## 安全

- 不提交密钥、令牌、真实用户数据。
- 新增外部请求必须考虑 SSRF；目标地址校验在服务端完成。
- 删除文件、数据、容器前必须备份并明确确认。
- 漏洞报告请参阅 `SECURITY.md`。
