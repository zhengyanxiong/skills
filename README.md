# Skills Repository

Central repository for reusable Agent Skills and a small CLI that installs them into supported agent runtimes with symlinks.

The repository is the source of truth. Agent-specific skill directories should contain links back to this checkout so updates here are immediately visible in Codex, Claude Code, OpenCode, Kimi, Hermes, Minimax, and other compatible tools.

## What Is In This Repo

- `*/SKILL.md`: one top-level directory per skill.
- `references/`, `scripts/`, `assets/`, `data/`: optional support files loaded by individual skills.
- `skills`: executable wrapper for the Python CLI.
- `skills.ps1`: PowerShell wrapper for Windows.
- `skills.py`: CLI implementation.
- `skills.manifest.json`: metadata for each skill, including purpose and upstream source.
- `tests/`: unit and integration tests for the CLI.

## CLI Quick Start

List local skills:

```bash
./skills list
```

On Windows PowerShell, use:

```powershell
.\skills.ps1 list
```

Check whether skills are linked into agent global directories:

```bash
./skills status
./skills status --agent codex
```

Install all skills into all known agents:

```bash
./skills install --agent all
```

Install one skill into one agent:

```bash
./skills install --agent codex --skill using-superpowers
```

Remove managed symlinks:

```bash
./skills uninstall --agent codex --skill using-superpowers
```

## Source Tracking

Each skill has metadata in `skills.manifest.json`:

```json
{
  "description": "What this skill is for.",
  "source": {
    "type": "git",
    "repo": "https://github.com/obra/superpowers.git",
    "ref": "main",
    "path": "skills/using-superpowers",
    "last_commit": "..."
  }
}
```

Use `type: local` when the current repository is the source of truth.

Manage source entries:

```bash
./skills sources list
./skills sources add frontend-design --repo https://github.com/anthropics/skills.git --path skills/frontend-design --ref main
./skills sources remove frontend-design
```

## Update Checks And Sync

Check upstream status:

```bash
./skills outdated
./skills outdated using-superpowers
```

For Git-backed skills, update detection is path-aware. The CLI checks the latest commit that touched the configured `source.path`, not just the repository HEAD.

Sync one skill from upstream:

```bash
./skills sync using-superpowers
```

Sync all tracked skills:

```bash
./skills sync --all
```

`sync` refuses to overwrite dirty local skill directories. Commit or stash local edits first.

## Health Checks

Run structural validation:

```bash
./skills doctor
```

This checks that every skill has `SKILL.md`, frontmatter `name` matches the directory name, and manifest entries point to local skills.

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

## Known Agent Directories

The CLI currently knows these global skill locations:

- Codex: `~/.codex/skills`
- Claude Code: `~/.claude/skills`
- OpenCode: `~/.config/opencode/skills`
- Kimi: `~/.kimi/skills`
- Hermes: `~/.hermes/skills`
- Minimax: `~/.minimax/skills`

If a target path already contains a real directory or a symlink to another location, install reports `conflict` and leaves it untouched.

## Development Notes

Skill directories and `name` frontmatter values should match exactly. Use lowercase hyphenated names. Keep `SKILL.md` focused; move long references, scripts, and templates into supporting subdirectories.

Before committing CLI changes, run:

```bash
python3 -m unittest discover -s tests -v
./skills doctor
```
