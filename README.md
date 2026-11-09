# claude-setup

A Claude Code workflow, described so that Claude can set it up on any machine. Claude checks what the machine already has, shows what each feature would add and cost, asks which ones you want, and installs them.

**You don't need access to any private repos.** Features that live in a private repo come with a build guide. Claude can build them for you, adapted to your own tools, or just explain what would be involved.

## Set up a machine

1. Install git, Python 3 and the Claude desktop app, and sign in.
   - Windows: `winget install Git.Git Python.Python.3.13`
   - Linux (Debian/Ubuntu): `sudo apt install git curl python3 python-is-python3`
   - macOS: `xcode-select --install`
2. Start a session in any folder and paste:

   > Set up this device from the public GitHub repo davidj24/claude-setup. Clone it with git to `~/projects/Claude/claude-setup` (on Windows `$HOME\projects\Claude\claude-setup`); if it's already there, `git pull`. Then read `.claude/skills/setup-device/SKILL.md` in the clone and follow it in setup mode, in this session.

## What you can choose

| Feature | What it does | How you get it |
|---|---|---|
| Daily brief and secretary | Type `brief` for one summary of your inboxes, calendar and tasks | Private; [build guide](guides/brief-and-secretary.md) |
| Task sync | Keeps one task database current and ticks off what you've done | Private; [build guide](guides/task-sync.md) |
| Recap sync | Lets the brief see your Claude work on every device, at no token cost | Private; [build guide](guides/recap-sync.md) |
| Course notebook | Keeps a study notebook full of a course's readings | Private; [build guide](guides/course-notebook.md) |
| Setup audit (detox) | Audits your setup and changes only what you tick | Private; [build guide](guides/setup-audit.md) |
| Mods: blast-radius, cache-thermometer, dictation-cleanup, voice-picker | Interface additions for Claude | Public: [claude-mods](https://github.com/davidj24/claude-mods) |
| Read-aloud | Reads replies aloud | Public, third-party |
| Voice dictation | Local voice typing (NVIDIA GPU; Linux with GNOME, or Windows) | Public: [voice-dictation](https://github.com/davidj24/voice-dictation) |
| Voice reader | Local text-to-speech with pause and rewind (Linux, GNOME) | Public: [voice-reader](https://github.com/davidj24/voice-reader) |
| Keyboard layers, launcher, weekly audit, global instructions | Personal config files | Included in this repo |

Claude tests access to each private repo without asking anyone to sign in. If you have access, it installs from the repo. If you don't, it uses the guide.

## Keeping machines in sync

In a session in this folder, say **sync my setup**. It pulls the latest, asks about anything added since this machine's last run, and offers to push changes you've made.

To add a new piece, say **register this in my setup**. Claude writes its `components/<id>.yaml`, including what each OS already has built in and what it costs.

## What's in this repo

- `components/`: one file per feature, describing how to install it and what it costs
- `guides/`: how to build each private feature yourself
- `dotfiles/`, `home/`: config files with no repo of their own
- `tools/`: small helpers the setup skill runs

Records of what each machine chose are kept outside this repo, because they describe specific computers.
