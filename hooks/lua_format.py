#!/usr/bin/env python3
"""Hook: auto-format Lua files after Write/Edit with stylua."""
import json
import os
import shutil
import subprocess
import sys


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool_name = event.get("tool_name", "")

    if tool_name not in ("Write", "Edit"):
        return

    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".lua"):
        return
    if not os.path.isfile(file_path):
        return

    if not shutil.which("stylua"):
        print(
            f"[lua-format] stylua 未安装，跳过格式化: {file_path}",
            file=sys.stderr,
        )
        return

    result = subprocess.run(
        ["stylua", file_path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            f"[lua-format] stylua 格式化失败 {file_path}: {result.stderr.strip()}",
            file=sys.stderr,
        )
    else:
        print(f"[lua-format] stylua 已格式化: {file_path}")


if __name__ == "__main__":
    main()
