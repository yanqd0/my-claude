---
allowed-tools: Bash(git:*)
description: 将当前修改合并到上一次提交，并同步更新提交信息。
---

与 `my-git-commit` 流程相同，差异仅在第 4 步：执行 `git commit --amend` 将修改合并到上一次提交，而非新建提交。

## 执行步骤（的差异）

4. 执行 `git commit --amend`，提交信息按下方规范更新。

## 提交信息格式（的差异）

与 `my-git-commit` 规则一致。在此基础上，对比上一个提交的内容变化，针对代码修改部分同步更新 title 和 description。
