# my-claude

Claude Code 自定义命令与配置项目。

## 命令

| 命令 | 用途 |
|------|------|
| `my-git-commit` | 暂存并提交，生成中文规范提交信息，支持多 commit 拆分 |
| `my-git-amend` | 将修改合并到上一次提交，同步更新提交信息 |
| `my-git-tag` | 打语义化版本 tag，自动归类 commit 生成改动摘要 |
| `my-mermaid` | 生成色彩合理、分组清晰的 mermaid 图，支持自动推测图类型和上下文分析 |
| `my-code-io` | 基于代码生成中文技术介绍文，含图表和多章节，面向非专业读者 |
| `my-new-command` | 根据描述创建新的 Claude Code 命令文件 |
| `my-new-hook` | 新增 Claude Code hook，支持直接操作 ~/.claude 或在项目中输出到 hooks/ 目录 |
| `my-plugin-init` | 初始化开发环境，安装推荐的插件和工具 |

## 配置片段

`settings/` 下的 JSON 文件在安装时会 deep-merge 到 `~/.claude/settings.json`，按功能分为：

| 文件 | 用途 |
|------|------|
| `default.json` | 通用偏好：权限、主题、自动记忆、遥测开关、effort 级别、compact 窗口等 |
| `provider.json` | API 提供商配置：接口地址、模型映射、子 agent 模型等 |
| `spinner_verbs.json` | 自定义 spinner 加载文案 |

`hooks/` 下可放置 hook 的 JSON 配置和脚本，安装时 JSON 合并到 settings.json，脚本软链接到 `~/.claude/hooks/`。

| 文件 | 用途 |
|------|------|
| `python_format` | 对 Python 文件 Write/Edit 后自动执行 yapf 或 black 格式化 |
| `_notification` | Stop 和 Notification 事件的桌面通知（默认禁用，`_` 前缀） |

## 安装

```sh
./install.py
```

将 `commands/*.md` 软链接到 `~/.claude/commands/`，`settings/*.json` 合并到 `~/.claude/settings.json`，`hooks/` 下脚本软链接到 `~/.claude/hooks/`。

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
