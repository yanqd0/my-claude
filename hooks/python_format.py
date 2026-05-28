#!/usr/bin/env python3
"""Hook: auto-format Python files after Write/Edit with yapf or black."""
import json
import os
import subprocess
import sys


def find_formatter():
    """Return the first available Python formatter command, or None."""
    for cmd in (["yapf", "-i"], ["black"]):
        proc = subprocess.run(
            ["which", cmd[0]],
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            return cmd
    return None


def main():
    """PostToolUse hook：对 Write/Edit 的 Python 文件自动执行格式化。

    1. 从 stdin 读取 hook 事件 JSON。
    2. 过滤：仅处理工具名称为 Write 或 Edit 的事件。
    3. 过滤：仅处理以 .py 结尾且实际存在的文件。
    4. 查找可用格式化工具（yapf 优先，其次 black）。
    5. 执行格式化，输出结果或错误信息到 stderr。
    """
    event = json.load(sys.stdin)
    tool_name = event.get("tool_name", "")

    # Only act on Write / Edit
    if tool_name not in ("Write", "Edit"):
        return

    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path or not file_path.endswith(".py"):
        return

    if not os.path.isfile(file_path):
        return

    formatter = find_formatter()
    if formatter is None:
        print(
            f"[python-format] yapf 和 black 均未安装，"
            f"跳过格式化: {file_path}",
            file=sys.stderr,
        )
        return

    result = subprocess.run(
        formatter + [file_path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            f"[python-format] {formatter[0]} 格式化失败 "
            f"{file_path}: {result.stderr.strip()}",
            file=sys.stderr,
        )
    else:
        print(f"[python-format] {formatter[0]} 已格式化: {file_path}")


if __name__ == "__main__":
    main()
