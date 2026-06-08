# Skills CLI Design

## Goal

Build a unified CLI for managing this repository's agent skills. The CLI should install local skills into global agent skill directories using symlinks, track each skill's upstream GitHub source, detect whether upstream updates exist, and sync updates back into this repository for review.

## Scope

The first implementation should support Codex, Claude Code, Kimi, Hermes, and Minimax. Existing shell and PowerShell scripts can remain as compatibility wrappers, but new behavior should live in a Python CLI so path handling, JSON metadata, Git calls, and cross-platform behavior stay maintainable.

## Commands

Core commands:

```bash
skills list
skills status
skills status --agent codex
skills install --agent all
skills install --agent codex --skill frontend-design
skills uninstall --agent kimi --skill frontend-design
skills sources list
skills sources add frontend-design --repo URL --path PATH --ref main
skills sources remove frontend-design
skills outdated
skills sync frontend-design
skills sync --all
skills doctor
```

`status` must be offline and fast by default. It checks whether each local skill is linked into each agent directory. It should not contact GitHub unless explicitly requested with a later option such as `--check-updates`.

`outdated` checks network-backed upstream status. `sync` applies upstream changes into this repository. `doctor` performs full local and remote health checks.

## Agent Installation Model

Each skill is a top-level directory containing `SKILL.md`. Installing means creating symlinks from an agent's global skill directory to this repository:

```text
~/.codex/skills/frontend-design -> /repo/frontend-design
~/.claude/skills/frontend-design -> /repo/frontend-design
```

Agent directories should be defined in a registry:

```json
{
  "codex": "~/.codex/skills",
  "claude-code": "~/.claude/skills",
  "kimi": "~/.kimi/skills",
  "hermes": "~/.hermes/skills",
  "minimax": "~/.minimax/skills"
}
```

The CLI should create missing skill parent directories when installing. It must not overwrite real files or directories. If a target exists and is not the expected symlink, report `conflict`.

## Source Manifest

Add a root-level manifest:

```text
skills.manifest.json
```

Recommended structure:

```json
{
  "skills": {
    "frontend-design": {
      "source": {
        "type": "git",
        "repo": "https://github.com/user/agent-skills.git",
        "ref": "main",
        "path": "skills/frontend-design",
        "last_commit": "abc1234",
        "last_checked_at": "2026-06-08T10:30:00Z"
      }
    }
  }
}
```

The local skill name is the manifest key. The upstream `path` may point to a subdirectory inside a larger GitHub repository. Local names and upstream directory names do not need to match.

`last_commit` should record the last upstream commit that changed the configured `path`, not necessarily the repository branch HEAD.

## Upstream Update Detection

For each tracked skill, `outdated` should fetch the source repository and inspect the latest commit affecting the configured path:

```bash
git log -1 <ref> -- <path>
```

This avoids false positives when the upstream repository changes outside the skill directory.

Statuses:

```text
current            last_commit matches latest path commit
update-available   latest path commit differs from last_commit
local-only         no source entry exists
source-missing     source path does not exist upstream
source-invalid     repo, ref, or path cannot be accessed
dirty-local        local skill has uncommitted changes
```

The CLI should cache source repositories under `.cache/sources/` and use sparse checkout where practical:

```bash
git clone --filter=blob:none --sparse <repo> .cache/sources/<stable-id>
git -C .cache/sources/<stable-id> sparse-checkout set <path>
```

Multiple skills from the same repository should share the same cached clone.

## Sync Flow

`skills sync <skill>` should:

1. Read `skills.manifest.json`.
2. Resolve the source repo, ref, and path.
3. Fetch the cached source repository.
4. Validate that the upstream path contains `SKILL.md`.
5. Check that the local skill directory has no uncommitted changes.
6. Copy the upstream path into the local skill directory.
7. Update `last_commit` and `last_checked_at`.
8. Leave the resulting repository diff for review and commit.

The command must not silently overwrite local edits. If local files are dirty, it should stop with `dirty-local` unless a future explicit option such as `--force` is added.

## Status and Doctor Checks

`skills status` should report local installation state:

```text
linked      target is a symlink pointing to this repository
missing     target skill is not installed for that agent
conflict    target exists but is not the expected symlink
broken      target is a symlink whose destination does not exist
unknown     agent directory cannot be resolved
```

`skills doctor` should validate:

- every local skill contains `SKILL.md`
- `SKILL.md` frontmatter `name` matches the directory name
- manifest entries refer to existing local skills
- source repo, ref, and path are reachable
- upstream source path contains `SKILL.md`
- installed symlinks point to the current repository
- broken and conflicting links are reported clearly

## Error Handling

Errors should be actionable. For example:

```text
error: claude-code/frontend-design exists as a real directory; expected symlink
hint: move or remove ~/.claude/skills/frontend-design, then rerun install
```

Network-backed commands should distinguish authentication errors, missing repositories, missing refs, missing paths, and invalid skill directories.

## Testing Strategy

Use Python unit tests for path resolution, manifest parsing, source status classification, and symlink conflict detection. Integration tests can create temporary repositories and temporary agent directories to verify install, status, outdated, and sync behavior without touching real user config directories.

The initial acceptance checks should cover:

- install creates expected symlinks
- status identifies linked, missing, conflict, and broken states
- manifest supports GitHub subdirectory sources
- outdated checks the latest commit for the configured path only
- sync refuses dirty local skill directories
