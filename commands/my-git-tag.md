---
allowed-tools: Bash(git:tag,git:log,git:describe) Read Edit Write
description: 打语义化版本 tag，自动生成改动摘要并同步 CHANGELOG。
---

根据用户指定的参数，打 `git tag`。支持一个可选参数：`<tag_name>`。

## 执行步骤

1. 解析参数：
   - 若提供 `<tag_name>`，作为 tag 名称；若为空，按以下优先级推算下一个版本号：
     1. 执行 `git describe --tags --abbrev=0` 获取最近一个 tag。
     2. 若存在 `CHANGELOG.md`，用 `grep -n '^## ' CHANGELOG.md | head -20` 快速获取近期版本列表。
     3. 综合两者，按[语义化版本号](https://semver.org/lang/zh-CN/)规则推算。自动生成的版本号格式与上一个 tag 保持一致（上一个带 `v` 则带 `v`，不带则不带）。手动输入的版本号可带 `v` 可不带。
2. 校验 tag 名称是否符合 `MAJOR.MINOR.PATCH` 格式（可带 `v` 前缀）。若不符合，尝试修正并告知用户修正内容。
3. 交互确认：若步骤 1、2 中**对用户非空的输入做了调整**（如修正了版本号格式），必须在继续前提示用户确认调整内容，得到确认后方可继续。
4. 生成 tag message：
   - 通过 `git log <上一个tag>..HEAD` 获取区间内所有 commit 的完整信息（标题及描述），不只用 `--oneline`。
   - 不查看代码，仅根据 commit message 将改动归类为 **Features**、**Bug Fixes**、**Others** 三类。
   - 自动生成一句概括性的大版本标题（中文，≤50 字符），概括本次版本的主要变化方向。
   - 每条描述末尾以句号（。）结尾，除非末尾是代码符号或链接。
   - 按以下格式（首行标题 → 空行 → Markdown 正文）：

```
<概括性标题，≤50字符>

## Features

- 改动描述 1。
- 改动描述 2。

## Bug Fixes

- 修复描述 1。

## Others

- 其它改动 1。
```

   - `## Features` 仅包含新增功能；`## Bug Fixes` 仅包含 bug 修复；无法归入前两类的（重构、文档、CI、样式调整等）写入 `## Others`。
   - 无内容的分类直接省略，不输出空标题（如 `## Bug Fixes` 下无条目则不出现）。
   - 过滤抵消项：同一版本内新增后又删除的功能相互抵消，不写入 message；同一版本内引入又在同一版本内修复的 bug 相互抵消，不写入。
5. 处理 `CHANGELOG.md`：
   - 若文件不存在，创建并写入 `# Change Log` 标题。
   - **若该版本已存在于 CHANGELOG.md 中**：对比已有内容与步骤 4 生成的 message。若差异微小，将已有内容转换为 tag message 格式（补充概括性标题，`###` 分类标题降为 `##`，移除版本号标题行）；若差异较大，按步骤 4 的格式修改，并新增一个提交（标题不能与之前 CHANGELOG 提交相同）。
   - **若该版本不存在**：插入新条目，内容格式与已有条目保持一致（表达方式、标点习惯、代码引用风格等）。
   - 插入内容格式为（注意 CHANGELOG 中版本标题为 `##`，分类标题为 `###`）：

```
## <version>

### Features

- 描述 1。

### Bug Fixes

- 描述 1。

### Others

- 描述 1。
```

   - 无内容的分类（`### ...`）直接省略，不留空标题。
   - 插入位置规则（逆序，新版本在上）：
     - 若新版本比所有已有版本都新 → 插入到 `# Change Log` 之后、第一个 `##` 之前。
     - 若新版本是已有 MAJOR.MINOR 系列的 patch → 插入到该系列区间内最上面。即位于更高 MAJOR.MINOR 之下、同系列最高 PATCH 之上。
   - 读取策略：仅读取 `CHANGELOG.md` 的前 50 行或 `grep -n '^## '` 获取版本号和行号，不读取全文件。
6. 提交 CHANGELOG.md（若有修改）：调用 `my-git-commit` skill 完成提交。如该版本已存在且被修改，提交标题不能与之前同版本的 CHANGELOG 提交重复。
7. 执行 `git tag -a <tag_name> -m "<message>"`。tag 打在第 6 步新产生的提交上（若无新提交则打在 HEAD）。
8. 将 tag 的版本号和内容摘要保存到项目记忆，便于后续查询。
