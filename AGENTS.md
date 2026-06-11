# Repository Guidelines

## Project Structure & Module Organization

This repository stores reusable agent skills. Each skill lives in a top-level directory named with lowercase letters, digits, and hyphens, for example `skill-authoring-guide/` or `ui-ux-pro-max/`. Every skill must include `SKILL.md` with YAML frontmatter. Optional supporting files belong in `references/` for long-form docs, `scripts/` for executable helpers, `assets/` for reusable resources, and `data/` for structured lookup tables. Root-level `link-skills.sh` and `link-skills.ps1` install these skills into supported agent config directories.

## Build, Test, and Development Commands

- `./link-skills.sh status`: show detected agents and current symlink state on macOS, Linux, WSL, or Git Bash.
- `./link-skills.sh install --dry-run`: preview links that would be created without changing files.
- `./link-skills.sh install --agents codex-cli --skills skill-authoring-guide`: link one skill to one agent.
- `./link-skills.sh uninstall --dry-run`: preview symlink removal.
- `./link-skills.ps1 status`: PowerShell equivalent for Windows.

There is no compile step. Validation is mostly structural: ensure each skill has `SKILL.md`, valid frontmatter, and any referenced files actually exist.

## Coding Style & Naming Conventions

Skill directory names and `name` frontmatter values must match exactly and use lowercase hyphenated names. Keep `SKILL.md` focused and under 500 lines; move detailed guidance into `references/`. Prefer Markdown headings, concise imperative instructions, and concrete examples. Shell scripts use Bash with `set -euo pipefail`; PowerShell scripts use explicit functions and clear parameter names.

## Testing Guidelines

New or changed skills should include `evals.json` with 2-3 representative activation tests and `assertions.json` with measurable quality checks. For script changes, run the relevant status and dry-run commands before committing, for example `./link-skills.sh status` and `./link-skills.sh install --dry-run`.

## Commit & Pull Request Guidelines

Recent history uses short, direct commit subjects, sometimes in Chinese, such as `Add cross-platform skills symlink script` or `收集了两个前端skills`. Keep commits scoped to one skill or tool change. Pull requests should describe the changed skill or script, list validation commands run, and call out any new agent compatibility, symlink behavior, or required user setup. Include screenshots only for UI-focused assets or visual documentation.

## Agent-Specific Instructions

When editing skills, preserve the progressive-loading model: frontmatter describes when to activate, `SKILL.md` contains core workflow, and large references load only on demand. Do not duplicate generated skill copies inside agent config directories; update this repository as the source of truth and use the link scripts.
