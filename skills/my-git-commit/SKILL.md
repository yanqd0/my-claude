---
name: my-git-commit
description: >-
  暂存并提交当前修改，生成规范的中文提交信息。当对话中完成阶段性工作、需要提交代码时，
  可自主调用；也作为其他 skill/command 的提交工具被调用。支持多 commit 拆分。
allowed-tools: Bash(git:*)
---

根据当前对话上下文中涉及的修改，执行 git commit。可接收一个可选参数 `<split_plan>`。

## 执行步骤

1. **确认变更范围**：`git status` 和 `git diff`（含 `--staged`）。
2. **识别提交规范**：`Read` `references/commit-convention.md`，按其"规范识别"流程确定 type 集合和格式。
3. **确定提交方案**：
   - 无 `<split_plan>`：所有修改合为 1 次提交。
   - 有 `<split_plan>`：解析拆分计划，边界不明确时向用户确认。
4. **多 commit 拆分**（仅当有 `<split_plan>`）：按顺序逐次 `git add` 相关文件 → `git commit`。
5. **撰写提交信息**：type 选择、标题格式、description 规范均见 `references/commit-convention.md`。
