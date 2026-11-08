---
name: setup-device
description: Set up, update or audit this Claude workflow on the current machine from the claude-setup repo, asking which features to install and explaining how to build any the user can't download. Use when the user says "set up this device", "set up this computer", "sync my setup", "update my setup", "what's installed here", or after cloning claude-setup on a new machine. Also use when they want to add a new skill, mod or tool to the setup repo ("register this", "add this to my setup").
---

# setup-device

The repo root is the folder holding this skill's `.claude/` (call it `<repo>`). Everything the
workflow contains is in `<repo>/components/*.yaml` (ignore `_TEMPLATE.yaml`).

This repo is public and anyone may run it. Some components come from private repos. Never assume
the user owns them, and never ask anyone to sign in to get access to someone else's repo.

**Machine records** say what each machine chose. They're at `~/.claude/skills/machines/<hostname>.yaml`
if `~/.claude/skills/machines/` exists (a private synced folder); otherwise at
`~/.claude/setup-machines/<hostname>.yaml`, which stays on this machine. Never put them in `<repo>`.

Pick the mode from what the user said:

- **setup**: no machine record yet, or they asked to set up.
- **update**: the machine record exists and they asked to sync or update.
- **status**: they asked what's installed; do steps 1-2 and report, change nothing.
- **register**: they want to add something new to the setup. Go to "Registering a component".

## 0. Started from the bootstrap prompt

If the user pasted the bootstrap prompt from the README in a session outside the repo, the session
won't pick up this skill by itself, so keep following this file directly. Run every command against
`<repo>` (the clone path) rather than the session's folder. Plugin changes still need an app restart
at the end. Once setup is done, mention that later syncs can be run from a session opened in `<repo>`.

## 1. Pull, probe and check access

1. `git -C <repo> pull --ff-only` (if it fails because of local changes, show `git status` and ask).
2. Run `python <repo>/tools/probe.py` (use `python3` if `python` is missing). Read the JSON.
3. Read every component file and, if it exists, this machine's record.
4. For each component, run its `detect_installed` check for this OS (read-only) so you know what's
   already here, even if the machine record doesn't say so.
5. For each component with an `access:` block, test the repo once without prompting for a sign-in:
   `GIT_TERMINAL_PROMPT=0 git ls-remote <access.repo>` (PowerShell: set
   `$env:GIT_TERMINAL_PROMPT=0` and `$env:GCM_INTERACTIVE="never"` first). Success means **has
   access**. Any failure means **no access**. Don't treat it as an error, and don't try to sign in.

## 2. Decide per component

Work out, for each component, one of: **already installed**, **unsupported here**, **missing a
requirement**, **candidate**, or **build it yourself** (an `access:` block and no access).

For a **build it yourself** component, list each entry in `access.features` as its own candidate,
so the user picks features rather than a repo. A component's `requires` is also met when the user
has chosen to build the feature that replaces it.

Use `platforms`, `needs`, `requires` and the probe (OS, desktop, GPU/CUDA, free disk, RAM, tools).

In update mode, skip components the machine record lists as `installed` or `declined` unless the
component file changed since `last_run` (check with
`git -C <repo> log --since=<last_run> -- components/<id>.yaml`). Ask again about those, saying what changed.

## 3. Ask, in one go

Show one short table of every candidate, then ask with AskUserQuestion (multiSelect; up to 4
questions per call, so group them, and put `default: recommended` ones first marked
"(Recommended)"). For each candidate the option description must give, using this machine's
numbers:

- what it gives them (`summary`)
- the cost (`cost`, compared to the probe's free disk and RAM: "4.2 GB of your 40 GB free")
- if a `built_in_alternatives` entry matches this OS: what's built in and its `gap`, so they can see
  what they'd actually gain
- `worth_it_when` / `skip_when`, applied to this machine ("you have an NVIDIA GPU, so...")
- for build-it-yourself features: say it will be built from a guide and adapted to their tools,
  rather than downloaded

List the components that are unsupported or missing a requirement in plain text after the
questions, with the reason, so they know they were considered. Components with `default: optional`
go in that list too unless they clearly fit.

Some components are one person's preferences (keyboard layouts, for example). Say so when offering
them to someone who has no access to the private repos.

Don't ask about things they can't change from here (connectors on the account); just check them if
a component says to.

## 4. Install or build

For each chosen component, in `requires` order:

**If they have access, or it has no `access:` block:**

1. Follow `install` for this OS (`all` applies everywhere). Replace `<repo>` with the real path.
   Run `tools/settings_merge.py` for settings edits; never hand-edit settings.json.
2. For `files:` entries: on Linux/macOS symlink the target to the repo copy (back up an existing
   different file first as `<name>.bak-<date>`); on Windows copy it.

**If it's build it yourself:** skip `install`, `verify` and `secrets`. Read the feature's guide in
`<repo>/guides/`, ask the questions it lists, and offer two choices:

- **Build it now:** create the feature in this session, following the guide and adapted to the
  user's answers. Check it against the guide's "Done when".
- **Just explain it:** summarize what would need building and leave the guide's path.

**Either way:**

- Steps that need sudo, a password, a sign-in or a secret: stop, tell the user the exact command or
  click, and wait. Never ask them to paste a secret into chat; open the file for them instead.
- Run `verify`, if it applies. Note pass/fail.

Plugin changes need an app restart; say so once at the end, not per plugin.

## 5. Record the machine

Write the machine record:

```yaml
hostname: <hostname>
nickname: <ask once on first setup, e.g. "Linux desktop", "Windows laptop">
os: <os_release>
last_run: <YYYY-MM-DD>
hardware: {ram_gb: , disk_free_gb: , gpu: }
components:
  <id>: {status: installed | built | explained | declined | unsupported, note: "<why, one line>"}
```

If it's in `~/.claude/skills/machines/`, then commit and push it from `~/.claude/skills`
(`<hostname>: setup run <date>`). If the push fails (offline, auth), say so; the commit is kept
locally. Otherwise just leave the file there.

## 6. Report

A short checklist: installed and verified, installed but not verified, built from a guide, explained
only (with the guide's path), waiting on the user (with the exact step), declined, unsupported.
Mention restarting the app if plugins changed.

## Pushing changes made on this machine

In update mode, also check whether this machine has edits that other machines don't have yet, in
every checkout the user has push access to: `<repo>`, `~/.claude/skills`, and any component checkout
that exists here. Look at `git status` and unpushed commits (`git log @{u}..`). List them and offer
to commit and push (ask first; show the diff summary).

## Registering a component

When the user has added (or is adding) a new skill, mod, tool, config or scheduled task:

1. Find where it lives and whether it's in a git repo with a remote. If it isn't, offer to put it in
   one (an existing repo if it fits, a copy under `<repo>/dotfiles/` for config files, or a new repo).
2. Copy `components/_TEMPLATE.yaml` to `components/<id>.yaml` and fill it in. Research
   `built_in_alternatives` for each OS properly (what's built in, how to check it's on, what it
   lacks compared to this); this is the part they rely on when setting up other machines. Measure
   `cost` on this machine (`du -sh`, process RAM) instead of guessing.
3. If it comes from a private repo, add an `access:` block and write a guide in `guides/` that lets
   someone without access build it.
4. Before anything goes in `<repo>`, remember it's public: no IDs, addresses, tokens, personal paths
   or machine records. Those stay in private repos.
5. Add it to this machine's record as installed.
6. Show them the file, then commit and push on their OK.
