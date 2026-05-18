---
allowed-tools: Bash(git:rev-parse,git:pull,git:merge,git:log)
description: 从远程仓库拉取最新代码。
---

## 执行步骤

1. `git rev-parse HEAD` 记录当前 HEAD。
2. 执行 `git pull`。
3. 若成功，结束。
4. 若失败（含合并冲突、三方合并等需手动解决的复杂情况）：
   - 不重试。
   - 用 `git log --oneline <原HEAD>..FETCH_HEAD` 展示将引入的提交，简要总结改动量。
   - 执行 `git merge --abort` 回退到 pull 前状态。
   - 分析失败原因，提示用户手动处理。
