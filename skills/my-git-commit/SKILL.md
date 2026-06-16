---
name: my-git-commit
description: >-
  暂存并提交当前修改，生成规范的中文提交信息。当对话中完成阶段性工作、需要提交代码时，
  可自主调用；也作为其他 skill/command 的提交工具被调用。支持多 commit 拆分。
allowed-tools: Bash(git:*)
---

根据当前对话上下文中涉及的修改，执行 git commit。可接收一个可选参数 `<split_plan>`。

## 执行步骤

1. **判断是否需要提交**：`git status` 确认有变更（修改、新增、删除）。若工作区干净，汇报"nothing to commit"并结束。
2. **加载提交格式规范**：`Read` `references/commit-message.md`，获取 title/description 格式要求。
3. **判断提交前缀规范**：
   - 若调用方（其他 skill/command）已指定 type 或规范 → 直接沿用。
   - 否则 `Read` `references/commit-prefix.md`，按其"规范识别"流程确定是启用默认 Conventional Commits 还是沿用项目既有规范。
4. **判断是否需要拆分**：
   - 无 `<split_plan>` 且变更逻辑单一 → 跳过，合并为 1 次提交。
   - 有 `<split_plan>` 或变更明显涉及多个独立逻辑 → `Read` `references/commit-split.md`，按其策略执行多 commit 拆分。边界不明确时向用户确认。
5. **执行提交**：按步骤 3 确定的 type、步骤 2 的格式、步骤 4 的拆分方案，逐次 `git add` + `git commit`。
