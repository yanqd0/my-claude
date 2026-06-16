# Command 目录结构规范

Command 以 `commands/<name>.md` 单文件定义，通过 `install.py` 软链接到 `~/.claude/commands/`。

## 格式规范

### Frontmatter

```yaml
---
allowed-tools: Bash(git:*) Read Write
description: 简短中文用途说明，一行。
---
```

- `allowed-tools`：最小权限原则，只声明 command 实际需要的工具。
- `description`：一行中文，用于 ` /commands` 列表展示。

### 正文结构

1. **首段**：一句话概述，可带可选参数 `<param_name>`。
2. **执行步骤**：编号列表，每步一个主题。涉及分支用缩进子项。
3. **约束/附录**（可选）：输出格式、文件路径约定等。

### 参数约定

- `<param_name>`：必选或可选参数，在首段和步骤中引用。
- 参数缺失时的回退行为需明确（如"回顾上下文推断"、"交互请用户确认"）。

### 分支逻辑

简单的 if-else 用缩进子项。复杂多分支（如 my-git-tag 的版本号推算）用编号子步骤 + 命中即停链。

## Skill vs Command 拦截判断

新建前，先过以下检查。任一条命中，**推荐使用 skill 而非 command**：

1. **自主调用**：该功能在合适场景下 Claude 可自行决定使用，不需等待用户输入 `/命令`。
2. **分支过多**：执行流程中有 ≥3 条独立分支，每条分支的逻辑差异大，适合拆为 skill + references/ 按需加载。
3. **被其他工具调用**：该功能主要作为其他 command/skill 的中间步骤，而非用户直接入口（如 my-git-commit）。
4. **纯生成/分析**：不修改文件、不执行副作用，仅产出内容（图、文、分析结果等）。

## 既有 command 风格参考

| command | 特点 |
|---------|------|
| `my-git-amend` | 最简风格：14 行，单流程无分支 |
| `my-git-tag` | 多步骤 + 分支：73 行，含参数校验、交互确认、格式模板 |
| `my-code-io` | 分析+生成类：64 行，含多维度分析框架和输出格式规范 |
| `my-plugin-init` | 检测+安装类：73 行，含清单表格、增量检测、逐项执行 |
| `my-new-command` | 元创建类：23 行，根据描述生成新 command |
| `my-new-hook` | 元创建类：65 行，含 hook 类型说明和模板 |
