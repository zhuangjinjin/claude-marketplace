# LibTV Claude Code 插件

将 LibTV 的远程画布及媒体能力和四个创作 Skill 接入 Claude Code。社区适配自 LiblibAI 的 Codex 插件，安装、授权及更新步骤见[仓库 README](../../README.md)。

## 结构与职责

- `.claude-plugin/plugin.json`：Claude 插件身份与版本。
- `.mcp.json`：LibTV HTTP MCP 服务，凭据由 Claude Code 管理。
- `skills/`：导演提案、Blender 联动、音乐广告及 MCP 短片制作工作流，以及参考文档和本地辅助脚本。
- `assets/`：保留的上游图标，不依赖 Codex 的界面字段。

## 快速使用

安装并通过 `/mcp` 授权后，运行 `/libtv:libtv-to-treatment` 或描述 LibTV 创作需求。

## 依赖与边界

依赖 Claude Code 和 LibTV 账号。Blender、浏览器自动化和钢琴工具需单独配置；Python 脚本需要 Python 3，Swift 录屏脚本需要 macOS 15+ 及系统权限。此插件不提供本地 MCP server，不在安装时运行脚本，不预置登录凭据。

设计、迁移说明及安全边界见 [DESIGN.md](DESIGN.md)，静态回归测试位于仓库根目录 `tests/`。

## MCP 短片制作（1.1.0 新增）

`/libtv:libtv-video-production` 使用现有 MCP 连接，从资产与分镜推进逐镜生成、核验及本地终剪，不依赖 LibTV CLI。仅本地终剪需要 `ffmpeg` / `ffprobe`。详见 [使用说明](skills/libtv-video-production/README.md) 和 [独立 MIT 许可](skills/libtv-video-production/LICENSE)。
