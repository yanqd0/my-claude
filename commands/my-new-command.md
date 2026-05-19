---
allowed-tools: Read Write Bash(ls,python3:*)
description: 根据描述创建新的 Claude Code 命令文件。
---

根据用户提供的名称和功能描述，创建一个新的命令文件。支持两个参数：`<name> <description>`。

## 执行步骤

1. 解析参数：
   - `<name>`：命令文件名，可带 `.md` 后缀也可不带。若不带则自动补 `.md`。
   - `<description>`：命令的功能描述，一句话说明用途。
2. 学习现有模式：
   - 列出目标目录下已有的 `.md` 文件。
   - 选取 1-2 个代表性文件，读取其 frontmatter 和结构作为模板参考。
3. 生成内容：
   - 参考既有命令的结构（YAML frontmatter + 概述 + `## 执行步骤` + 分步说明 + 格式规范），结合功能描述生成新文件。
   - frontmatter 中 `allowed-tools` 按最小权限原则填写，`description` 一句中文概述。
4. 交互确认：将生成的完整内容展示给用户，得到确认后再写入。用户可能要求修改，按反馈迭代。
5. 写入文件：
   - 默认写入 `~/.claude/commands/<name>.md`，已存在则提示冲突，由用户决定覆盖或改名。
   - 若存在 `CLAUDE.md` 且其中指示了项目级写入策略，则按其指示操作。
6. 若写入的是项目目录（非 `~/.claude/commands/`），则按项目说明执行安装步骤。
