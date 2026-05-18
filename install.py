#!/usr/bin/env python3
"""Install this project's commands to Claude Code."""

import argparse
import os
import shutil
import sys
from pathlib import Path


def install_commands(src_dir, dst_dir):
    """Symlink .md files from src_dir into dst_dir.

    Return count of installed.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    installed = 0

    for src in sorted(src_dir.glob("*.md")):
        dst = dst_dir / src.name

        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                print(f"  skip   : {dst.name} (correct)")
                continue
            print(f"  fix    : {dst.name} -> {src}")
            dst.unlink()
        elif dst.exists():
            print(f"  skip   : {dst.name} (existing file)")
            continue
        else:
            print(f"  install: {dst.name}")

        dst.symlink_to(src)
        installed += 1

    return installed


def _validate(src_dir, dst_dir):
    passed = 0
    failed = 0
    src_files = {f.name: f for f in src_dir.glob("*.md")}
    dst_files = {}

    for f in dst_dir.iterdir():
        if f.name in dst_files:
            print(f"  ✗ {f.name} (duplicate)")
            failed += 1
            continue
        dst_files[f.name] = f

    for name, src in sorted(src_files.items()):
        dst = dst_dir / name
        if not dst.exists():
            print(f"  ✗ {name} (missing)")
            failed += 1
            continue
        if not dst.is_symlink():
            print(f"  ✗ {name} (not a symlink)")
            failed += 1
            continue
        if os.readlink(dst) != str(src):
            print(f"  ✗ {name} -> {os.readlink(dst)} (expected: {src})")
            failed += 1
            continue
        print(f"  ✓ {name}")
        passed += 1

    # 检查多余文件
    extra = set(dst_files) - set(src_files)
    for name in sorted(extra):
        print(f"  ✗ {name} (extra)")
        failed += 1

    return passed, failed


def _run_test(src_dir):
    root = Path("/tmp/my-claude")
    dst_dir = root / "commands"

    print(f"=== Install test ({dst_dir}) ===\n")

    installed = install_commands(src_dir, dst_dir)
    print(f"\nInstalled {installed} commands.\n")

    print("=== Validation ===")
    passed, failed = _validate(src_dir, dst_dir)

    print(f"\nClean up {root} ...")
    shutil.rmtree(root)

    result = "PASSED" if failed == 0 else "FAILED"
    print(f"\n=== Test {result}: {passed} passed, {failed} failed ===")
    sys.exit(0 if failed == 0 else 1)


def main():
    """Symlink commands/*.md into root/commands/."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--root",
        "-r",
        default="~/.claude",
        help="target root directory (default: ~/.claude)",
    )
    group.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="install to /tmp/my-claude/, validate, then clean up",
    )
    args = parser.parse_args()

    src_dir = Path(__file__).resolve().parent / "commands"
    if not src_dir.is_dir():
        print(f"Source directory not found: {src_dir}", file=sys.stderr)
        sys.exit(1)

    if args.test:
        _run_test(src_dir)
    else:
        root = Path(args.root).expanduser()
        dst_dir = root / "commands"

        installed = install_commands(src_dir, dst_dir)
        print(f"\nDone. {installed} commands installed.")


if __name__ == "__main__":
    main()
