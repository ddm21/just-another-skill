# /init-memory — Initialize Memory for This Project

Your job is to set up the memory system for the current project from scratch.

---

## What to do

### Step 1 — Detect project context silently

Look at the current working directory:
- Folder name
- Any files that reveal what this is (package.json, README, n8n exports, etc.)
- Type of work: app / automation / research / business ops / other

Do this silently. Don't report it yet.

### Step 2 — Ask two questions only

Ask:
1. "What is this project about?" (one line is fine)
2. "Any rules or constraints I should always follow here?" (say 'no' to skip)

### Step 3 — Create the files

**`CLAUDE.md` in the project root:**

```
# Claude Instructions — [project name]

## Memory system

On every session start:
1. Read all files in `.memory/` silently
2. Use that context to understand the project without me re-explaining

Files:
- `.memory/context.md` — current project state
- `.memory/session-log.md` — last 20 sessions
- `.memory/ongoing.md` — unfinished tasks
- `.memory/decisions.md` — key decisions

Acknowledge context in one line max on session start. Don't recap unless asked.
If no memory found, say: "No memory yet. Starting fresh."
If we did meaningful work and I haven't run /log-memory, remind me once. Just once.

## Commands
- `/init-memory` — initialize memory for a new project (run once)
- `/log-memory` — save current session to memory

---

## About this project
[filled from user input]

## Rules / constraints
[filled from user input — omit section entirely if user had none]
```

**`.memory/context.md`:**

```
# Project: [project name]

## What this is
[from user input]

## Current state
Just initialized. No sessions logged yet.

## Active focus
Not set yet.

## Next action
Not set yet.

## Tools / stack
[detect from project folder if possible, else leave blank]
```

**`.memory/session-log.md`:**

```
# Session Log
[Sessions will appear here, newest first. Max 20 entries.]
```

**`.memory/ongoing.md`:**

```
# Ongoing Tasks
[Unfinished tasks will appear here]
```

**`.memory/decisions.md`:**

```
# Decisions
[Key decisions will appear here]
```

### Step 4 — Confirm

Say: "Memory initialized for [project name]. Run /log-memory anytime to save a session."

Nothing else.
