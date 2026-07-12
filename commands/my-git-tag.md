---
allowed-tools: Bash(git:tag,git:log,git:describe) Read Edit Write Grep Skill
description: 打语义化版本 tag，自动生成改动摘要并同步 CHANGELOG。
---

根据用户指定的参数，打 `git tag`。支持一个可选参数：`<tag_name>`。

## 执行步骤

1. 解析参数：
   - 若提供 `<tag_name>`，作为 tag 名称；若为空，按以下优先级推算下一个版本号：
     1. 执行 `git describe --tags --abbrev=0` 获取最近一个 tag。
     2. 若存在 `CHANGELOG.md`，用 `Grep`（pattern `^## `）快速获取近期版本列表。
     3. 综合两者，按[语义化版本号](https://semver.org/lang/zh-CN/)规则推算。自动生成的版本号格式与上一个 tag 保持一致（上一个带 `v` 则带 `v`，不带则不带）。手动输入的版本号可带 `v` 可不带。
2. 校验 tag 名称是否符合 `MAJOR.MINOR.PATCH` 格式（可带 `v` 前缀）。若不符合，尝试修正并告知用户修正内容。
3. 交互确认：若步骤 1、2 中**对用户非空的输入做了调整**（如修正了版本号格式），必须在继续前提示用户确认调整内容，得到确认后方可继续。
4. 同步 CHANGELOG：使用 `Skill` 工具调用 `my-changelog`，传入版本号 `<tag_name>` 与区间 `<上一个tag>..HEAD`。my-changelog 会归类改动（Features / Bug Fixes / Others）、写入 `CHANGELOG.md` 并提交。其归类结果保留在上下文中，供下一步生成 tag message，无需重新分析 commit。
5. 生成 tag message：基于步骤 4 的归类结果整形为 tag message 格式（与 CHANGELOG 条目同源，仅改呈现）：
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
6. 执行 `git tag -a <tag_name> -m "<message>"`。tag 打在步骤 4 my-changelog 产生的 CHANGELOG 提交上（若无新提交则打在 HEAD）。
7. 将 tag 的版本号和内容摘要保存到项目记忆，便于后续查询。
