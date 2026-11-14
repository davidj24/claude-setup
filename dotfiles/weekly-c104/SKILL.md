---
name: weekly-c104
description: Runs the c104-notebook skill every Thursday evening to add this week's DATA C104 readings and slides to the Gemini notebook.
---

This is a scheduled run with no user present. Work in ~/projects/Claude.

1. `git -C ~/.claude/skills pull --ff-only` (ignore failures).
2. Invoke the `c104-notebook` skill and follow it exactly, including step 6's `D104 Notebook uploads` hand-off row in Notion.
3. Use Claude in Chrome (David's signed-in Chrome). If Chrome or the extension isn't available, or Gemini or Google Slides shows a sign-in page, stop and say so in one line. Never type passwords or sign in.
4. Work silently: no progress updates. Don't touch anything outside the notebook, the upload folder (~/Downloads/C104 notebook uploads/) and that one Notion row.
5. Your final message is the skill's step 6 report, in at most 6 lines.