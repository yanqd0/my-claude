#!/usr/bin/env python3
"""Install this project's commands, skills and agents to Claude Code."""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def _install_items(src_dir, dst_dir, label="", glob_pattern="*.md"):
    """Symlink items from src_dir into dst_dir.

    *glob_pattern* controls what is matched (commands: "*.md",
    skills: "*" for both .md files and directories).
    Return count of installed.  *label* is used in log lines.
    """
    if not src_dir.is_dir():
        return 0

    dst_dir.mkdir(parents=True, exist_ok=True)
    installed = 0
    tag = f" ({label})" if label else ""

    for src in sorted(src_dir.glob(glob_pattern)):
        if src.name.startswith("."):
            continue
        dst = dst_dir / src.name

        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                print(f"  skip   : {dst.name}{tag} (correct)")
                continue
            print(f"  fix    : {dst.name}{tag} -> {src}")
            dst.unlink()
        elif dst.exists():
            print(f"  skip   : {dst.name}{tag} (existing file)")
            continue
        else:
            print(f"  install: {dst.name}{tag}")

        dst.symlink_to(src)
        installed += 1

    # Clean up broken symlinks (from deleted source files)
    for dst in sorted(dst_dir.iterdir()):
        if dst.is_symlink() and not dst.exists():
            print(f"  cleanup: {dst.name}{tag} (broken link)")
            dst.unlink()

    return installed


def install_commands(src_dir, dst_dir):
    """Symlink commands/*.md into ~/.claude/commands/."""
    return _install_items(src_dir, dst_dir)


def install_skills(src_dir, dst_dir):
    """Symlink skills/* into ~/.claude/skills/ (dirs and .md files)."""
    return _install_items(src_dir, dst_dir, label="skills", glob_pattern="*")


def install_agents(src_dir, dst_dir):
    """Symlink agents/*.md into ~/.claude/agents/."""
    return _install_items(src_dir, dst_dir, label="agents")


# ── settings ───────────────────────────────────────────────────────────


def _deep_merge(base, overlay, force=False, _parent_key=None):
    """Merge overlay into base. Skip existing non-dict keys unless force=True.

    ANTHROPIC_AUTH_TOKEN is never overwritten, regardless of force.
    permissions.allow arrays are union-merged instead of overwritten.
    Hook event arrays (PostToolUse, Stop, etc.) are also union-merged.
    """
    for key, value in overlay.items():
        if key == "ANTHROPIC_AUTH_TOKEN":
            continue
        if key in base:
            if isinstance(base[key], dict) and isinstance(value, dict):
                _deep_merge(base[key], value, force, _parent_key=key)
            elif (
                _parent_key == "permissions" and key == "allow"
                and isinstance(base[key], list) and isinstance(value, list)
            ):
                for item in value:
                    if item not in base[key]:
                        base[key].append(item)
            elif (
                _parent_key == "hooks" and isinstance(base[key], list)
                and isinstance(value, list)
            ):
                _existing = {json.dumps(e, sort_keys=True) for e in base[key]}
                for item in value:
                    if json.dumps(item, sort_keys=True) not in _existing:
                        base[key].append(item)
            elif force:
                base[key] = value
        else:
            base[key] = value


def _deep_revert(base, overlay, _parent_key=None):
    """Remove keys from base where values match overlay (recursing into dicts).

    permissions.allow and hook event arrays are reverted by removing
    matching entries individually instead of removing the whole key.
    """
    for key, value in overlay.items():
        if key not in base:
            continue
        if isinstance(base[key], dict) and isinstance(value, dict):
            _deep_revert(base[key], value, _parent_key=key)
            if not base[key]:
                del base[key]
        elif (
            isinstance(base[key], list) and isinstance(value, list)
            and ((_parent_key == "permissions" and key == "allow")
                 or _parent_key == "hooks")
        ):
            _to_remove = {json.dumps(e, sort_keys=True) for e in value}
            base[key] = [
                e for e in base[key]
                if json.dumps(e, sort_keys=True) not in _to_remove
            ]
            if not base[key]:
                del base[key]
        elif base[key] == value:
            del base[key]


def install_settings(settings_dir, dst_path, forced=None):
    """Merge settings/*.json into dst_path.

    When forced is non-empty, only those files are processed (force=True).
    Otherwise all non-_-prefixed files in settings_dir are merged normally.
    """
    if forced is None:
        forced = set()

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if dst_path.exists():
        base = json.loads(dst_path.read_text())
    else:
        base = {}

    installed = 0

    if forced:
        sources = [Path(p) for p in sorted(forced)]
    else:
        sources = sorted(settings_dir.glob("*.json"))

    for src in sources:
        if not forced:
            if src.name.startswith("_"):
                print(f"  skip   : {src.name} (internal)")
                continue

        overlay = json.loads(src.read_text())
        is_forced = bool(forced)

        before = json.dumps(base, sort_keys=True, ensure_ascii=False)
        _deep_merge(base, overlay, force=is_forced)
        after = json.dumps(base, sort_keys=True, ensure_ascii=False)

        if before != after:
            tag = "force" if is_forced else "install"
            print(f"  {tag}: {src.name}")
            installed += 1
        else:
            print(f"  skip   : {src.name} (up to date)")

    dst_path.write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n")
    return installed


def _revert_settings(settings_dir, dst_path, forced=None):
    """Remove matching keys from dst_path per settings/*.json. Skip _prefixed.

    When forced is non-empty, only revert the specified JSON files.
    """
    if not dst_path.exists():
        print(f"Settings file not found: {dst_path}")
        return 0

    base = json.loads(dst_path.read_text())

    if forced is not None:
        sources = [Path(p) for p in sorted(forced)]
        sources = [s for s in sources if s.suffix == ".json"]
    else:
        sources = sorted(settings_dir.glob("*.json"))
        sources = [s for s in sources if not s.name.startswith("_")]

    reverted = 0
    for src in sources:
        if not src.is_file():
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

    if reverted > 0:
        dst_path.write_text(
            json.dumps(base, indent=2, ensure_ascii=False) + "\n"
        )
    return reverted


# ── mcp ──────────────────────────────────────────────────────────────────


def install_mcp(mcp_dir, dst_path, forced=None):
    """Merge mcp/*.json into dst_path under mcpServers.

    Each fragment must contain an ``mcpServers`` dict keyed by server name.
    When a server name already exists in the destination it is skipped
    unless *forced* is truthy (non-empty set of paths).

    Return count of installed servers.
    """
    if not mcp_dir.is_dir():
        return 0

    if forced is None:
        forced = set()

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if dst_path.exists():
        base = json.loads(dst_path.read_text())
    else:
        base = {}

    base.setdefault("mcpServers", {})

    if forced:
        sources = [Path(p) for p in sorted(forced)]
    else:
        sources = sorted(mcp_dir.glob("*.json"))

    installed = 0
    for src in sources:
        if not forced:
            if src.name.startswith("_"):
                print(f"  skip   : {src.name} (internal)")
                continue

        if not src.is_file():
            print(f"  skip   : {src.name} (not found)")
            continue

        overlay = json.loads(src.read_text())
        overlay_servers = overlay.get("mcpServers", {})
        if not overlay_servers:
            print(f"  skip   : {src.name} (no mcpServers key)")
            continue

        is_forced = bool(forced)

        for server_name, server_config in overlay_servers.items():
            if server_name in base["mcpServers"] and not is_forced:
                print(
                    f"  skip   : {src.name} "
                    f"({server_name} already exists)"
                )
                continue
            base["mcpServers"][server_name] = server_config
            tag = "force" if is_forced else "install"
            print(f"  {tag}: {src.name} ({server_name})")
            installed += 1

    if installed > 0:
        dst_path.write_text(
            json.dumps(base, indent=2, ensure_ascii=False) + "\n"
        )

    return installed


def _revert_mcp(mcp_dir, dst_path, forced=None):
    """Remove mcpServers entries that were installed from mcp/*.json.

    Return count of removed servers.
    """
    if not mcp_dir.is_dir():
        return 0

    if not dst_path.exists():
        print(f"Config file not found: {dst_path}")
        return 0

    base = json.loads(dst_path.read_text())

    if "mcpServers" not in base:
        return 0

    if forced is not None:
        sources = [Path(p) for p in sorted(forced)]
        sources = [s for s in sources if s.suffix == ".json"]
    else:
        sources = sorted(mcp_dir.glob("*.json"))
        sources = [s for s in sources if not s.name.startswith("_")]

    reverted = 0
    for src in sources:
        if not src.is_file():
            continue
        overlay = json.loads(src.read_text())
        overlay_servers = overlay.get("mcpServers", {})
        if not overlay_servers:
            continue

        for server_name in overlay_servers:
            if server_name in base["mcpServers"]:
                del base["mcpServers"][server_name]
                print(f"  revert : {src.name} ({server_name})")
                reverted += 1
            else:
                print(f"  skip   : {src.name} "
                      f"({server_name}, not found)")

    if reverted > 0:
        if not base["mcpServers"]:
            del base["mcpServers"]
        dst_path.write_text(
            json.dumps(base, indent=2, ensure_ascii=False) + "\n"
        )

    return reverted


# ── hooks ──────────────────────────────────────────────────────────────


def install_hooks(hooks_dir, settings_path, hooks_dst, forced=None):
    """Install hooks: merge JSON into settings.json, symlink scripts to hooks_dst.

    When forced is non-empty (set of JSON file paths), only those hooks are
    processed with force=True.

    Return (json_installed, scripts_installed).
    """
    if not hooks_dir.is_dir():
        return 0, 0

    if forced is None:
        forced = set()

    # --- JSON → settings.json ---
    json_installed = 0

    if settings_path.exists():
        base = json.loads(settings_path.read_text())
    else:
        base = {}

    if forced:
        json_sources = [Path(p) for p in sorted(forced)]
        json_sources = [s for s in json_sources if s.suffix == ".json"]
    else:
        json_sources = sorted(hooks_dir.glob("*.json"))
        json_sources = [s for s in json_sources if not s.name.startswith("_")]

    for src in json_sources:
        if not src.is_file():
            print(f"  skip   : {src.name} (hooks, not found)")
            continue
        overlay = json.loads(src.read_text())
        is_forced = bool(forced)

        before = json.dumps(base, sort_keys=True, ensure_ascii=False)
        _deep_merge(base, overlay, force=is_forced)
        after = json.dumps(base, sort_keys=True, ensure_ascii=False)

        if before != after:
            tag = "force" if is_forced else "install"
            print(f"  {tag}: {src.name} (hooks)")
            json_installed += 1
        else:
            print(f"  skip   : {src.name} (hooks, up to date)")

    if json_installed > 0:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(base, indent=2, ensure_ascii=False) + "\n"
        )

    # --- Scripts → symlink to hooks_dst ---
    scripts_installed = 0
    hooks_dst.mkdir(parents=True, exist_ok=True)

    if forced:
        script_sources = []
        for f_path in forced:
            name = Path(f_path).stem
            for script in hooks_dir.glob(f"{name}.*"):
                if script.suffix != ".json" and not script.name.startswith(
                    "_"
                ):
                    script_sources.append(script)
        script_sources = sorted(set(script_sources))
    else:
        script_sources = sorted(hooks_dir.glob("*"))
        script_sources = [
            s for s in script_sources if s.suffix != ".json"
            and not s.name.startswith("_") and not s.name.startswith(".")
        ]

    for src in script_sources:
        dst = hooks_dst / src.name
        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                print(f"  skip   : {dst.name} (hooks, correct)")
                continue
            print(f"  fix    : {dst.name} (hooks) -> {src}")
            dst.unlink()
        elif dst.exists():
            print(f"  skip   : {dst.name} (hooks, existing file)")
            continue
        else:
            print(f"  install: {dst.name} (hooks)")

        dst.symlink_to(src)
        scripts_installed += 1

    # Clean up broken symlinks (from deleted hook scripts)
    for dst in sorted(hooks_dst.iterdir()):
        if dst.is_symlink() and not dst.exists():
            print(f"  cleanup: {dst.name} (hooks, broken link)")
            dst.unlink()

    return json_installed, scripts_installed


def _revert_hooks(hooks_dir, settings_path, hooks_dst, forced=None):
    """Remove JSON keys from settings.json, remove script symlinks.

    When forced is non-empty, only revert the specified hooks.
    Return (json_reverted, scripts_removed).
    """
    json_reverted = 0
    scripts_removed = 0

    # --- JSON revert ---
    if hooks_dir.is_dir() and settings_path.exists():
        base = json.loads(settings_path.read_text())

        if forced is not None:
            json_sources = [Path(p) for p in sorted(forced)]
            json_sources = [s for s in json_sources if s.suffix == ".json"]
        else:
            json_sources = sorted(hooks_dir.glob("*.json"))
            json_sources = [
                s for s in json_sources if not s.name.startswith("_")
            ]

        for src in json_sources:
            if not src.is_file():
                continue
            overlay = json.loads(src.read_text())

            before = json.dumps(base, sort_keys=True, ensure_ascii=False)
            _deep_revert(base, overlay)
            after = json.dumps(base, sort_keys=True, ensure_ascii=False)

            if before != after:
                print(f"  revert : {src.name} (hooks)")
                json_reverted += 1
            else:
                print(f"  skip   : {src.name} (hooks, no match)")

        if json_reverted > 0:
            settings_path.write_text(
                json.dumps(base, indent=2, ensure_ascii=False) + "\n"
            )

    # --- Script revert ---
    if hooks_dst.is_dir():
        hook_names = None
        if forced is not None:
            hook_names = {Path(p).stem for p in forced}

        for f in sorted(hooks_dst.iterdir()):
            if f.is_symlink():
                target = os.readlink(f)
                if str(hooks_dir) in target:
                    if hook_names is not None and f.stem not in hook_names:
                        continue
                    print(f"  remove: {f.name} (hooks)")
                    f.unlink()
                    scripts_removed += 1
                else:
                    print(f"  skip  : {f.name} (hooks, elsewhere)")
            else:
                print(f"  skip  : {f.name} (hooks, file)")

    return json_reverted, scripts_removed


def _verify_settings(settings_dir, settings_path):
    """Verify merged settings.json contains all source keys with correct values.

    Return (passed, failed).
    """
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


def _deep_check(merged, key, source_value, path=None, _parent_key=None):
    """Recursively check merged[key] contains source_value.

    Return (passed, failed).
    permissions.allow and hook event arrays are checked as superset
    (all source entries must exist in merged).
    """
    if key == "ANTHROPIC_AUTH_TOKEN":
        return 0, 0

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
            dp, df = _deep_check(merged_val, k, v, path, _parent_key=key)
            p += dp
            f += df
        return p, f

    # List superset checks: all source entries must exist in merged
    if (
        isinstance(source_value, list) and isinstance(merged_val, list)
        and ((_parent_key == "permissions" and key == "allow")
             or _parent_key == "hooks")
    ):
        if _parent_key == "permissions":
            _to_check = set(source_value)
            _have = set(merged_val)
        else:
            _to_check = {json.dumps(e, sort_keys=True) for e in source_value}
            _have = {json.dumps(e, sort_keys=True) for e in merged_val}
        missing = _to_check - _have
        if missing:
            label = "entries" if _parent_key == "permissions" else "entries"
            print(f"  ✗ {path} (missing {label})")
            return 0, 1
        print(f"  ✓ {path}")
        return 1, 0

    if merged_val == source_value:
        print(f"  ✓ {path}")
        return 1, 0

    print(f"  ✗ {path} (mismatch)")
    return 0, 1


# ── commands validation ────────────────────────────────────────────────


def _validate(src_dir, dst_dir, glob_pattern="*.md"):
    """Validate symlinks: all source items must be correct in dst."""
    if not src_dir.is_dir():
        return 0, 0

    passed = 0
    failed = 0
    src_files = {
        f.name: f
        for f in src_dir.glob(glob_pattern) if not f.name.startswith(".")
    }
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


def _revert_items(src_dir, dst_dir, label=""):
    """Remove symlinks pointing to *src_dir* from *dst_dir*.

    Also removes broken symlinks.  Return count removed.
    """
    if not dst_dir.is_dir():
        return 0

    removed = 0
    tag = f" ({label})" if label else ""

    for f in sorted(dst_dir.iterdir()):
        if f.is_symlink():
            target = os.readlink(f)
            if str(src_dir) in target or not f.exists():
                print(f"  remove: {f.name}{tag}")
                f.unlink()
                removed += 1
            else:
                print(f"  skip  : {f.name}{tag} (elsewhere)")
        else:
            print(f"  skip  : {f.name}{tag} (file)")

    return removed


def _revert_commands(src_dir, dst_dir):
    """Remove command symlinks pointing to src_dir from dst_dir."""
    return _revert_items(src_dir, dst_dir)


def _revert_skills(src_dir, dst_dir):
    """Remove skill symlinks pointing to src_dir from dst_dir."""
    return _revert_items(src_dir, dst_dir, label="skills")


def _revert_agents(src_dir, dst_dir):
    """Remove agent symlinks pointing to src_dir from dst_dir."""
    return _revert_items(src_dir, dst_dir, label="agents")


def _run_test(
    src_dir, skills_dir, agents_dir, settings_dir, hooks_dir, mcp_dir
):
    root = Path("/tmp/my-claude")
    dst_dir = root / "commands"
    skills_dst = root / "skills"
    agents_dst = root / "agents"

    print(f"=== Install test ({dst_dir}) ===\n")

    installed = install_commands(src_dir, dst_dir)
    installed_sk = install_skills(skills_dir, skills_dst)
    installed_ag = install_agents(agents_dir, agents_dst)
    print(
        f"\nInstalled {installed} commands, {installed_sk} skills, "
        f"{installed_ag} agents.\n"
    )

    print("=== Validation (commands) ===")
    passed, failed = _validate(src_dir, dst_dir)
    print("\n=== Validation (skills) ===")
    sp, sf = _validate(skills_dir, skills_dst, glob_pattern="*")
    passed += sp
    failed += sf
    if agents_dir.is_dir():
        print("\n=== Validation (agents) ===")
        ap, af = _validate(agents_dir, agents_dst)
        passed += ap
        failed += af

    if settings_dir.is_dir():
        print("\n=== Settings install test ===")
        settings_path = root / "settings.json"
        installed_s = install_settings(settings_dir, settings_path)
        print(f"\n{installed_s} settings installed.\n")

        print("=== Settings verify ===")
        vp, vf = _verify_settings(settings_dir, settings_path)
        if vf > 0:
            failed += vf

        print("\n=== Settings partial revert test ===")
        # Install all, then revert only one specific file
        install_settings(settings_dir, settings_path)
        json_files = sorted(settings_dir.glob("*.json"))
        non_internal = [f for f in json_files if not f.name.startswith("_")]
        if non_internal:
            target = non_internal[0]
            reverted_s = _revert_settings(
                settings_dir, settings_path, {str(target)}
            )
            print(f"\nPartial revert of {target.name}: {reverted_s} reverted.")
            # Re-install for subsequent tests
            install_settings(settings_dir, settings_path)

        print("\n=== Settings revert test ===")
        reverted_s = _revert_settings(settings_dir, settings_path)
        print(f"\n{reverted_s} settings reverted.")

    if hooks_dir.is_dir():
        print("\n=== Hooks install test ===")
        settings_path = root / "settings.json"
        hooks_dst = root / "hooks"
        j, s = install_hooks(hooks_dir, settings_path, hooks_dst)
        print(f"\n{j} hook settings, {s} hook scripts installed.\n")

        print("=== Hooks verify ===")
        vp, vf = _verify_settings(hooks_dir, settings_path)
        if vf > 0:
            failed += vf

        if hooks_dst.is_dir():
            for f in sorted(hooks_dst.iterdir()):
                if f.is_symlink():
                    print(f"  ✓ {f.name}")
                else:
                    print(f"  ✗ {f.name} (not a symlink)")
                    failed += 1

        print("\n=== Hooks partial revert test ===")
        json_files = sorted(hooks_dir.glob("*.json"))
        non_internal = [f for f in json_files if not f.name.startswith("_")]
        if non_internal:
            target = non_internal[0]
            j, s = _revert_hooks(
                hooks_dir, settings_path, hooks_dst, {str(target)}
            )
            print(
                f"\nPartial revert of {target.name}: {j} hook setting, {s} script reverted."
            )
            # Re-install for subsequent tests
            install_hooks(hooks_dir, settings_path, hooks_dst)

        print("\n=== Hooks revert test ===")
        j, s = _revert_hooks(hooks_dir, settings_path, hooks_dst)
        print(f"\n{j} hook settings, {s} hook scripts reverted.")

    if mcp_dir.is_dir():
        mcp_path = root / ".claude.json"

        print("\n=== MCP install test ===")
        installed_m = install_mcp(mcp_dir, mcp_path)
        print(f"\n{installed_m} MCP servers installed.\n")

        print("=== MCP verify ===")
        if mcp_path.exists():
            merged = json.loads(mcp_path.read_text())
            servers = merged.get("mcpServers", {})
            for src in sorted(mcp_dir.glob("*.json")):
                if src.name.startswith("_"):
                    continue
                expected = json.loads(src.read_text())
                for sname, scfg in expected.get("mcpServers", {}).items():
                    if sname not in servers:
                        print(f"  ✗ {src.name} ({sname} missing)")
                        failed += 1
                        continue
                    actual = servers[sname]
                    if actual != scfg:
                        print(f"  ✗ {src.name} ({sname} mismatch)")
                        failed += 1
                    else:
                        print(f"  ✓ {src.name} ({sname})")
        else:
            print("  ✗ .claude.json missing")
            failed += 1

        print("\n=== MCP partial revert test ===")
        json_files = sorted(mcp_dir.glob("*.json"))
        non_internal = [f for f in json_files if not f.name.startswith("_")]
        if non_internal:
            target = non_internal[0]
            reverted_m = _revert_mcp(mcp_dir, mcp_path, {str(target)})
            print(f"\nPartial revert of {target.name}: {reverted_m} reverted.")
            # Re-install for subsequent tests
            install_mcp(mcp_dir, mcp_path)

        print("\n=== MCP revert test ===")
        reverted_m = _revert_mcp(mcp_dir, mcp_path)
        print(f"\n{reverted_m} MCP servers reverted.")

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
    parser.add_argument(
        "--settings",
        "-s",
        action="append",
        default=None,
        metavar="FILE",
        help="force-install a settings JSON file (repeatable)",
    )
    parser.add_argument(
        "--hooks",
        action="append",
        default=None,
        metavar="FILE",
        help="force-install a hook JSON file and its script (repeatable)",
    )
    parser.add_argument(
        "--mcp",
        action="append",
        default=None,
        metavar="FILE",
        help="force-install an MCP server JSON file (repeatable)",
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
    skills_dir = Path(__file__).resolve().parent / "skills"
    skills_dst = root / "skills"
    agents_dir = Path(__file__).resolve().parent / "agents"
    agents_dst = root / "agents"
    settings_dir = Path(__file__).resolve().parent / "settings"
    settings_path = root / "settings.json"
    hooks_dir = Path(__file__).resolve().parent / "hooks"
    hooks_dst = root / "hooks"
    mcp_dir = Path(__file__).resolve().parent / "mcp"
    mcp_path = Path.home() / ".claude.json"

    if args.test:
        _run_test(
            src_dir, skills_dir, agents_dir, settings_dir, hooks_dir, mcp_dir
        )
    elif args.revert:
        if not args.settings and not args.hooks and not args.mcp:
            # Full revert: everything
            removed = _revert_commands(src_dir, dst_dir)
            removed_s = _revert_skills(skills_dir, skills_dst)
            removed_a = _revert_agents(agents_dir, agents_dst)
            print(
                f"\nDone. {removed} commands, {removed_s} skills, "
                f"{removed_a} agents removed."
            )

            if settings_dir.is_dir():
                print("\n=== Settings ===")
                reverted_s = _revert_settings(settings_dir, settings_path)
                print(f"\nDone. {reverted_s} settings reverted.")

            if hooks_dir.is_dir():
                print("\n=== Hooks ===")
                j, s = _revert_hooks(hooks_dir, settings_path, hooks_dst)
                print(f"\nDone. {j} hook settings, {s} hook scripts reverted.")

            if mcp_dir.is_dir():
                print("\n=== MCP ===")
                reverted_m = _revert_mcp(mcp_dir, mcp_path)
                print(f"\nDone. {reverted_m} MCP servers reverted.")
        else:
            # Partial revert: only specified parts, skip commands
            if args.settings:
                print("\n=== Settings ===")
                reverted_s = _revert_settings(
                    settings_dir, settings_path, set(args.settings)
                )
                print(f"\nDone. {reverted_s} settings reverted.")

            if args.hooks:
                print("\n=== Hooks ===")
                j, s = _revert_hooks(
                    hooks_dir, settings_path, hooks_dst, set(args.hooks)
                )
                print(f"\nDone. {j} hook settings, {s} hook scripts reverted.")

            if args.mcp:
                print("\n=== MCP ===")
                reverted_m = _revert_mcp(mcp_dir, mcp_path, set(args.mcp))
                print(f"\nDone. {reverted_m} MCP servers reverted.")
    else:
        # resolve --settings paths to absolute paths for forced merge
        forced = set()
        if args.settings:
            for path_str in args.settings:
                p = Path(path_str).resolve()
                if not p.is_file():
                    print(f"Settings file not found: {p}", file=sys.stderr)
                    sys.exit(1)
                forced.add(str(p))

        # resolve --mcp paths to absolute paths for forced merge
        mcp_forced = set()
        if args.mcp:
            for path_str in args.mcp:
                p = Path(path_str).resolve()
                if not p.is_file():
                    print(f"MCP file not found: {p}", file=sys.stderr)
                    sys.exit(1)
                mcp_forced.add(str(p))

        installed = install_commands(src_dir, dst_dir)
        installed_s = install_skills(skills_dir, skills_dst)
        installed_a = install_agents(agents_dir, agents_dst)
        print(
            f"\nDone. {installed} commands, {installed_s} skills, "
            f"{installed_a} agents installed."
        )

        if settings_dir.is_dir():
            print("\n=== Settings ===")
            installed_s = install_settings(settings_dir, settings_path, forced)
            print(f"\nDone. {installed_s} settings installed.")

        if hooks_dir.is_dir():
            print("\n=== Hooks ===")
            j, s = install_hooks(
                hooks_dir, settings_path, hooks_dst, args.hooks
            )
            print(f"\nDone. {j} hook settings, {s} hook scripts installed.")

        if mcp_dir.is_dir():
            print("\n=== MCP ===")
            installed_m = install_mcp(mcp_dir, mcp_path, mcp_forced)
            print(f"\nDone. {installed_m} MCP servers installed.")


if __name__ == "__main__":
    main()
