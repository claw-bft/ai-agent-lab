# Task Tracking System

**Purpose:** Long-term task tracking with progress monitoring for Kimi Claw.

## Architecture

**Storage:** File-based system in `memory/tasks/` with JSONL format for append-only logging.
**Interface:** CLI commands + automatic heartbeat checks.
**Sync:** Updates to USER.md on session end.

## Directory Structure

```
memory/
├── tasks/
│   ├── active.jsonl       # Current tasks
│   ├── completed.jsonl    # Finished tasks
│   ├── archive/           # Monthly archives
│   │   └── 2026-02.jsonl
│   └── index.md           # Quick reference
├── SOUL.md
└── USER.md
```

## Task Schema

```json
{
  "id": "uuid",
  "title": "Task description",
  "status": "pending|in-progress|blocked|completed|cancelled",
  "priority": "critical|high|medium|low",
  "created": "2026-02-25T21:41:00+08:00",
  "updated": "2026-02-25T21:41:00+08:00",
  "deadline": null,
  "source": "user|heartbeat|self",
  "progress": 0,
  "notes": [],
  "tags": []
}
```

## Commands

| Command | Action |
|---------|--------|
| `task add "title"` | Create new task |
| `task list` | Show active tasks |
| `task done <id>` | Mark complete |
| `task progress <id> <n>` | Update progress % |
| `task block <id> "reason"` | Mark blocked |
| `task archive` | Move completed to archive |

## Heartbeat Integration

Every 30min, check:
1. Tasks nearing deadline
2. Blocked tasks >24h
3. High priority pending >48h

Alert user if any found.
