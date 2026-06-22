# my-claude

Claude Code 自定义命令与配置项目。

## 命令

| 命令 | 用途 |
|------|------|
| `my-git-amend` | 将修改合并到上一次提交，同步更新提交信息 |
| `my-git-tag` | 打语义化版本 tag，自动归类 commit 生成改动摘要 |
| `my-new-command` | 根据描述创建新的 Claude Code 命令文件 |
| `my-new-hook` | 新增 Claude Code hook，支持直接操作 ~/.claude 或在项目中输出到 hooks/ 目录 |
| `my-plugin-init` | 初始化开发环境，安装推荐的插件和工具 |

## 技能

`skills/` 下的 `.md` 文件通过 `install.py` 软链接到 `~/.claude/skills/`，作为可被 Claude 自主调用的 skill。

| Skill | 用途 |
|------|------|
| `my-mermaid` | 生成色彩合理、分组清晰的 mermaid 图，自动推测图类型，支持上下文分析和交互确认 |
| `my-git-commit` | 暂存并提交，生成规范的中文提交信息，支持多 commit 拆分 |
| `my-code-io` | 基于代码生成中文技术介绍文，含图表和多章节，面向非专业读者 |

## 配置片段

`settings/` 下的 JSON 文件在安装时会 deep-merge 到 `~/.claude/settings.json`，按功能分为：

| 文件 | 用途 |
|------|------|
| `default.json` | 通用偏好：权限、主题、自动记忆、遥测开关、effort 级别等 |
| `deepseek-v4.json` | DeepSeek V4 提供商：接口地址、模型映射、子 agent 模型、compact 窗口等 |
| `spinner_verbs.json` | 自定义 spinner 加载文案 |
| `mem-lite.json` | mem-lite 的 MCP 工具权限：搜索、记忆、维护等 |
| `context7.json` | context7 的 MCP 工具权限：库文档查询 |
| `agent-bell.json` | agent-bell 的 Stop 和 Notification hook 配置 |
| `_anthropic.json` | （可选）Anthropic 官方模型：Opus/Sonnet/Haiku 分层映射。`_` 前缀文件默认不安装 |

`_` 前缀的 JSON 文件默认跳过安装，可通过 `./install.py --settings settings/_anthropic.json` 强制安装。

`hooks/` 下可放置 hook 的 JSON 配置和脚本，安装时 JSON 合并到 settings.json，脚本软链接到 `~/.claude/hooks/`。

| 文件 | 用途 |
|------|------|
| `python_format` | 对 Python 文件 Write/Edit 后自动执行 yapf 或 black 格式化 |
| `shell_format` | 对 Shell 脚本 Write/Edit 后自动执行 shfmt 格式化 |
| `_notification` | Stop 和 Notification 事件的桌面通知（默认禁用，`_` 前缀） |

## 推荐插件

运行 `my-plugin-init` 可一键检测并安装。已安装的自动跳过。

| 插件 | 方式 | 用途 |
|------|------|------|
| `claude-mem-lite` | npm | 跨会话持久记忆，SQLite FTS5 全文检索 |
| `context7` | 官方插件 | 拉取版本匹配的库文档，消除已废弃 API 的幻觉 |
| `explanatory-output-style` | 官方插件 | 教育式解释实现选择，输出附带设计决策说明 |
| `agent-bell` | npm | 桌面通知与音效：Stop/Notification 事件触发，冷却防轰炸 |

## 安装

```sh
./install.py
```

将 `commands/*.md` 软链接到 `~/.claude/commands/`，`skills/` 下内容软链接到 `~/.claude/skills/`，`settings/*.json` 和 `hooks/*.json` deep-merge 到 `~/.claude/settings.json`，`hooks/` 下脚本软链接到 `~/.claude/hooks/`。

## 卸载

```sh
./install.py --revert
```

删除指向本仓库的软链接，移除 settings.json 中由本项目添加的配置项。

## 其他选项

```sh
./install.py --root /custom/path          # 自定义目标根目录
./install.py --settings path/to/file.json # 强制安装指定 settings 文件
./install.py --hooks path/to/hook.json    # 强制安装指定 hook
./install.py --test                       # 安装到 /tmp 并校验，测试后自动清理
```
