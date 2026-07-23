#!/usr/bin/env python3
"""Notification hook: pop up desktop alerts on Stop and Notification events.

Read the hook event JSON from stdin and dispatch platform-specific
notifications.  Zero dependencies beyond Python stdlib and the system's
built-in notification tools.

SSH + tmux support: when running inside tmux (detected via $TMUX), use
``tmux display-message`` instead of desktop notifications.  Falls back
to terminal bell when neither path is available.
"""
import json
import os
import platform
import subprocess
import sys


def _project_name():
    return os.path.basename(os.getcwd())


def _in_tmux():
    return os.environ.get("TMUX", "") != ""


def _notify_tmux(message):
    """Show message in tmux status bar and via terminal bell."""
    # display-message shows briefly in the tmux status line
    subprocess.run(
        ["tmux", "display-message", message],
        capture_output=True,
        check=False,
    )


def _notify_desktop(title, message, sound=True):
    """Send a desktop notification.  Sound is best-effort."""

    system = platform.system()

    if system == "Darwin":
        script = f'display notification "{message}" with title "{title}"'
        if sound:
            script += ' sound name "Glass"'
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            check=False,
        )

    elif system == "Linux":
        args = ["notify-send", "--app-name=Claude Code", title, message]
        result = subprocess.run(args, capture_output=True, check=False)
        if result.returncode != 0:
            print("\a", end="", file=sys.stderr)

    else:
        print("\a", end="", file=sys.stderr)


def notify(title, message, sound=True):
    """Route to the best available notification channel."""

    # Always include terminal bell — it works through SSH
    print("\a", end="", file=sys.stderr)

    if _in_tmux():
        # tmux: show in status bar (visible in remote SSH sessions)
        _notify_tmux(f"{title}: {message}")
    else:
        _notify_desktop(title, message, sound=sound)


def main():
    event = json.load(sys.stdin)

    hook_event = event.get("hook_event", "")
    matcher = event.get("matcher", "")

    pn = _project_name()

    if hook_event == "Stop":
        notify(f"[{pn}]", "Done", sound=True)

    elif hook_event == "Notification":
        labels = {
            "permission_prompt": "Permission required",
            "idle_prompt": "Ready for input",
        }
        desc = labels.get(matcher, "Needs attention")
        notify(f"[{pn}]", desc, sound=False)


if __name__ == "__main__":
    main()
