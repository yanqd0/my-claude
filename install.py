#!/usr/bin/env python3
"""Install this project's commands to Claude Code."""

import argparse
import json
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


# ── settings ───────────────────────────────────────────────────────────


def _deep_merge(base, overlay):
    """Merge overlay into base. Skip existing non-dict keys."""
    for key, value in overlay.items():
        if key in base:
            if isinstance(base[key], dict) and isinstance(value, dict):
                _deep_merge(base[key], value)
        else:
            base[key] = value


def _deep_revert(base, overlay):
    """Remove keys from base where values match overlay (recursing into dicts)."""
    for key, value in overlay.items():
        if key not in base:
            continue
        if isinstance(base[key], dict) and isinstance(value, dict):
            _deep_revert(base[key], value)
            if not base[key]:
                del base[key]
        elif base[key] == value:
            del base[key]


def install_settings(settings_dir, dst_path):
    """Merge settings/*.json into dst_path. Skip _prefixed files."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if dst_path.exists():
        base = json.loads(dst_path.read_text())
    else:
        base = {}

    installed = 0
    for src in sorted(settings_dir.glob("*.json")):
        if src.name.startswith("_"):
            print(f"  skip   : {src.name} (internal)")
            continue

        overlay = json.loads(src.read_text())

        before = json.dumps(base, sort_keys=True, ensure_ascii=False)
        _deep_merge(base, overlay)
        after = json.dumps(base, sort_keys=True, ensure_ascii=False)

        if before != after:
            print(f"  install: {src.name}")
            installed += 1
        else:
            print(f"  skip   : {src.name} (up to date)")

    dst_path.write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n")
    return installed


def _revert_settings(settings_dir, dst_path):
    """Remove matching keys from dst_path per settings/*.json. Skip _prefixed."""
    if not dst_path.exists():
        print(f"Settings file not found: {dst_path}")
        return 0

    base = json.loads(dst_path.read_text())

    reverted = 0
    for src in sorted(settings_dir.glob("*.json")):
        if src.name.startswith("_"):
            print(f"  skip   : {src.name} (internal)")
            continue

        overlay = json.loads(src.read_text())

        before = json.dumps(base, sort_keys=True, ensure_ascii=False)
        _deep_revert(base, overlay)
        after = json.dumps(base, sort_keys=True, ensure_ascii=False)

        if before != after:
            print(f"  revert : {src.name}")
            reverted += 1
        else:
            print(f"  skip   : {src.name} (no match)")

    dst_path.write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n")
    return reverted


def _verify_settings(settings_dir, settings_path):
    """Verify merged settings.json contains all source keys with correct values."""
    if not settings_dir.is_dir():
        return 0, 0

    if not settings_path.exists():
        print("  ✗ settings.json (missing)")
        return 0, 1

    merged = json.loads(settings_path.read_text())
    passed = 0
    failed = 0

    for src in sorted(settings_dir.glob("*.json")):
        if src.name.startswith("_"):
            continue

        source = json.loads(src.read_text())
        for key, value in source.items():
            p, f = _deep_check(merged, key, value)
            passed += p
            failed += f

    return passed, failed


def _deep_check(merged, key, source_value, path=None):
    """Recursively check merged[key] contains source_value. Returns (passed, failed)."""
    if path is None:
        path = key
    else:
        path = f"{path}.{key}"

    if key not in merged:
        print(f"  ✗ {path} (missing)")
        return 0, 1

    merged_val = merged[key]
    if isinstance(source_value, dict) and isinstance(merged_val, dict):
        p, f = 0, 0
        for k, v in source_value.items():
            dp, df = _deep_check(merged_val, k, v, path)
            p += dp
            f += df
        return p, f

    if merged_val == source_value:
        print(f"  ✓ {path}")
        return 1, 0

    print(f"  ✗ {path} (mismatch)")
    return 0, 1


# ── commands validation ────────────────────────────────────────────────


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


def _revert_commands(src_dir, dst_dir):
    """Remove symlinks that point to src_dir or are broken. Return count removed."""
    if not dst_dir.is_dir():
        print(f"Commands directory not found: {dst_dir}")
        return 0

    removed = 0
    for f in sorted(dst_dir.iterdir()):
        if f.is_symlink():
            target = os.readlink(f)
            if str(src_dir) in target or not f.exists():
                print(f"  remove: {f.name}")
                f.unlink()
                removed += 1
            else:
                print(f"  skip  : {f.name} (elsewhere)")
        else:
            print(f"  skip  : {f.name} (file)")

    return removed


def _run_test(src_dir, settings_dir):
    root = Path("/tmp/my-claude")
    dst_dir = root / "commands"

    print(f"=== Install test ({dst_dir}) ===\n")

    installed = install_commands(src_dir, dst_dir)
    print(f"\nInstalled {installed} commands.\n")

    print("=== Validation ===")
    passed, failed = _validate(src_dir, dst_dir)

    if settings_dir.is_dir():
        print("\n=== Settings install test ===")
        settings_path = root / "settings.json"
        installed_s = install_settings(settings_dir, settings_path)
        print(f"\n{installed_s} settings installed.\n")

        print("=== Settings verify ===")
        vp, vf = _verify_settings(settings_dir, settings_path)
        if vf > 0:
            failed += vf

        print("\n=== Settings revert test ===")
        reverted_s = _revert_settings(settings_dir, settings_path)
        print(f"\n{reverted_s} settings reverted.")

    print(f"\nClean up {root} ...")
    shutil.rmtree(root)

    result = "PASSED" if failed == 0 else "FAILED"
    print(f"\n=== Test {result}: {passed} passed, {failed} failed ===")
    sys.exit(0 if failed == 0 else 1)


def main():
    """Symlink commands/*.md into root/commands/."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "--root",
        "-r",
        default="~/.claude",
        help="target root directory (default: ~/.claude)",
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="install to /tmp/my-claude/, validate, then clean up",
    )
    action.add_argument(
        "--revert",
        action="store_true",
        help="remove symlinks pointing to this repo, and broken symlinks",
    )
    args = parser.parse_args()

    src_dir = Path(__file__).resolve().parent / "commands"
    if not src_dir.is_dir():
        print(f"Source directory not found: {src_dir}", file=sys.stderr)
        sys.exit(1)

    root = Path(args.root).expanduser()
    dst_dir = root / "commands"
    settings_dir = Path(__file__).resolve().parent / "settings"
    settings_path = root / "settings.json"

    if args.test:
        _run_test(src_dir, settings_dir)
    elif args.revert:
        removed = _revert_commands(src_dir, dst_dir)
        print(f"\nDone. {removed} symlinks removed.")

        if settings_dir.is_dir():
            print("\n=== Settings ===")
            reverted_s = _revert_settings(settings_dir, settings_path)
            print(f"\nDone. {reverted_s} settings reverted.")
    else:
        installed = install_commands(src_dir, dst_dir)
        print(f"\nDone. {installed} commands installed.")

        if settings_dir.is_dir():
            print("\n=== Settings ===")
            installed_s = install_settings(settings_dir, settings_path)
            print(f"\nDone. {installed_s} settings installed.")


if __name__ == "__main__":
    main()
