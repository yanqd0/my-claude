# my-claude

Claude Code 自定义命令集，提供规范的 git 操作流程。

## 命令

| 命令 | 用途 |
|------|------|
| `my-git-commit` | 暂存并提交，生成中文规范提交信息，支持多 commit 拆分 |
| `my-git-amend` | 将修改合并到上一次提交，同步更新提交信息 |
| `my-git-push` | 推送本地提交，失败时分析原因 |
| `my-git-pull` | 拉取远程代码，复杂合并自动回退并展示差异 |
| `my-git-tag` | 打语义化版本 tag，自动归类 commit 生成改动摘要 |
| `my-mermaid` | 生成色彩合理、分组清晰的 mermaid 图，支持自动推测图类型和上下文分析 |
| `my-code-io` | 基于代码生成中文技术介绍文，含图表和多章节，面向非专业读者 |

## 安装

```sh
./install.py
```

将 `commands/*.md` 软链接到 `~/.claude/commands/`，Claude Code 即可识别。

## 卸载

```sh
./install.py --revert
```

删除指向本仓库的软链接和失效链接，不影响实际文件。

## 其他选项

```sh
./install.py --root /custom/path    # 自定义目标根目录
./install.py --test                 # 安装到 /tmp 并校验，测试后自动清理
```
