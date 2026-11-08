# Build guide: setup audit (detox)

**What you get:** a periodic audit of your Claude setup that produces one checklist page, then changes only what you tick.

The original is a third-party skill (Ben AI's `/detox`), so it isn't reproduced here. Look for the original first. If you can't find it, build your own to this outline.

## Design

**The one rule: always ask.** Nothing changes until the user ticks it on the page or says so in chat. Saved ticks are data, so confirm in chat before the first change.

| Step | What | Changes anything? |
|---|---|---|
| Gather | A script collects local facts: skills, connectors, memory files, scheduled tasks, session history | No |
| Analyze | One pass each over interface, memory and context, skills, connectors, scheduled tasks | No |
| Publish | One checklist page of findings with reasons | No |
| Wait | The user ticks items | No |
| Apply | Make only the ticked changes, after confirming | Yes |

## Safe defaults

- Removed skills move to a dated backup folder and are never deleted.
- "Unused" means no use in 30 days.
- Say clearly which actions can't be undone, such as deleted chats.

## Running weekly

Schedule it to run through publishing only, then stop and share the link. A scheduled run has nobody present, so it must never apply changes.

## Done when

A run produces the page, and nothing on the machine has changed until something is ticked.
