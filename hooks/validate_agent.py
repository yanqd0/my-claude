#!/usr/bin/env python3
"""Hook: validate agent .md files after Write/Edit."""
import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    """PostToolUse hook：对 Write/Edit 的 agent .md 文件自动校验。

    1. 从 stdin 读取 hook 事件 JSON。
    2. 过滤：仅处理工具名称为 Write 或 Edit 的事件。
    3. 过滤：仅处理路径中 agents/ 为目录组件且以 .md 结尾的文件。
    4. 调用同目录 validate-agent.sh 执行校验。
    5. 透传退出码和输出。
    """
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    tool_name = event.get("tool_name", "")

    if tool_name not in ("Write", "Edit"):
        return

    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path or not file_path.endswith(".md"):
        return
    if "agents" not in Path(file_path).parent.name:
        return
    if not os.path.isfile(file_path):
        return

    script_dir = os.path.dirname(os.path.realpath(__file__))
    validator = os.path.join(script_dir, "validate-agent.sh")

    result = subprocess.run(
        ["bash", validator, file_path],
        check=False,
    )

    if result.returncode != 0:
        print(
            f"[validate-agent] 校验失败，请修复上述问题: {file_path}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
