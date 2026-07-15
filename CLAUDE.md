# my-claude

Claude Code 自定义 command 与 skill 项目。

## 目录结构

- `commands/` — command 定义（`.md`），软链接到 `~/.claude/commands/`
- `skills/` — skill 定义（目录，含 `SKILL.md` + `references/`），软链接到 `~/.claude/skills/`
- `agents/` — 全局 subagent 定义（`.md`），软链接到 `~/.claude/agents/`
- `settings/` — settings.json 片段（`.json`），deep-merge 到 `~/.claude/settings.json`
- `hooks/` — hook 配置（`.json`）和脚本（`.py` 等），JSON 合并到 settings.json，脚本软链接到 `~/.claude/hooks/`
- `.claude/rules/` — 项目级规则，SessionStart 自动加载。含 `skill-structure.md`、`command-structure.md`

## 同步策略

修改上述任一目录下的文件（新增、删除、重命名、功能变更）后，必须同步更新 `README.md` 中的相关表格和说明。同步维护工作应在提交前完成，所有变更合并为一次提交。

## `my-new-command` 项目级策略

在本项目中执行 `my-new-command` 时，新 command 写入 `commands/` 目录（非默认 `~/.claude/commands/`）。完成后参考既有 command 风格优化内容、添加 frontmatter，执行 `./install.py` 安装。
