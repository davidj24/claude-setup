#!/usr/bin/env python3
"""Share short Claude session recaps between your machines. Uses no AI.

  python recaps.py <ISO timestamp>   Print sessions active since then, on every machine
  python recaps.py publish           Upload this machine's recent recaps (run hourly)
  python recaps.py install <url>     Set up the hourly upload, using your private repo

Each printed line is: <project> | <title> | <final recap, or the end of the last reply>
Sessions from other machines have "<machine>: " before the project.
Brief and launcher sessions are left out.
"""
import glob
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

MAX_LINES = 40
MAX_TEXT = 300
KEEP_DAYS = 14
SKIP_TITLES = ("brief", "secretary")
REPO = os.path.expanduser("~/.claude/recaps-repo")
TASK_NAME = "claude-recaps"
MACHINE = re.sub(r"[^a-z0-9-]+", "-", platform.node().lower()).strip("-") or "unknown"


def parse_time(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def clean(text):
    return " ".join(text.split()).replace("|", "/")


def git(*args):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    command = ["git", "-C", REPO, "-c", "user.name=claude-recaps",
               "-c", "user.email=claude-recaps@users.noreply.github.com", *args]
    try:
        return subprocess.run(command, env=env, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 1, "", "timed out")


def read_session(path, since):
    cwd = title = recap = last_text = updated = None
    with open(path, errors="ignore") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            cwd = entry.get("cwd") or cwd
            title = entry.get("customTitle") or entry.get("aiTitle") or title
            stamp = entry.get("timestamp")
            try:
                recent = bool(stamp) and parse_time(stamp) >= since
            except ValueError:
                recent = False
            if not recent or entry.get("type") != "assistant":
                continue
            updated = stamp
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text" and block.get("text", "").strip():
                    last_text = block["text"]
                elif block.get("type") == "tool_use" and block.get("name", "").endswith("wrap_up"):
                    recap = (block.get("input") or {}).get("recap") or recap
    if updated is None:
        return None
    return cwd, title, recap, last_text, updated


def local_sessions(since):
    """Return {session id: {"updated": ISO time, "line": text}} from this machine's transcripts."""
    root = os.path.expanduser("~/.claude/projects")
    home = os.path.expanduser("~")
    found = {}
    for path in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        if "subagents" in path.replace("\\", "/").split("/"):
            continue
        if os.path.getmtime(path) < since.timestamp():
            continue
        session = read_session(path, since)
        if not session:
            continue
        cwd, title, recap, last_text, updated = session
        if any(word in (title or "").lower() for word in SKIP_TITLES):
            continue
        summary = recap or (last_text or "")[-MAX_TEXT:]
        if not summary.strip():
            continue
        project = "scratch" if "scratch-workspaces" in (cwd or "") else (cwd or "?").replace(home, "~")
        session_id = os.path.splitext(os.path.basename(path))[0]
        found[session_id] = {
            "updated": updated,
            "line": f"{project} | {clean(title or 'untitled')} | {clean(summary)[:MAX_TEXT]}",
        }
    return found


def other_machine_sessions(since):
    found = {}
    for path in glob.glob(os.path.join(REPO, "*.jsonl")):
        machine = os.path.splitext(os.path.basename(path))[0]
        if machine == MACHINE:
            continue
        with open(path, errors="ignore") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                    if parse_time(entry["updated"]) < since:
                        continue
                    found[entry["session"]] = {
                        "updated": entry["updated"],
                        "line": f"{machine}: {entry['line']}",
                    }
                except (ValueError, KeyError, TypeError):
                    continue
    return found


def show(since_text):
    since = parse_time(since_text)
    sessions = {}
    if os.path.isdir(os.path.join(REPO, ".git")):
        git("pull", "--rebase", "--quiet")
        sessions.update(other_machine_sessions(since))
    sessions.update(local_sessions(since))
    ordered = sorted(sessions.values(), key=lambda item: parse_time(item["updated"]), reverse=True)
    for item in ordered[:MAX_LINES]:
        print(item["line"])


def publish():
    if not os.path.isdir(os.path.join(REPO, ".git")):
        sys.exit("recaps repo missing: run 'python recaps.py install' first")
    git("pull", "--rebase", "--quiet")
    since = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)
    sessions = local_sessions(since)
    name = f"{MACHINE}.jsonl"
    with open(os.path.join(REPO, name), "w", encoding="utf-8", newline="\n") as handle:
        for session_id in sorted(sessions):
            handle.write(json.dumps({"session": session_id, **sessions[session_id]}, sort_keys=True) + "\n")
    git("add", name)
    if git("diff", "--cached", "--quiet").returncode != 0:
        git("commit", "--quiet", "-m", f"Update {MACHINE}")
    if git("rev-list", "--count", "@{u}..HEAD").stdout.strip() != "0":
        if git("push", "--quiet").returncode != 0:
            git("pull", "--rebase", "--quiet")
            result = git("push", "--quiet")
            if result.returncode != 0:
                sys.exit(f"push failed, will retry next run: {result.stderr.strip()}")


def install_linux(script):
    folder = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f"{TASK_NAME}.service"), "w") as handle:
        handle.write("[Unit]\nDescription=Upload Claude session recaps\n\n"
                     f"[Service]\nType=oneshot\nExecStart=\"{sys.executable}\" \"{script}\" publish\n")
    with open(os.path.join(folder, f"{TASK_NAME}.timer"), "w") as handle:
        handle.write("[Unit]\nDescription=Upload Claude session recaps hourly\n\n"
                     "[Timer]\nOnCalendar=hourly\nPersistent=true\n\n"
                     "[Install]\nWantedBy=timers.target\n")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", f"{TASK_NAME}.timer"], check=True)


def install_windows(script):
    runner = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(runner):
        runner = sys.executable
    command = (
        f"$a = New-ScheduledTaskAction -Execute '{runner}' -Argument '\"{script}\" publish'; "
        "$t = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1); "
        "$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable; "
        f"Register-ScheduledTask -TaskName '{TASK_NAME}' -Action $a -Trigger $t -Settings $s -Force | Out-Null"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", command], check=True)


def install(remote):
    if not os.path.isdir(os.path.join(REPO, ".git")):
        if not remote:
            sys.exit("Give the address of your private recaps repo: python recaps.py install <url>")
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        subprocess.run(["git", "clone", "--quiet", remote, REPO], check=True, env=env)
    script = os.path.abspath(__file__)
    system = platform.system()
    if system == "Linux":
        install_linux(script)
    elif system == "Windows":
        install_windows(script)
    else:
        sys.exit(f"hourly upload isn't set up for {system} yet")
    publish()
    print(f"Hourly recap upload is on for {MACHINE}.")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "install":
        install(sys.argv[2])
    elif len(sys.argv) != 2:
        sys.exit(__doc__)
    elif sys.argv[1] == "publish":
        publish()
    elif sys.argv[1] == "install":
        install(None)
    else:
        show(sys.argv[1])


if __name__ == "__main__":
    main()
