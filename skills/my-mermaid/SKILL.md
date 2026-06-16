---
name: my-mermaid
description: >-
  生成色彩合理、分组清晰的 mermaid 图。当对话中出现系统架构、流程图、时序交互、
  状态机、数据模型、时间线、占比分布等适合可视化的内容时，可自主调用此技能生成图表。
allowed-tools: Read Write
---

根据用户描述或上下文，生成一张或多张 mermaid 图。

## 执行步骤

1. **确定内容**：回顾对话中适合可视化的内容，整理简要说明，逐一提示用户确认。用户明确描述时跳过确认。
2. **选择图类型**：根据下表确定类型，然后 **Read 对应的 `references/<file>.md`** 获取完整的语法、配色和大小限制。

   | 核心叙事 | 图类型 | 参考文件 | 触发场景（代码阅读 / 技术介绍） |
   |---------|--------|---------|------|
   | 结构关系 | `flowchart` | `flowchart.md` | 模块依赖、调用链、条件分支 / 系统架构、部署拓扑、算法流程 |
   | 块结构 | `block` | `flowchart.md` | 系统方块图、组件层次 / 部署架构块图、模块划分 |
   | 交互顺序 | `sequenceDiagram` | `sequence-diagram.md` | API 调用、消息传递、中间件链路 / 认证流程、协议握手 |
   | 状态转移 | `stateDiagram-v2` | `state-diagram.md` | 订单/任务/连接生命周期 / TCP 状态机、Promise 状态、CI 流水线 |
   | 类型层级 | `classDiagram` | `class-diagram.md` | 类继承/组合、接口实现 / 设计模式、框架核心类型 |
   | 数据实体 | `erDiagram` | `er-diagram.md` | Schema 定义、ORM 外键 / 数据库设计、API 嵌套结构 |
   | 进度/计划 | `gantt` | `gantt-timeline-journey.md` | 不适用（面向计划） / 功能排期、版本路线图 |
   | 时间线 | `timeline` | `gantt-timeline-journey.md` | git log 可视化 / 技术演进史、版本变更年表 |
   | 用户旅程 | `journey` | `gantt-timeline-journey.md` | 用户操作追踪 / 引导流程、功能体验路径 |
   | 占比分布 | `pie` | `pie.md` | 文件类型占比、测试覆盖率 / 流量分布、资源分配 |
   | 量化对比 | `xychart` | `xychart.md` | benchmark 对比 / 框架性能横向对比、QPS 柱状图 |
   | 集合关系 | `venn-beta` | `venn-ishikawa.md` | 功能重叠、模块交集 / 技术方案差异与覆盖 |
   | 分支拓扑 | `gitGraph` | `git-graph.md` | 分支合并历史 / 分支策略、发布流程 |
   | 因果分析 | `ishikawa-beta` | `venn-ishikawa.md` | Bug 根因追溯 / 问题分解、故障归类 |
   | 知识层次 | `mindmap` | `mindmap.md` | 项目目录结构 / 技术体系全景、功能拆解 |

   优先级：结构 > 交互 > 状态转移 > 时间/分布 > 量化对比。
   `flowchart` 不要用已废弃的 `graph`；`stateDiagram-v2` 不要用旧版 `stateDiagram`。

3. **读取上下文**：`Read` 目标文件以准确绘图。
4. **生成预览**：输出 mermaid 代码块，用户确认后再写入。
5. **写入文件**：默认仅展示。用户要求时按指定路径或对话相关 `.md` 写入。
6. **多图**：每张图前用 Markdown 加粗标注图名。

## 通用格式规范

以下规范适用于所有图类型（各类型的特有限制在 reference 文件中）：

- 节点 ID 用简洁英文或拼音，标签用中文。含空格时用双引号包裹，换行用 `<br/>`。
- 标题使用 YAML frontmatter（`---\ntitle: 中文标题\n---`），不支持的渲染器用 `%% 图标题：xxx`。
- 不生成 README 或说明文件，mermaid 代码块直接嵌入回复。
- 使用 `classDef` 和 `class` 进行语义着色（配色方案见各 reference 文件）。
