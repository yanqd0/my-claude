---
allowed-tools: Read Write Bash(chmod:*) Edit AskUserQuestion
description: 新增 Claude Code hook，支持直接操作 ~/.claude 或在项目中输出到 hooks/ 目录。
---

新增一个 Claude Code hook。支持三个参数，依次为：`<name> <description_or_script> [event]`。

## 执行步骤

1. 解析参数：
   - `<name>`：hook 名称，用于命名文件（`<name>.json`、`<name>.py`）。
   - `<description_or_script>`：hook 的描述或脚本。若为存在的 `.py` 文件路径则直接使用；若为存在的其他脚本路径也接受；若为自然语言描述则生成 Python 3 脚本。
   - `[event]`：可选，hook 事件名称。Claude Code 当前支持的 hook 事件包括：
     - `PreToolUse` / `PostToolUse` / `PostToolUseFailure` — 工具调用前后
     - `UserPromptSubmit` / `UserPromptExpansion` — 用户提示词
     - `SessionStart` / `SessionEnd` — 会话开始/结束
     - `Stop` / `StopFailure` — 停止/停止失败
     - `SubagentStart` / `SubagentStop` — 子 agent 启停
     - `PreCompact` / `PostCompact` — 压缩前后
     - `PermissionRequest` / `PermissionDenied` — 权限请求
     - `Notification` — 通知
     - `PreToolBatch` / `PostToolBatch` — 工具批处理前后
     - `FileChanged` / `CwdChanged` — 文件/目录变更
     - `ConfigChange` — 配置变更
     - `Setup` / `TaskCreated` / `TaskCompleted` / `TeammateIdle` / `InstructionsLoaded` / `Elicitation` / `ElicitationResult` / `WorktreeCreate` / `WorktreeRemove`
2. 推测 event：
   - 若用户提供的 event 在支持列表中，直接使用。
   - 若 event 参数为空或不在支持列表中，根据 `<description_or_script>` 的内容推测最匹配的事件，用 `AskUserQuestion`（单选）列出候选事件让用户选定：推荐项置首并在 label 标注（推荐），description 写明理由。
3. 生成内容：
   - **hook JSON**：格式如下，`command` 值按安装目标选择不同路径（**全局** vs **项目级**）：
     ```json
     {
       "hooks": {
         "<EventName>": [
           {
             "matcher": "<pattern or empty for all>",
             "hooks": [
               {
                 "type": "command",
                 "command": "~/.claude/hooks/<name>.py"
               }
             ]
           }
         ]
       }
     }
     ```
     项目级 hook 将 `command` 替换为 `"${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>.py"`。Claude Code 运行时自动解析 `${CLAUDE_PROJECT_DIR}` 为项目根路径，确保无论从哪个子目录触发都能找到脚本。绝对不要写死为项目绝对路径或相对路径。若需要限定工具类型，在 matcher 中填写工具名或模式；否则留空。若需要多个 hook 动作，在 `hooks` 数组中追加即可。
   - **hook 脚本**：默认使用 Python 3，从 stdin 读取 Claude Code 传入的 JSON 事件数据。脚本**必须**在首行写明 shebang，写入后执行 `chmod +x`。若用户提供了现成脚本文件，检查并补全 shebang 后直接复制使用。
4. 交互确认：将 JSON 片段和 Python 脚本内容完整展示，用 `AskUserQuestion`（单选）确认，选项如"写入"、"修改后再写入（在 Other 描述改动）"；选择修改则按反馈迭代后重新确认。
5. 写入文件：
   - **默认模式**（非本项目）：直接操作 `~/.claude/`。
     - JSON 片段：读取 `~/.claude/settings.json`，将 hook 配置 deep-merge 进去后写回。若文件不存在则创建。
     - 脚本：写入 `~/.claude/hooks/<name>.py`（不存在则创建目录），执行 `chmod +x`。
   - **项目模式**（若当前工作目录存在 `CLAUDE.md` 且其中指示了 `my-new-hook` 项目级写入策略）：输出到项目目录。
     - JSON 片段：写入 `hooks/<name>.json`。
     - 脚本：写入 `hooks/<name>.py`，执行 `chmod +x`。
     写入完成后，执行 `./install.py --hooks hooks/<name>.json` 完成安装，并同步更新 `README.md`。
     若项目不使用 `install.py` 而是直接写 `.claude/settings.json`，则 JSON 写入 `.claude/settings.json`（deep-merge），脚本写入 `.claude/hooks/<name>.py`，`command` 使用 `${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>.py`。

## 格式规范

- hook 动作通过 `hooks` 数组定义，每项包含 `type`（固定为 `"command"`）和 `command`（要执行的命令）。`command` 值直接指向脚本路径，依赖脚本 shebang 执行，**不写** `python3` 前缀。路径选择取决于安装目标：
  - **全局 hook**（安装到 `~/.claude/`）：`command` 用 `~/.claude/hooks/<name>.py`，脚本位于 `~/.claude/hooks/`。
  - **项目级 hook**（安装到项目目录）：`command` **必须**用 `${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>.py`。Claude Code 运行时自动解析该变量为项目根路径，避免因子目录 `cwd` 不同导致找不到脚本。绝对不要写死为项目绝对路径（如 `/home/user/project/...`）或相对路径（如 `./.claude/hooks/...`），这些在克隆/移动项目后会失效。
- **shebang 与依赖管理**：脚本**必须**在首行写明 shebang，写入后执行 `chmod +x` 确保可执行。
  - **简单脚本**（仅 Python 标准库 + 系统 CLI 工具依赖）：使用 `#!/usr/bin/env python3`。现有 hooks 均为此模式。
  - **复杂脚本**（需要第三方 Python 包）：使用 `#!/usr/bin/env -S uv run`，并通过 PEP 723 内联元数据（`# /// script` … `# ///`）在脚本头部声明依赖，无需额外 `requirements.txt`。例：
    ```python
    #!/usr/bin/env -S uv run
    # /// script
    # requires-python = ">=3.12"
    # dependencies = ["httpx>=1.0", "rich"]
    # ///
    import httpx, rich, sys, json
    ...
    ```
  - Hook JSON 中的 `command` 无需感知脚本是 `python3` 还是 `uv run`——两者均由 shebang 自动处理。
- 脚本的 `matcher` 为空字符串时匹配所有触发，填写工具名或正则时仅匹配符合条件的。
- 多个 hook 配置可合并写入同一个 event 数组。
- hook 名称（`<name>`）使用小写字母、数字和下划线（`_`），不使用中划线（`-`）。与目标语言命名习惯保持一致（如 Python 用 `python_format` 而非 `python-format`）。
