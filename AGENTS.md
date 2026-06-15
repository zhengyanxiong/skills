# Repository Guidelines

## Supported Agents

Skills can be installed into any of the following agent config directories:

| Agent ID | Config Directory |
|----------|-----------------|
| `codex` | `~/.codex/skills` |
| `claude-code` | `~/.claude/skills` |
| `kimi` | `~/.kimi/skills` |
| `hermes` | `~/.hermes/skills` |
| `minimax` | `~/.minimax/skills` |

To install for a specific agent:

```bash
python3 skills.py install --agent codex
python3 skills.py install --agent claude-code
```

Override the config directory with `--agent-dir`:

```bash
python3 skills.py install --agent-dir codex=/custom/path
```

## Install Skills From Remote Sources

```bash
# GitHub shorthand (owner/repo)
python3 skills.py add owner/repo

# Specific path inside a repo
python3 skills.py add owner/repo/path/to/skills

# Full git URL
python3 skills.py add https://github.com/owner/repo.git

# Limit to specific agents
python3 skills.py add owner/repo --agent claude-code --agent hermes
```

The `add` command clones the remote repository, discovers `SKILL.md` files, copies them to the local repo, creates symlinks to agent directories, and updates `skills.manifest.json` for tracking.

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all local skills |
| `add <source>` | Install skills from a remote GitHub repo or git URL |
| `status` | Show symlink install status per agent |
| `install` | Create symlinks for all local skills |
| `uninstall` | Remove skill symlinks |
| `doctor` | Validate local skills and manifest |
| `outdated` | Check for upstream updates |
| `sync` | Sync upstream source updates |
| `sources list` | List source manifest entries |
| `sources add` | Add source entry to manifest |
| `sources remove` | Remove source entry from manifest |

## Project Structure

Each skill lives in a top-level directory named with lowercase letters, digits, and hyphens.
Every skill must include `SKILL.md` with YAML frontmatter.

```
skills-repo/
├── skill-name/
│   ├── SKILL.md          # Required: skill description and instructions
│   ├── references/       # Optional: long-form docs
│   ├── scripts/          # Optional: executable helpers
│   └── data/             # Optional: lookup tables
├── skills.py             # Core CLI tool
├── skills.manifest.json  # Source tracking manifest
├── skills                # Linux/macOS entry point
└── skills.ps1            # Windows entry point
```

## Build & Test

No compile step. Run validation:

```bash
python3 skills.py doctor           # Validate all skills
python3 skills.py install --dry-run  # Preview symlink changes
python3 -m pytest tests/           # Run tests
```

## Coding Style

- Skill directory names match `name` frontmatter value
- `SKILL.md` under 500 lines; move details to `references/`
- Shell scripts: `set -euo pipefail`
- Python: type-annotated, stdlib only (no external deps)

## Commit Guidelines

Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`.
Keep commits scoped to one skill or tool change.
