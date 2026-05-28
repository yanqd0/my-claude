---
allowed-tools: Read Write Bash(chmod:*) Edit
description: 新增 Claude Code hook，支持直接操作 ~/.claude 或在项目中输出到 hooks/ 目录。
---

新增一个 Claude Code hook。支持三个参数，依次为：`<name> <description_or_script> [event]`。

## 执行步骤

1. 解析参数：
   - `<name>`：hook 名称，用于命名文件（`<name>.json`、`<name>.py`）。
   - `<description_or_script>`：hook 的描述或脚本。若为存在的 `.py` 文件路径则直接使用；若为存在的其他脚本路径也接受；若为自然语言描述则生成 Python 3 脚本。
   - `[event]`：可选，hook 事件名称。Claude Code 当前支持的 hook 事件包括：
     - `userPromptSubmit` — 用户提交提示词
     - `beforeToolUse` / `afterToolUse` — 工具调用前后
     - `stop` / `resume` — 会话停止/恢复
     - `startup` / `shutdown` — 启动/关闭
     - `notification` — 通知
     - `precompact` / `postcompact` — 压缩前后
2. 推测 event：
   - 若用户提供的 event 在支持列表中，直接使用。
   - 若 event 参数为空或不在支持列表中，根据 `<description_or_script>` 的内容推测最匹配的事件，列出候选（标注推荐项和理由），通过交互提示请用户确认。
3. 生成内容：
   - **hook JSON**：格式如下（标准 Claude Code hooks 配置）：
     ```json
     {
       "hooks": {
         "<EventName>": [
           {
             "matcher": "<pattern or empty for all>",
             "command": "python3 <path/to/<name>.py>"
           }
         ]
       }
     }
     ```
     若需要限定工具类型，在 matcher 中填写工具名或模式；否则留空。
   - **hook 脚本**：默认使用 Python 3，从 stdin 读取 Claude Code 传入的 JSON 事件数据。若用户提供了现成脚本文件，直接复制使用。
4. 交互确认：将 JSON 片段和 Python 脚本内容完整展示，得到确认后再写入。
5. 写入文件：
   - **默认模式**（非本项目）：直接操作 `~/.claude/`。
     - JSON 片段：读取 `~/.claude/settings.json`，将 hook 配置 deep-merge 进去后写回。若文件不存在则创建。
     - 脚本：写入 `~/.claude/hooks/<name>.py`（不存在则创建目录），执行 `chmod +x`。
   - **项目模式**（若当前工作目录存在 `CLAUDE.md` 且其中指示了 `my-new-hook` 项目级写入策略）：输出到项目目录。
     - JSON 片段：写入 `hooks/<name>.json`。
     - 脚本：写入 `hooks/<name>.py`，执行 `chmod +x`。
     写入完成后，执行 `./install.py --hooks hooks/<name>.json` 完成安装，并同步更新 `README.md`。

## 格式规范

- JSON 片段中的 `command` 字段：默认模式下用 `python3 ~/.claude/hooks/<name>.py`；项目模式下同样指向 `python3 ~/.claude/hooks/<name>.py`（因为 `install.py` 会将项目 `hooks/<name>.py` 软链接到 `~/.claude/hooks/<name>.py`，使用时脚本一定在该路径下）。
- 脚本的 `matcher` 为空字符串时匹配所有触发，填写工具名或正则时仅匹配符合条件的。
- 多个 hook 配置可合并写入同一个 event 数组。
- hook 名称（`<name>`）使用小写字母、数字和下划线（`_`），不使用中划线（`-`）。与目标语言命名习惯保持一致（如 Python 用 `python_format` 而非 `python-format`）。
