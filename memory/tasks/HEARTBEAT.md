## Heartbeat Task Check

Every 30 minutes, check for:

1. **Overdue tasks** - pending/in-progress past deadline
2. **Blocked tasks** - stuck > 24 hours
3. **High priority** - pending > 48 hours

Alert user if any found.

## Task Commands

```bash
# Add task
task add "Description" [priority:low|medium|high|critical]

# List all active
task list

# Update progress
task progress <id-prefix> <0-100>

# Mark complete
task done <id-prefix>

# Quick alias
alias task="bash /root/.openclaw/workspace/memory/tasks/task.sh"
```

## Current Status

Run `task list` to see active tasks.
