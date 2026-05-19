# Change Log

## 0.1.1

### Features

- tag message 首行增加概括性大版本标题（≤50 字符），便于 `git tag -ln` 显示。

### Bug Fixes

- 修复从 CHANGELOG.md 搬运内容至 tag message 时，丢失 `## Features` 等分类标题的问题。

## 0.1.0

### Features

- 新增`/my-git-commit`命令：暂存并提交，生成中文规范提交信息，支持多 commit 拆分。
- 新增`/my-git-amend`命令：将修改合并到上一次提交并更新提交信息。
- 新增`/my-git-push`命令：推送本地提交，失败时分析原因。
- 新增`/my-git-pull`命令：拉取远程代码，复杂合并自动回退。
- 新增`/my-git-tag`命令：语义化版本管理，自动生成改动摘要并同步`CHANGELOG.md`。
- 新增`/my-new-command`命令：根据描述创建新命令文件，自动学习既有模式生成。
- 新增`install.py`安装脚本：支持安装、测试、卸载。

### Others

- Initial commit.
- 重构`install.py`代码结构。
- 添加`.gitignore`忽略编辑器临时文件。
- 添加`README.md`与`CLAUDE.md`项目文档。
- 优化命令文件格式，便于大模型理解。
