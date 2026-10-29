# 来源与适配范围

- 来源：https://github.com/PomeloR611/libtv-video-agent
- 固定提交：`29c3122a2535bf37f332d189a5c28668f2a627d2`
- 上游许可证：MIT，Copyright (c) 2026 LibTV Video Agent contributors。完整原文见 [LICENSE](LICENSE)。
- 适配日期：2026-10-29。

保留并重述：前期定调、定版资产、可选九宫格、clean 后核验、逐镜 QC、批次预览、提示词职责分离及 ffmpeg 终剪方法。

重写：原 SKILL.md 与 AGENTS.md 的操作入口合并为 MCP Skill；cli-reference 改为 mcp-reference；旧能力快照改为能力边界说明。移除 CLI 登录/安装、cwd 绑定、固定模型/槽位/价格和付费审核探针。所有收费媒体统一遵守明确授权，未知任务按原幂等身份恢复。旧剪辑模板不直接复制，提供音轨缺失分支及合成素材可验证的新示例。

上游 AGENTS.md 的有效制作方法已并入本技能和专题参考，不额外安装全局规则文件；原仓库的研发计划不是运行时依赖，不分发。新的文档按本目录 MIT 许可提供；不改变父插件其他工作流、曲谱或素材的许可。
