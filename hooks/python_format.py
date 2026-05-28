#!/usr/bin/env python3
"""Hook: auto-format Python files after Write/Edit with yapf or black."""
import json
import os
import subprocess
import sys


def find_formatter():
    """Return the first available Python formatter command, or None."""
    for cmd in (["yapf", "-i"], ["black"]):
        if subprocess.run(["which", cmd[0]],
                          capture_output=True).returncode == 0:
            return cmd
    return None


def main():
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
