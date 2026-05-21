# my-claude

Git 操作相关的 Claude Code 自定义命令项目。

## 命令文件

所有命令定义在 `commands/*.md`，通过 `install.py` 软链接到 `~/.claude/commands/`。

## 同步策略

修改 `commands/` 下的命令文件（新增、删除、重命名、功能变更）后，必须同步更新 `README.md` 中的命令表格和相关说明，确保文档与实际功能一致。

## `my-new-command` 项目级策略

在本项目中执行 `my-new-command` 时，新命令文件写入 `commands/` 目录（而非默认的 `~/.claude/commands/`）。写入完成后，参考既有命令的风格优化内容、添加 frontmatter，然后执行 `./install.py` 完成安装。新增文件后，以及后续对命令文件的修改调整中，同步按需更新 `README.md` 中的命令表格和相关说明。
