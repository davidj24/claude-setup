# Build guide: recap sync across devices

**What you get:** the brief knows what you did in Claude on every machine. A script uploads one short line per session, using no AI and no tokens. The brief pays only to read the lines, about 75 tokens per session.

**Worth it when:** you use Claude on more than one machine. On a single machine, you only need the script's reading mode.

## Steps

1. Create **your own private** GitHub repo, such as `<you>/claude-recaps`, with one starting commit. It must be private because recaps describe your work.
2. Copy [reference/recaps.py](reference/recaps.py) to your task-sync skill's folder.
3. On every machine (Linux or Windows), run this once:

   ```bash
   python <skill folder>/recaps.py install https://github.com/<you>/claude-recaps.git
   ```

4. In the task sync, run this once per brief and use the output as described in [task-sync.md](task-sync.md):

   ```bash
   python <skill folder>/recaps.py <last-sync timestamp>
   ```

## How it works

- Claude sessions stay on the machine where they ran, as transcripts in `~/.claude/projects`. Sessions don't need to end to be counted.
- Every hour while a machine is on, a timer writes that machine's recent recaps to its own file in the repo, and commits only if something changed. One file per machine means they can't conflict.
- If a machine was off at the hour or offline, the upload happens next time it can.
- At brief time, the script pulls the repo, then combines other machines' files with fresh local sessions.

Each line is `<project> | <session title> | <final recap, or the end of the last reply>`. Lines from other machines start with `<machine>: `.

## Limits

- Work in the last hour before shutting a machine down reaches the repo only when it's next on. Use a `brief: ...` note for anything urgent.
- Work done without Claude isn't seen. Notes cover that too.

## Done when

A file named after each machine appears in your repo, and the reading command prints sessions from a different machine.
