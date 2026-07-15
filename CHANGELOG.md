# Change Log

## 0.3.0

### Features

- my-mermaid、my-code-io、my-git-commit、my-git-amend 四个核心功能从命令迁移为 skill，支持 Claude 根据场景自主调用。
- 新增 my-changelog skill：管理 CHANGELOG.md，判断当前版本、归类整合 commit 并逆序插入，与 my-git-tag 共享版本判断逻辑。
- my-mermaid 全面升级：参考文件重写为 11 个按需加载的 reference，新增 subgraph 业务语义着色、方向布局与隐式分层规则、配色分组扩展，提取共享 classDef 配色供所有图类型复用。
- my-code-io 大幅增强：分析维度扩展至 9 组 × 29 个维度，新增图表类型路由表，输出路径改为 `~/Documents/claude/<project>`，支持 `<output>` 路径参数，步骤 3 拆为大纲/位置推导/确认/调整子步骤。
- 新增 lua_format hook：Lua 文件 Write/Edit 后自动执行 stylua 格式化。
- install.py 新增 skills 目录级安装支持，权限配置（permissions.allow）支持多文件 union 合并。
- AskUserQuestion 交互规范全面落地：新增项目级规则明确定义，所有 skill/command 交互点统一改造为显式调用。
- 新增 `_anthropic.json` 可选官方模型配置（Opus/Sonnet/Haiku 分层映射），`provider.json` 重命名为 `deepseek-v4.json` 并移入 compact 窗口配置。

### Bug Fixes

- 修复 my-code-io 图表步骤自行手绘 mermaid 导致丢失配色的问题，改为强制经 my-mermaid skill 生成图代码。
- 补全 skill frontmatter 缺失的 `allowed-tools` 权限声明。

### Others

- 新增 `.claude/rules/command-structure.md` 与 `skill-structure.md` 项目级规则，定义目录结构、格式、交互与 Skill 间调用等规范。
- 完善 skill description 触发短语与调用模式，强化自主调用识别能力。
- my-git-commit 参考文件拆分为 message/prefix/split 三份，规范识别优化为无需显式读取 CLAUDE.md。
- my-git-tag 提交 CHANGELOG 改为经 my-git-commit skill。
- 统一 mermaid 图类型选择表为单一事实来源（type-index.md），inline 小体积 reference 到 SKILL.md，清理死引用。
- README 新增推荐插件章节、补全 settings 表与 hooks JSON 合并说明。

## 0.2.0

### Features

- 新增 my-new-hook 命令：创建和安装 Claude Code hook，支持项目级和全局两种输出模式。
- 新增 python_format hook：Python 文件 Write/Edit 后自动执行 yapf 或 black 格式化。
- 新增 shell_format hook：Shell 脚本 Write/Edit 后自动执行 shfmt 格式化。
- 新增 _notification hook：Stop/Notification 事件桌面通知，支持 macOS/Linux/tmux，含项目名标注。
- install.py 全面支持 hooks 事件列表 union-merge：同一事件下多个 JSON 文件的条目可共存。
- 新增 my-plugin-init 命令：增量安装推荐插件（claude-mem-lite、context7、explanatory-output-style、agent-bell）。
- 新增 mem-lite.json、context7.json、agent-bell.json 三个 settings 权限与 hook 配置片段。
- my-git-commit 引入 Conventional Commits 前缀规范，含 CLAUDE.md/记忆/历史三层识别体系。
- 新增 my-mermaid 命令：15 种 Mermaid 图类型决策指南，含按类型差异化的大小控制策略。
- 新增 my-code-io 命令：基于代码生成中文技术介绍文，含图表和多章节。
- permissions.allow 数组支持多 settings 文件 union 合并与独立逐条卸载。
- install.py 新增 --settings 强制安装参数与失效软链接自动清理。

### Bug Fixes

- 修复 install.py --revert 部分还原失败与 docstring 描述错误。
- 修正 hooks JSON 中 hook 事件名与格式问题。
- 修正 my-mermaid 标题示例中 graph→flowchart 废弃语法。

### Others

- 删除闲置的 my-git-push 和 my-git-pull 命令。
- 重组 settings 配置片段：拆分为 default/provider/spinner_verbs/rtk。
- 完善 CLAUDE.md：新增目录结构与同步策略。

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
