#!/usr/bin/env python3
"""Hook: auto-format shell scripts after Write/Edit with shfmt."""
import json
import os
import subprocess
import sys

SHELL_EXTS = {".sh", ".bash", ".zsh"}


def find_shfmt():
    """Return True if shfmt is available."""
    return subprocess.run(["which", "shfmt"], capture_output=True,
                          check=False).returncode == 0


def main():
    event = json.load(sys.stdin)
    tool_name = event.get("tool_name", "")

    if tool_name not in ("Write", "Edit"):
        return

    file_path = event.get("tool_input", {}).get("file_path", "")
    _, ext = os.path.splitext(file_path)
    if ext not in SHELL_EXTS:
        return
    if not os.path.isfile(file_path):
        return

    if not find_shfmt():
        print(
            f"[shell-format] shfmt 未安装，跳过格式化: {file_path}",
            file=sys.stderr,
        )
        return

    result = subprocess.run(
        ["shfmt", "-w", "-i", "4", file_path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            f"[shell-format] shfmt 格式化失败 {file_path}: {result.stderr.strip()}",
            file=sys.stderr,
        )
    else:
        print(f"[shell-format] shfmt 已格式化: {file_path}")


if __name__ == "__main__":
    main()
