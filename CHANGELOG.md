# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- English README translation
- GitHub Actions CI workflow refinements
- Doctor report badge in README
- Demo GIF for `skills add` workflow

## [1.0.0] - 2026-07-05

### 🎉 First Public Release

The Skills Repository is now publicly available under the MIT License. The core
asset is the cross-Agent CLI (`skills.py`) plus 60 curated `SKILL.md` files
covering AI Agent development, debugging, security, research, and engineering
workflow practices.

### Added

- **CLI tool `skills.py`** — Python stdlib-only CLI for managing AI Agent Skills across 6+ Agents
  - `add <source>` — Clone upstream repository and install matching SKILL.md files
  - `list` — Enumerate all local skills
  - `install --agent <a>` — Create symlinks to Agent skill directories
  - `uninstall` — Remove symlinks (does not delete source)
  - `status` — Show per-agent installation state
  - `doctor` — Validate SKILL.md + frontmatter + manifest consistency
  - `outdated [name]` — Check upstream source for newer commits
  - `sync` — Pull upstream updates into local repo
  - `sources list/add/remove` — Manage source manifest entries
- **60 Skills** sourced from leading open-source projects:
  - `obra/superpowers` — TDD, debugging, code review, sub-agent patterns
  - `anthropics/skills` — Brand guidelines, document processing, design
  - `addyosmani/agent-skills` — Engineering practice collection
  - `trailofbits/skills` — Security audit, static analysis, entry-point analysis
  - `Orchestra-Research/AI-Research-SKILLs` — Autonomous research workflows
  - `affaan-m/ECC` — Market research
  - `Panniantong/Agent-Reach` — Multi-platform content router
  - Plus 4 local skills authored in this repo
- **Source manifest** (`skills.manifest.json`) — Tracks upstream repo, commit hash, and last-checked timestamp for every skill
- **Cross-platform support** — Linux, macOS, Windows (WSL)
- **5-minute fetch cache** — Avoids redundant upstream fetches within 5 minutes

### Documentation

- `README.md` — Overview, value proposition, quick start, skill catalog, CLI reference
- `LICENSE` — MIT License
- `CONTRIBUTING.md` — Contribution workflow, commit conventions, style guide
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1
- `CHANGELOG.md` — This file
- `SECURITY.md` — Vulnerability reporting via GitHub Security Advisories
- `AGENTS.md` — Agent-specific installation instructions

### Security

- `SECURITY.md` documents private vulnerability disclosure process
- 72-hour acknowledgement + 90-day disclosure timeline SLA
- Source manifest allows tracing each Skill to upstream commit hash for supply chain transparency

## How to Read This Changelog

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now-removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

Each version is dated `YYYY-MM-DD`. Semantic Versioning is followed:
- **Major** (X.0.0): incompatible CLI/format changes
- **Minor** (0.Y.0): backwards-compatible functionality additions
- **Patch** (0.0.Z): backwards-compatible bug fixes

[Unreleased]: https://github.com/zhengyanxiong/skills/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/zhengyanxiong/skills/releases/tag/v1.0.0
