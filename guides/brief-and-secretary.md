# Build guide: daily brief and secretary

**What you get:** type `brief` once a day and a separate session reads your inboxes, calendar and task sources, then shows one short brief. You can ask it follow-up questions.

**Needs first:** the task sync from [task-sync.md](task-sync.md), which does the actual reading and writing.

## How it's put together

There are two sessions, because each one should stay small:

| Session | Job | Why it's separate |
|---|---|---|
| **Secretary** (launcher): one pinned session you reuse daily | Only starts the day's brief | It does almost nothing, so its context stays tiny |
| **Brief – <date>**: a new side session each day | Reads sources, updates tasks, shows the brief, answers follow-ups | It starts fresh, so yesterday's reading isn't paid for again |

Run the side session on a mid-tier model such as Sonnet. The work is mostly reading and sorting.

## What to build

Create the skill `~/.claude/skills/brief/SKILL.md`:

- **Trigger:** the user types `brief`, optionally followed by notes, such as `brief: called the recruiter, dropped the Acme test`.
- **Behavior:** call `start_session` (load it with ToolSearch if deferred) with `initiation: "user_asked"`, `context: "fresh"`, `use_worktree: false`, a mid-tier model, the title `Brief – <Mon D>`, and the prompt below with `<notes>` replaced by what the user typed after "brief", word for word, or `none`.
- **Launcher stays silent:** it writes nothing in its own chat, including when the side session finishes.

```
Run the daily sync. Don't ask questions while it runs; report problems in the brief.

Notes from the user on what they finished: <notes>

Work silently: no progress updates between steps. Write chat text only for a problem the user must act on, and for the final brief.

1. If the skills folder is a git repo, pull it (ignore failures).
2. Invoke the task-sync skill and follow it exactly.
3. If a browser source isn't available or shows a sign-in page, skip it and list it under "Source problems". Never type passwords or sign in.
4. Never send, post or reply to anything on the user's behalf. Only read sources and write to the task database, the state page and allowed calendar events.
5. Your final message is the brief itself, in the format the skill gives. For follow-up questions, answer from what you already read before fetching more.
```

## Using it well

- **Don't message yesterday's brief session.** Once a session has been idle past its cache lifetime, one short message reprocesses its whole context at the full rate. Put late updates in tomorrow's `brief: ...` notes instead.
- **Nothing here is scheduled.** The brief runs when you ask, so a machine that's asleep can't miss it. Scheduling is an easy add if you want it.

## Done when

Typing `brief` starts a side session, the launcher chat stays empty, and the side session ends with the brief.
