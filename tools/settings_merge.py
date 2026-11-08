"""Make small, idempotent edits to ~/.claude/settings.json. Backs the file up first.

  python tools/settings_merge.py marketplace <name> github <owner/repo>
  python tools/settings_merge.py marketplace <name> git <url>
  python tools/settings_merge.py marketplace <name> directory <path>
  python tools/settings_merge.py remove-marketplace <name>
  python tools/settings_merge.py enable <plugin@marketplace>
  python tools/settings_merge.py disable <plugin@marketplace>
  python tools/settings_merge.py base            # merge settings.base.json (only sets keys that are missing)
  python tools/settings_merge.py show

Restart the Claude app (or start a new session) afterwards for plugin changes to load.
"""
import json
import shutil
import sys
import time
from pathlib import Path

SETTINGS = Path.home() / ".claude" / "settings.json"
BASE = Path(__file__).resolve().parent.parent / "settings.base.json"


def load():
    if SETTINGS.exists():
        return json.loads(SETTINGS.read_text())
    return {}


def save(data):
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    if SETTINGS.exists():
        backups = SETTINGS.parent / "backups"
        backups.mkdir(exist_ok=True)
        shutil.copy2(SETTINGS, backups / f"settings.json.{time.strftime('%Y%m%d-%H%M%S')}")
    SETTINGS.write_text(json.dumps(data, indent=2) + "\n")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    data = load()
    before = json.dumps(data, sort_keys=True)

    if cmd == "marketplace":
        name, kind, where = args
        if kind == "github":
            source = {"source": "github", "repo": where}
        elif kind == "git":
            source = {"source": "git", "url": where}
        elif kind == "directory":
            source = {"source": "directory", "path": str(Path(where).expanduser().resolve())}
        else:
            raise SystemExit(f"unknown source kind {kind}")
        data.setdefault("extraKnownMarketplaces", {})[name] = {"source": source}
    elif cmd == "remove-marketplace":
        data.get("extraKnownMarketplaces", {}).pop(args[0], None)
        for key in [k for k in data.get("enabledPlugins", {}) if k.endswith("@" + args[0])]:
            del data["enabledPlugins"][key]
    elif cmd in ("enable", "disable"):
        plugin = args[0]
        if "@" not in plugin:
            raise SystemExit("use plugin@marketplace")
        if cmd == "enable":
            market = plugin.split("@", 1)[1]
            if market not in data.get("extraKnownMarketplaces", {}) and market != "claude-plugins-official":
                raise SystemExit(f"marketplace {market} isn't registered yet; add it first")
            data.setdefault("enabledPlugins", {})[plugin] = True
        else:
            data.get("enabledPlugins", {}).pop(plugin, None)
    elif cmd == "base":
        base = json.loads(BASE.read_text())
        for key, value in base.items():
            if key.startswith("_"):
                continue
            data.setdefault(key, value)
    elif cmd == "show":
        print(json.dumps(data, indent=2))
        return 0
    else:
        print(__doc__)
        return 2

    if json.dumps(data, sort_keys=True) == before:
        print("no change")
    else:
        save(data)
        print(f"updated {SETTINGS}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
