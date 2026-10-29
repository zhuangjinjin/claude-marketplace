# LibTV Claude Code 适配设计

## 目标与方案选择

将上游 Codex 分发包转换为 Claude Code 原生插件市场，保留三个创作工作流及全部媒体资产。不实现新的 MCP server，不代理 OAuth，也不改变 LibTV 服务端行为。

## 核心组件与关键决策

- 市场入口改为根目录 `.claude-plugin/marketplace.json`，使用 Claude 的 `owner` 与相对路径字符串 `source`。
- 插件入口改为 `.claude-plugin/plugin.json`。移除 Codex `interface`、安装策略和认证策略；Claude 默认发现插件根目录的 `skills/` 与 `.mcp.json`。
- HTTP MCP 地址保持 `https://mcp.liblib.tv/mcp`。删除 Codex 专属 `tool_timeout_sec`，由 Claude 进程的 MCP 超时设置管理。
- 不分发 Codex `agents/openai.yaml`，工作流入口使用 Claude 的 namespaced slash commands；工具名称以当前会话实际发现结果为准。
- 工作流中的本地资源基于 Skill 所在目录解析，不写死 Codex 或 Claude 的缓存版本目录。
- 上游辅助脚本和曲谱保持原样，以减少迁移造成的功能变化。

## 安全考量

远程 MCP 是外部服务信任边界。登录由 Claude Code 与服务端 OAuth 完成，不在仓库中保存令牌；上传素材会发送到 LibTV，生成操作可能收费，须获得用户确认。

Swift 脚本涉及录屏及输入控制，须用户授权系统权限。插件不安装 hooks、不自动运行这些脚本。下载的资源和 MCP 返回文本按不可信内容处理，不视为额外执行指令。

## 已知限制与验证

静态验证覆盖市场、插件、MCP 配置、Skill 入口及资产保留。实际 OAuth 登录、付费媒体生成、Blender、浏览器与 macOS 录屏依赖真实账号、工具和用户授权，不能以清单验证代替端到端测试。

上游未提供仓库整体 LICENSE；只保留其已有的曲谱署名和许可，不推断整体开源许可。维护时需同步上游变化并复查平台专用路径和工具名称。

## 变更历史

### 2026-10-29 — Claude Code 初始适配

基于上游 `4ac581c3cbdaa53d0d42df85c6bf62e45600bc5f`，转换清单、移除 Codex 专用元数据、更新工作流兼容说明并补充安装文档与静态回归测试。

## 静态扫描复核

安全扫描器将 `trim_wav_silence.py:48` 的 `wave.open(str(args.source), "rb")` 标为路径遍历。该工具是用户显式传入任意本地路径的离线 CLI，不存在服务端目录沙箱或不可信网络参数，读取该路径正是其功能；输出已拒绝源目标相同和已有目标，并以 `xb` 创建文件。因此该项按误报处理，不为消除告警而破坏 CLI 的文件访问功能。上游 Python 脚本的函数长度和复杂度警告保留，本次不扩大为算法重构。
