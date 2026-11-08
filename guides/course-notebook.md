# Build guide: course study notebook

**What you get:** each week, a Gemini notebook is kept complete with every required reading and lecture's slides, named by lecture so it sorts properly.

**Only worth building if** you take a course with a published schedule and study from a notebook. The original is specific to one class, so adapt everything below. It needs Claude in Chrome and a signed-in Google account.

Ask the user for: the notebook URL, where the course schedule lives, and which readings count as required.

## The procedure

1. **Work out what should be there.** Read the course schedule. Include required readings and slides for lectures already held; never optional readings.
2. **Read the notebook's source list** in a new tab. Filter in the page and return only names that don't match the naming pattern, plus the highest lecture number present.
3. **Add web readings by link,** all at once through Add sources → Websites. If the connection drops, check the list before retrying, or you'll create duplicates. Remove any failed sources afterward.
4. **Hand over the rest.** Scripted uploads don't work in Gemini, so download slides and course-hosted PDFs into one folder for the user to drag in. Paywalled sites, Google Docs `/pub` links, Google Slides links and course-site files usually can't be added by URL.
5. **Rename every new source:** `L<NN> - <Author> - <Short title>`, or `L<NN> - Slides - <Lecture title>`. Use two-digit lecture numbers. Renaming needs real key presses, because setting the field by script doesn't save.
6. **Report** what was added, what's waiting to be dragged in, and what failed. If you've built the brief, put the drag-in list under FYI.

## Done when

A second run adds nothing new and every source follows the naming pattern.
