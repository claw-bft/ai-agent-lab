# CLAUDE.md

## Capabilities

- Smartest coding agent. Codes in any language, any library/framework. Uses context7 for latest info.
- Super agent: web search, web fetch for real-time information.
- Uses available skills via `find-skills` or creates new ones via `skill-creator`.
- Reduces tool calls for simple questions.

## Folder Structure

```
├── CLAUDE.md              # This file; workspace rules
├── .claude/               # Claude/Cursor configuration
│   └── skills/            # Skills (one folder per skill)
├── memory/                # Session-loaded context
│   ├── SOUL.md            # Identity, principles, capabilities
│   └── USER.md            # User preferences, context, history
├── wikis/                 # Knowledge base (Obsidian-style)
└── workspace/             # Workspace root
    ├── projects/          # Git repos and code projects
    ├── uploads/           # Uploaded files
    └── outputs/           # Generated outputs
```

## Conventions

- **memory/**: All UPPERCASE `.md` files in English. Keep under 1000 tokens; move detail to sub-files.
- **wikis/**: Local-first Markdown, bidirectional links. Refactoring requires user approval; log in `refactor-history.log`.

## Session End Protocol

Before session ends, update `memory/USER.md` and `memory/SOUL.md`:
- Memories and lessons up-to-date
- Important details preserved
- Outdated info cleaned

## Writing Style for `memory/` Files

Dense, telegraphic short sentences. No filler words. Comma/semicolon-joined facts. `**Bold**` paragraph titles instead of `##` headers. Prioritize information density.

## Notes

- All UPPERCASE `.md` files under `memory/` must be in English, except proper nouns.
- `SOUL.md` and `USER.md` loaded every session. Keep under 1000 tokens. Ruthless deduplication.
