# LibTV Claude Code Marketplace

将 [liblib-ai/marketplace](https://github.com/liblib-ai/marketplace) 的 Codex 插件适配为 Claude Code 插件市场。此仓库是社区适配版，不是 LiblibAI 官方 Claude 插件发行渠道。

提供一个插件 `libtv`，保留上游三个 Skill、参考资料、曲谱和辅助脚本，通过 `https://mcp.liblib.tv/mcp` 连接 LibTV。

## 安装

需要支持插件的新版 Claude Code、Git，以及可用的 LibTV 账号。

### 从本地安装（无需先发布仓库）

在此仓库目录中执行：

```bash
claude plugin marketplace add .
claude plugin install libtv@libtv-claude
```

### 从 GitHub 安装

适配代码推送至此仓库的 GitHub 远程后，执行：

```bash
claude plugin marketplace add zhuangjinjin/claude-marketplace
claude plugin install libtv@libtv-claude
```

重启 Claude Code，运行 `/mcp`，选择本插件的 LibTV 服务，按提示完成 OAuth 登录。每位用户使用自己的 LibTV 账号授权；仓库不包含 client ID、token 或其他凭据。实际 OAuth 兼容性以登录结果为准。

## 使用

| 命令 | 用途 |
| --- | --- |
| `/libtv:libtv-to-treatment` | 将画布素材整理成中文 16:9 可翻页导演提案 |
| `/libtv:libtv-blender-live-action` | LibTV 出图 → Blender 白模运镜 → Seedance 实拍化 |
| `/libtv:music-driven-product-ad` | 音乐驱动的一镜到底产品广告 |

也可以直接描述需求，如“查看我在 LibTV 中的项目”。三个工作流均需要 LibTV MCP 授权；Blender、浏览器控制、钢琴演奏等能力是独立依赖，不随本插件安装。缺少这些工具时，应先配置，而不是假设它们存在。

音乐工作流自带 Python 3 脚本和 Swift 源码。录屏相关脚本需要 macOS 15+、Swift 工具链及用户授予的屏幕录制/辅助功能权限。使用本机脚本前请阅读源码，不应在安装时自动执行。生成媒体可能消耗 LibTV 额度，执行前确认操作和费用。

上游的 `tool_timeout_sec` 是 Codex 配置，本适配版不将它传给 Claude。长任务优先使用服务提供的异步任务查询；确需延长 MCP 工具超时，可在启动时设置：

```bash
MCP_TOOL_TIMEOUT=1200000 claude
```

此环境变量使用毫秒，影响该 Claude 进程的 MCP 工具调用，不是单独针对 LibTV。

## 更新与验证

```bash
claude plugin marketplace update libtv-claude
claude plugin update libtv@libtv-claude
```

更新后重启 Claude Code。本地开发可用 `claude --plugin-dir ./plugins/libtv` 临时加载（不要同时启用同名已安装插件）。

```bash
claude plugin validate . --strict
claude plugin validate ./plugins/libtv --strict
python3 -I -m unittest discover -s tests -v
```

清单和静态测试不会登录 LibTV，也不会生成付费媒体；它们不能替代 OAuth、MCP 工具调用和创作链路的端到端验证。

## 来源与许可

上游快照：`4ac581c3cbdaa53d0d42df85c6bf62e45600bc5f`。适配细节见 [插件设计文档](plugins/libtv/DESIGN.md)。

上游未附仓库整体 LICENSE，本适配不擅自为其代码或文档增加许可证；进一步分发或商业使用前，请向上游确认授权范围。

曲谱资产中，除 `mendelssohn-wedding-march` 外，Mutopia 版本均为公有领域；该曲源版及衍生曲谱为 **CC BY-SA 4.0**（排版 © 2017 Alexander Brock，基于 Durand & Cie. 出版的 Dubois 改编版，plate D. & F. 9516）。保留其署名及许可声明，详见 [曲谱说明](plugins/libtv/skills/music-driven-product-ad/references/repertoire.md) 与 [曲谱目录](plugins/libtv/skills/music-driven-product-ad/assets/scores/catalog.json)。
