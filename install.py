#!/usr/bin/env python3
"""安装本项目。"""

import argparse
import os
import sys
from pathlib import Path

def main():
    """将 commands/ 下的 .md 文件软链接到 root/commands/ 目录。"""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "--root", "-r",
        default="~/.claude",
        help="安装目标根目录，默认为 ~/.claude",
    )
    args = parser.parse_args()

    src_dir = Path(__file__).resolve().parent / "commands"
    root = Path(args.root).expanduser()
    dst_dir = root / "commands"

    if not src_dir.is_dir():
        print(f"源目录不存在: {src_dir}", file=sys.stderr)
        sys.exit(1)

    dst_dir.mkdir(parents=True, exist_ok=True)
    installed = 0

    for src in sorted(src_dir.glob("*.md")):
        dst = dst_dir / src.name

        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                print(f"跳过（已正确）: {dst.name}")
                continue
            print(f"修正: {dst.name} -> {src}")
            dst.unlink()
        elif dst.exists():
            print(f"跳过（非软链接，实际文件）: {dst.name}")
            continue
        else:
            print(f"安装: {dst.name}")

        dst.symlink_to(src)
        installed += 1

    print(f"\n完成，共安装 {installed} 个命令。")

if __name__ == "__main__":
    main()
