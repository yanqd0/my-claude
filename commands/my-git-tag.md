---
allowed-tools: Bash(git:tag,git:log,git:describe,git:rev-parse)
description: 打语义化版本 tag，自动生成改动摘要并记忆。
---

根据用户指定的参数，打 `git tag`。支持两个可选参数：`<tag_name> [<target_ref>]`。

## 执行步骤

1. 解析参数：
   - 若提供 `<target_ref>` 且为合法 git ref，在此处打 tag；否则在 `HEAD` 打 tag。
   - 若提供 `<tag_name>`，作为 tag 名称；若为空，执行 `git describe --tags --abbrev=0` 获取最近一个 tag，按[语义化版本号](https://semver.org/lang/zh-CN/)规则推算下一个版本号。自动生成的版本号格式与上一个 tag 保持一致（上一个带 `v` 则带 `v`，不带则不带）。手动输入的版本号可带 `v` 可不带。
2. 校验 tag 名称是否符合 `MAJOR.MINOR.PATCH` 格式（可带 `v` 前缀）。若不符合，尝试修正并告知用户修正内容。
3. 交互确认：若步骤 1、2 中**对用户非空的输入做了调整**（如修正了版本号格式、回退了非法 ref），必须在打 tag 前提示用户确认调整内容，得到确认后方可继续。
4. 生成 tag message：
   - 通过 `git log --oneline <上一个tag>..<target_ref>` 获取区间内所有 commit message。
   - 不查看代码，仅根据 message 将改动归类为 **Features**、**Bug Fixes**、**Others** 三类。
   - 按以下 Markdown 格式：

```
## Features

- 新增功能 1
- 新增功能 2

## Bug Fixes

- 修复 1

## Others

- 其它改动 1
```

   - `## Features` 仅包含新增功能；`## Bug Fixes` 仅包含 bug 修复；无法归入前两类的（重构、文档、CI、样式调整等）写入 `## Others`。
   - 过滤抵消项：同一版本内新增后又删除的功能相互抵消，不写入 message；同一版本内引入又在同一版本内修复的 bug 相互抵消，不写入。
5. 执行 `git tag -a <tag_name> <target_ref> -m "<message>"`。
6. 将 tag 的版本号和内容摘要保存到项目记忆，便于后续查询。
