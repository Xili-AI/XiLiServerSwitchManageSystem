# 设计系统

XiLiServerSwitchManageSystem 的视觉方向是 **像素 + 赛博 + 工业控制台**。目标不是堆砌霓虹，而是让一个运维工具拥有清晰的信息层级、稳定的可读性和可记忆的品牌气质。

## 1. 品牌资产

| 资产 | 位置 | 用途 |
| --- | --- | --- |
| XILI-AI 字标 | `src/frontend/src/assets/brand/logo.png` | 登录页、侧栏、页脚 |
| 像素机器人 | `src/frontend/src/assets/brand/robot.png` | 登录页主视觉、空状态、错误页、网关核心 |
| Press Start 2P | `src/frontend/src/assets/fonts/PressStart2P.woff2` | 英文标题、品牌字 |
| VT323 | `src/frontend/src/assets/fonts/VT323.woff2` | HUD、终端、数字、按钮英文 |
| Noto Sans SC / 微软雅黑 | 系统字体 | 中文正文与表单 |

Logo 与机器人均为公司品牌资产，MIT 许可证不授予商标使用权。

## 2. 色彩

| Token | 值 | 用途 |
| --- | --- | --- |
| `--bg` | `#050914` | 页面底色 |
| `--bg-2` | `#081226` | 次级背景 |
| `--bg-3` | `#0b1b3a` | 面板/边框 |
| `--xl-cyan` | `#5fd3f3` | 主强调、焦点、在线 |
| `--xl-blue` | `#3a6ed8` | 主按钮、品牌蓝 |
| `--xl-glow` | `#4ea8ff` | 光晕、链接 |
| `--xl-violet` | `#7c5cff` | 次级装饰、网关状态 |
| `--xl-lime` | `#8bffb0` | 成功 / 在线 |
| `--xl-amber` | `#ffcc66` | 警告 / 待检测 |
| `--xl-red` | `#ff5f7e` | 离线 / 危险 |
| `--text` | `#d7e7ff` | 主文字 |
| `--text-dim` | `#8fb3e8` | 次级文字 |
| `--text-muted` | `#5f7fb3` | 弱提示 |

使用原则：

- 大面积保持深色，强调色只用于状态、焦点和关键动作。
- 红色只用于破坏性操作和离线状态；不要用来做普通装饰。
- 绿色用于在线/成功，避免与品牌青混淆。

## 3. 字体

```css
--pixel: 'Press Start 2P', monospace;  /* 英文标题 */
--mono: 'VT323', monospace;            /* HUD / 数字 / 英文按钮 */
--body: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
```

- 中文不使用像素字体，避免可读性下降。
- 数字与 HUD 使用 VT323，形成控制台气质。
- 正文行高 1.6–1.8，长文本最大宽度约 720px。

## 4. 布局

- 控制台：左侧固定导航（264px，可折叠到 84px）+ 顶部 HUD + 内容区。
- 内容最大宽度 1440px，页面左右留白 24–28px。
- 卡片网格：`repeat(auto-fill, minmax(300px, 1fr))`。
- 登录页：左侧品牌叙事 + 右侧终端卡片；移动端单列。
- 所有页面顶部使用「控制台 / 页面」的面包屑，页面内使用更具语义的标题（例如「服务注册表」「网关配置」「操作员档案」）。

## 5. 组件

### PixelPanel

- 深色渐变背景 + 1px 青色边框 + 硬阴影。
- 左上/右下角有像素角标。
- `hoverable` 时上浮 3px，边框和光晕增强。

### PixelButton

- 2px 边框 + 5px 硬阴影，hover 上浮、active 下压。
- `primary` 使用蓝青渐变，`ghost` 降低存在感，`danger` 仅用于删除。
- 英文使用 VT323，中文回退到系统字体。

### StatusLight

- 在线：青绿 LED + 光晕。
- 离线：红色 LED。
- 待检测：琥珀色。
- 标签使用 VT323 大写，保持 HUD 感。

### ServiceCard

- 顶部 2px 品牌色线。
- 图标、名称、标识、状态、描述、目标、入口、模式、延迟、操作。
- 入口地址带复制按钮；操作区包含「打开」「嵌入」「检测」「编辑」「删除」。
- 鼠标悬停时轻微上浮，卡片内部有扫描线扫过。

### Terminal

- 三色点 + 标题栏 + 等宽正文。
- 用于登录页启动日志、仪表盘系统状态。
- 光标使用 1.1s steps 动画。

## 6. 动效

- 登录页：GSAP 入场（Logo、标题、终端、机器人、卡片依次出现）、机器人浮动、全息环旋转、鼠标视差、扫描线。
- 页面切换：淡入 + 8px 位移，220ms。
- 按钮：160ms 位移与阴影变化。
- 卡片：200ms 上浮与边框发光。
- 数字：0.8s 计数动画。
- 扫描线：全局固定层 + 局部卡片扫光。
- 所有动效在 `prefers-reduced-motion: reduce` 下禁用；登录页也支持 `?nofx=1` 调试参数。

## 7. 登录页

登录页是产品的第一印象，结构如下：

1. 全屏网格 + 星点/连线粒子 + 顶部/底部光晕；
2. 顶部品牌条：XILI-AI 字标 + 安全链路状态 + 版本；
3. 左侧：像素徽章、`XILISERVERSWITCHMANAGESYSTEM` 故障风格标题、品牌副标题、启动终端、像素机器人全息环；
4. 右侧：终端风格登录卡片（操作员 ID、访问密钥、错误提示、进入按钮、网关在线状态）；
5. 成功登录：品牌区上移淡出、卡片缩小淡出、网格放大 + 闪光过渡。

移动端隐藏终端和机器人，保留品牌标题与登录卡片。

## 8. 可访问性

- 所有输入都有 `<label>`，表单可通过 Enter 提交。
- 焦点环使用 2px 青色 outline + 3px offset。
- 错误使用 `role="alert"`。
- 状态不仅依赖颜色，同时有文字（在线/离线/检测中）。
- 降低动效偏好下禁用所有扫描、浮动、故障动画。
- 正文对比度保持在高位；弱提示文字不用于关键信息。

## 9. 实现位置

| 内容 | 文件 |
| --- | --- |
| Token / 字体 | `src/frontend/src/styles/tokens.css` |
| 基础样式 | `src/frontend/src/styles/global.css` |
| 像素组件 | `src/frontend/src/styles/pixel.css` |
| 动效 | `src/frontend/src/styles/animations.css` |
| Naive UI 主题 | `src/frontend/src/App.vue` |
| 登录页 | `src/frontend/src/views/auth/LoginView.vue` |
| 背景粒子 | `src/frontend/src/components/cyber/CyberBackground.vue` |
| 网关核心图 | `src/frontend/src/components/common/GatewayOrb.vue` |
