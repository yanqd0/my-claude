# Skill 目录结构规范

Skill 以 `skills/<name>/` 目录组织，必须包含 `SKILL.md`（入口），可选包含 `references/`（按需加载的细节文件）。

## SKILL.md 内容原则

- 包含 frontmatter（`name`、`description`、`allowed-tools`），`description` 需写明触发场景引导自主调用。
- 内容为执行流程 + 分支判断，轻量为主。步骤级的细节下沉到 `references/`。
- 涉及多个分支逻辑时，明确"命中即停"的优先级链。

## references/ 拆分决策

仅在内容满足任一条件时才拆分到 `references/`：

1. **条件触发**：仅在特定分支或特定条件下才需要读取（如 my-mermaid 的 10 个图类型文件，每次只读 1 个；commit-split.md 仅在有 split_plan 时读）。
2. **冷启动**：仅在首次使用、项目无历史状态时才需要（如 commit-prefix.md，仅在仓库无任何提交规范时读一次，之后由记忆 + git log 命中）。
3. **大体积**：内容超过 ~40 行且不总是需要。

不满足以上条件的细节直接 inline 在 SKILL.md 中。

## 示例

- `my-mermaid/`：SKILL.md 含类型选择触发表 + 通用格式规范；references/ 下 10 个文件，每种图类型独立。
- `my-git-commit/`：SKILL.md 含完整识别流程链 + 条件分支；commit-message.md（每次必读，15 行）、commit-prefix.md（仅冷启动）、commit-split.md（仅拆分时），各自满足拆分条件。
