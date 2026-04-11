# /log-memory — Save Session to Project Memory

Your job is to log what happened in this session into the project memory folder.

---

## Memory folder location

`.memory/` in the current project root.

If `.memory/` doesn't exist, say:
"Memory not initialized. Run /init-memory first."
Then stop.

---

## What to do

### Step 1 — Summarize this session yourself

Look at the full conversation. Figure out:
- What was the main thing we worked on?
- What got done?
- What did NOT get done or is still in progress?
- Any decisions made that future sessions should know?

### Step 2 — Ask once

Say: "Here's what I'll save — [2 line summary]. Confirm?"

Wait for yes before writing anything.

### Step 3 — Write updates

**`.memory/session-log.md`**

Read the existing file. Add the new entry at the very top, below the `# Session Log` heading.

**Retention: last 2 days only.** After adding the new entry, check all existing entries by date. Any entry older than 2 days from today gets compressed into the Archive Summary and deleted.

**Archive compression (required before deleting old entries):**
1. For each entry being removed, extract meaningful learnings — patterns, workarounds, color/layout decisions, tool quirks, bugs, techniques that worked/failed. Skip routine "generated X pages" details.
2. Append 1-2 line summaries to the `## Archive Summary` section at the bottom. Each line should be a standalone insight, not a session recap. Group by theme if multiple entries are compressed at once.
3. If no `## Archive Summary` section exists yet, create it at the very bottom.
4. Only then delete the old entries.

The Archive Summary should never exceed ~30 lines. If it gets close, consolidate redundant entries.

Entry format:
```
## [DATE] — [one line topic summary]
- Did: [what actually happened, 2-4 sentences]
- Status: [Done / In Progress / Blocked]
- Decisions: [key choices made, or "none"]
- Next: [exact next step, or "none"]
```

**`.memory/context.md`** — overwrite entirely:

```
# Project: [project name]

## What this is
[1-2 sentences on what this project is]

## Current state
[Where things stand right now]

## Active focus
[What we are actively working on]

## Next action
[The single most important next step]

## Tools / stack
[Tools, services, stack being used]
```

**`.memory/ongoing.md`** — add or update incomplete tasks. Remove tasks that are now done:

```
## [Task name]
- Started: [date]
- What: [brief description]
- Left off at: [specific detail to resume cold]
- Blocked by: [anything blocking — remove line if not blocked]
```

**`.memory/decisions.md`** — append only if a real decision was made this session. Skip entirely if nothing notable.

**Retention: last 2 days only** (same as session-log). After adding a new decision, check all entries by date. Any decision older than 2 days gets compressed into the `## Archive Summary` at the bottom as a 1-line bullet, then deleted. Group archived bullets by theme when consolidating.

Entry format:
```
## [Decision title] — [date]
- Decided: [what]
- Why: [reason]
- Rejected: [alternatives not picked, if any]
```

### Step 4 — Confirm

Tell me which files were updated. One line each. Done.
