# my-claude

Claude Code 自定义命令项目。

## 目录结构

- `commands/` — 命令定义（`.md`），通过 `install.py` 软链接到 `~/.claude/commands/`
- `skills/` — 技能定义（`.md`），通过 `install.py` 软链接到 `~/.claude/skills/`。技能可被 Claude 自主调用，适合"遇合适场景自动生效"的工具（如 my-mermaid）；命令需用户显式触发。
- `settings/` — settings.json 片段（`.json`），通过 `install.py` deep-merge 到 `~/.claude/settings.json`
- `hooks/` — hook 配置（`.json`）和脚本（`.py` 等），JSON 合并到 settings.json，脚本软链接到 `~/.claude/hooks/`

## 同步策略

修改上述任一目录下的文件（新增、删除、重命名、功能变更）后，必须同步更新 `README.md` 中的相关表格和说明，确保文档与实际功能一致。同步维护工作应在提交前完成，所有关联变更合并为一次提交，不拆分为多次。

## `my-new-command` 项目级策略

在本项目中执行 `my-new-command` 时，新命令文件写入 `commands/` 目录（而非默认的 `~/.claude/commands/`）。写入完成后，参考既有命令的风格优化内容、添加 frontmatter，然后执行 `./install.py` 完成安装。

## 技能 vs 命令策略

- 命令（`commands/`）：需用户显式触发（`/命令名`），适合有副作用的操作（提交、打 tag、安装插件、创建文件等）。
- 技能（`skills/`）：Claude 可在合适场景自主调用，适合纯生成/分析类工具（如 mermaid 图、代码分析等）。
- 新建时优先评估：能否被自主调用？如果可以，放 `skills/`；如果必须用户决策，放 `commands/`。
