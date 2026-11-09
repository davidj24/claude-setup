# claude-setup

This public repo describes a Claude workflow so any machine can be set up or synced by Claude.

- `components/*.yaml`: one file per piece (skill repo, plugin, tool, dotfile, scheduled task). Copy `_TEMPLATE.yaml` for new ones.
- `guides/`: how to build each private feature without access to its repo. `guides/reference/recaps.py` must stay identical to the copy in claude-skills.
- `dotfiles/`: config files that have no repo of their own (kanata, scheduled-task prompts). On Linux the live files are symlinks into here.
- `home/CLAUDE.md`: becomes `~/.claude/CLAUDE.md` on every machine.
- `tools/probe.py`, `tools/settings_merge.py`: stdlib-only helpers the skill runs.

Rules:
- This repo is public. No IDs, addresses, personal paths or machine records; those stay in private repos.
- Never commit secrets, tokens, `.credentials.json`, session data or model files. Components list secrets by path only.
- Code for a component lives in its own repo (claude-skills, claude-mods, voice-dictation, voice-reader); this repo only points at it.
- Keep component files accurate: if you change how something installs or what it costs, update its yaml in the same change.
