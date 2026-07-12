---
allowed-tools: Bash(git:tag,git:log,git:describe) Read Edit Write Grep Skill AskUserQuestion
description: 打语义化版本 tag，自动生成改动摘要并同步 CHANGELOG。
---

根据用户指定的参数，打 `git tag`。支持一个可选参数：`<tag_name>`。

## 执行步骤

1. 确定版本号：`Read` `~/.claude/skills/my-changelog/references/next-version.md`，按其流程解析或推算版本号——提供 `<tag_name>` 则采用并校验格式，为空则自动推算下一个版本号；对用户非空输入做了调整（如修正格式）时须先请用户确认。该 reference 与 my-changelog 共享同一份判断逻辑。
2. 同步 CHANGELOG：使用 `Skill` 工具调用 `my-changelog`，传入版本号 `<tag_name>` 与区间 `<上一个tag>..HEAD`。my-changelog 会归类改动（Features / Bug Fixes / Others）、整合简化后写入 `CHANGELOG.md` 并提交。其归类结果保留在上下文中，供下一步生成 tag message，无需重新分析 commit。
3. 生成 tag message：基于步骤 2 的归类结果整形为 tag message 格式（与 CHANGELOG 条目同源，仅改呈现）：
   - 自动生成一句概括性的大版本标题（中文，≤50 字符），概括本次版本的主要变化方向。
   - 分类标题用 `##`（不含版本号标题行），按「首行标题 → 空行 → Markdown 正文」格式：

```
<概括性标题，≤50字符>

## Features

- 改动描述 1。

## Bug Fixes

- 修复描述 1。

## Others

- 其它改动 1。
```

   - 无内容的分类直接省略，不输出空标题。
4. 执行 `git tag -a <tag_name> -m "<message>"`。tag 打在步骤 2 my-changelog 产生的 CHANGELOG 提交上（若无新提交则打在 HEAD）。
5. 将 tag 的版本号和内容摘要保存到项目记忆，便于后续查询。
