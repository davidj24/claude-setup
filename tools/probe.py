"""Print a JSON snapshot of this machine for the setup-device skill.

Stdlib only, works on Linux, macOS and Windows. Run with: python tools/probe.py
"""
import json
import os
import platform
import shutil
import socket
import subprocess
from pathlib import Path

HOME = Path.home()
CLAUDE = HOME / ".claude"


def run(cmd, timeout=5):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def ram_gb():
    system = platform.system()
    try:
        if system == "Linux":
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal:"):
                    return round(int(line.split()[1]) / 1024 / 1024, 1)
        if system == "Darwin":
            v = run(["sysctl", "-n", "hw.memsize"])
            return round(int(v) / 1024**3, 1) if v else None
        if system == "Windows":
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MS()
            m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.ullTotalPhys / 1024**3, 1)
    except Exception:
        pass
    return None


def gpu():
    names = run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
    if names:
        return {"vendor": "nvidia", "cuda": True, "devices": names.splitlines()}
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        return {"vendor": "apple", "cuda": False, "devices": ["Apple Silicon"]}
    if platform.system() == "Linux":
        lspci = run(["lspci"]) or ""
        vga = [l for l in lspci.splitlines() if "VGA" in l or "3D" in l]
        return {"vendor": "other", "cuda": False, "devices": vga}
    return {"vendor": "unknown", "cuda": False, "devices": []}


def settings():
    p = CLAUDE / "settings.json"
    try:
        s = json.loads(p.read_text())
    except (OSError, ValueError):
        return {"exists": p.exists()}
    return {
        "exists": True,
        "enabledPlugins": s.get("enabledPlugins", {}),
        "marketplaces": {k: v.get("source", {}) for k, v in s.get("extraKnownMarketplaces", {}).items()},
    }


def git_remote(path):
    return run(["git", "-C", str(path), "remote", "get-url", "origin"])


def main():
    system = platform.system()
    tools = ["git", "gh", "curl", "python", "python3", "uv", "node", "winget", "brew",
             "kanata", "pw-record", "systemctl", "nvidia-smi", "claude"]
    total, _, free = shutil.disk_usage(HOME)
    claude_md = CLAUDE / "CLAUDE.md"
    info = {
        "hostname": socket.gethostname(),
        "os": system,
        "os_release": platform.platform(),
        "arch": platform.machine(),
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP"),
        "session_type": os.environ.get("XDG_SESSION_TYPE"),
        "ram_gb": ram_gb(),
        "disk_home_free_gb": round(free / 1024**3, 1),
        "disk_home_total_gb": round(total / 1024**3, 1),
        "gpu": gpu(),
        "tools": {t: bool(shutil.which(t) or (t == "kanata" and any(
            (HOME / "Kanata" / n).exists() for n in ("kanata", "kanata.exe")))) for t in tools},
        "claude_dir": {
            "exists": CLAUDE.exists(),
            "skills_repo_remote": git_remote(CLAUDE / "skills"),
            "skills_dir_exists": (CLAUDE / "skills").exists(),
            "claude_md": ("symlink -> " + os.readlink(claude_md)) if claude_md.is_symlink()
                         else ("file" if claude_md.exists() else None),
            "secrets_present": sorted(p.name for p in (CLAUDE / "secrets").glob("*")) if (CLAUDE / "secrets").exists() else [],
            "scheduled_tasks": sorted(p.name for p in (CLAUDE / "scheduled-tasks").glob("*")) if (CLAUDE / "scheduled-tasks").exists() else [],
            "settings": settings(),
        },
    }
    if system == "Linux":
        info["services"] = {s: run(["systemctl", "--user", "is-active", s]) for s in ("kanata", "voice-dictation")}
        info["pipewire"] = bool(run(["pw-cli", "info", "0"]))
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
