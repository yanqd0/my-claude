# Agent 目录结构规范

Agent 以 `agents/<name>.md` 单文件定义，通过 `install.py` 软链接到 `~/.claude/agents/`（全局）。
项目级 agent 直接放各项目的 `.claude/agents/`，与全局同名时离工作目录近者胜出（nearest wins），
主对话委派时无感切换。

## 格式规范

### Frontmatter

```yaml
---
name: code-reviewer
description: >-
  一段式：功能概括 + 正向触发条款 + 负向排除条款 + 触发节奏。
tools: Skill, Read, Grep, Glob, Bash
skills:
  - code-review        # 可选：预加载技能内容到 agent 上下文
background: true       # 审查/测试类默认后台运行，不阻塞主对话
color: blue
---
```

- `tools`：最小权限原则。审查/测试类一律只读集（`Read, Grep, Glob, Bash`），
  委托技能时加 `Skill`；仅 debugger 类才考虑给 `Edit`。
- `background: true`：凡"主对话继续干活、agent 异步报告"的角色都加。
- `color`：按角色区分（tester 绿、reviewer 蓝、auditor 红）。

### description 撰写规范

description 是主对话决定是否委派时能看到的**唯一信息**（同 skill），必须包含三要素：

1. **正向触发**：具体场景关键词 + `use proactively`（如"一次 git commit 完成后"）。
2. **负向排除**：写明不适用场景与职责互斥条款，防止抢活或多 agent 重复出动
   （如 tester 排除有构建系统的项目；code-reviewer 声明"不做安全审计——移交 security-auditor"）。
3. **触发节奏**：每 commit / 阶段性 / 仅显式触发。多个同类 agent 间节奏刻意错开，
   仅在明确设计的模式下并行（如大范围 review）。

### 正文结构

1. **执行流程**：编号步骤。第一步通常是确认范围/场景，含"不该我干时立即停止并说明"。
2. **报告格式**：首行一句话结论；每个发现 `文件:行号` + 一句描述 + 修复方向；
   末尾固定「主对话后续动作」一节（审后协议）——修复、决策一律交主对话，agent 不代做。
3. **约束**：负面清单（只读不改、不安装依赖、副作用脚本不直接运行等）。

## 薄壳委托原则

内置技能（code-review、security-review 等）已覆盖的逻辑**不自研**，agent 只保留
触发条件 + 后台执行 + 审后协议三层。委托用双保险并禁止旁路：

1. frontmatter `skills:` 预加载技能内容；
2. 正文显式写"使用 `Skill` 工具调用 `<name>`"作回退，并声明**不得**跳过技能凭经验自行执行
   （调用方保留自做能力会绕过被调技能）。

## 触发接线

依赖 description 的主动委派是概率性的。关键触发点应由调用方 skill 显式接线：
在其 SKILL.md 步骤中写"使用 `Agent` 工具后台派出 `<agent>`"，并在 frontmatter 的
`allowed-tools` 中声明 `Agent`（参考 my-git-commit 第 6 步派出 code-reviewer）。

## 用户交互

agent 后台运行，**不使用 AskUserQuestion**。需要用户决策的事项一律写入报告的
「主对话后续动作」，由主对话按其交互约定处理。

## 全局 vs 项目级判断

- **职能进全局，知识进项目**：语言无关的流程角色（审、测、调）放全局；
  依赖项目专有知识（构建矩阵、测试入口、领域约定）的放项目级。
- 猜错代价高的角色（如 tester 跑错测试命令有副作用），全局版 description 收窄到
  安全场景，复杂项目用**同名**项目级 agent 覆盖；猜错代价低的只读角色可保持通用兜底。

## 既有 agent 风格参考

| agent | 特点 |
|-------|------|
| `tester` | 收窄型：description 限定孤立脚本并显式排除构建系统项目；无测试时构造快速验证；副作用脚本只做静态检查 |
| `code-reviewer` | 薄壳 + 接线型：委托 code-review 技能；由 my-git-commit 提交后显式派出；审后协议支持 my-git-amend 回写 |
| `security-auditor` | 薄壳 + 低频型：委托 security-review 技能；阶段性触发不逐 commit；发现交主对话决策，不自动修复 |
