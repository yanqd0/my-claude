# my-claude

Git 操作相关的 Claude Code 自定义命令项目。

## 命令文件

所有命令定义在 `commands/*.md`，通过 `install.py` 软链接到 `~/.claude/commands/`。

## 同步策略

修改 `commands/` 下的命令文件（新增、删除、重命名、功能变更）后，必须同步更新 `README.md` 中的命令表格和相关说明，确保文档与实际功能一致。
