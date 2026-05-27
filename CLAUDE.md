# my-claude

Claude Code 自定义命令项目。

## 目录结构

- `commands/` — 命令定义（`.md`），通过 `install.py` 软链接到 `~/.claude/commands/`
- `settings/` — settings.json 片段（`.json`），通过 `install.py` deep-merge 到 `~/.claude/settings.json`
- `hooks/` — hook 配置（`.json`）和脚本（`.py` 等），JSON 合并到 settings.json，脚本软链接到 `~/.claude/hooks/`

## 同步策略

修改上述任一目录下的文件（新增、删除、重命名、功能变更）后，必须同步更新 `README.md` 中的相关表格和说明，确保文档与实际功能一致。同步维护工作应在提交前完成，所有关联变更合并为一次提交，不拆分为多次。

## `my-new-command` 项目级策略

在本项目中执行 `my-new-command` 时，新命令文件写入 `commands/` 目录（而非默认的 `~/.claude/commands/`）。写入完成后，参考既有命令的风格优化内容、添加 frontmatter，然后执行 `./install.py` 完成安装。
