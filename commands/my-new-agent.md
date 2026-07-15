---
allowed-tools: Read Glob Write AskUserQuestion
description: 在当前项目创建项目级 agent 定义文件。
---

根据功能描述在当前项目创建一个项目级 agent。支持两个参数：`<description> [<name>]`。

## 执行步骤

1. 解析参数：
   - `<description>`：agent 的职责描述，必选。
   - `<name>`：agent 名称（小写字母+连字符），可选。
2. 学习现有模式：
   - `Glob` 列出 `~/.claude/agents/*.md`（全局）与 `./.claude/agents/*.md`（本项目）已有 agent。
   - 读取 1-2 个代表性文件作为风格参考；若 `<name>` 与全局 agent 同名，视为**覆盖场景**
     （nearest wins），读取被覆盖者以对齐职责边界、写明差异。
3. name 处理与前置确认（一次性，后续步骤不再确认）：
   - `<name>` 缺省 → 从 `<description>` 推断英文名；已提供 → 校验其与描述主题的一致性，
     偏差过大时准备改名建议。
   - 检查目标路径 `./.claude/agents/<name>.md` 是否已存在：存在则将"覆盖或改名"列为待确认问题。
   - 结合步骤 2 的总结审视 `<description>`：触发场景是否明确、职责边界（负向排除）是否清晰、
     是否需要写权限、与既有 agent 有无重叠——对不明确、有问题处各准备一个确认问题（0~N 个）。
   - 用 `AskUserQuestion` 一次性确认：完整写入路径（含最终 name），以及上述待确认问题。
4. 生成内容（frontmatter + 正文）：
   - description 三要素：正向触发（场景关键词 + use proactively）、负向排除（不适用场景
     与职责互斥条款）、触发节奏。
   - `tools` 最小权限：审查/测试类只读集（Read, Grep, Glob, Bash），委托技能加 Skill，
     仅调试/修复类考虑 Edit。
   - 后台异步报告的角色加 `background: true`；可选 `color`。
   - 正文三段：执行流程（首步确认范围，不该接手时立即停止）、报告格式（首行结论 +
     `文件:行号` + 末尾「主对话后续动作」）、约束负面清单。
   - 项目专有知识（构建/测试命令、目录约定）直接写进正文，不留间接引用。
5. 写入与收尾：写入步骤 3 已确认的路径；若 `.claude/agents/` 目录为本次新建，
   提醒需重启 Claude Code 会话才会加载；建议将该文件纳入版本控制。
