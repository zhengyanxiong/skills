---
name: Skill Proposal
about: Propose a new Skill to be included in this repository
title: "[Skill]: "
labels: ["skill-proposal"]
assignees: []
---

## 📦 Proposed Skill

- **Skill name** (will be directory name, lowercase-hyphenated):
- **One-line description** (will go in manifest and `description:` frontmatter):

## 🔗 Source

- **Upstream repository** (if applicable): [owner/repo](https://github.com/...)
- **Source URL** (specific path, if subset): e.g., `skills/<name>/SKILL.md`
- **License** of source: (MIT / Apache-2.0 / etc.)

## ✨ Value Proposition

Why is this Skill worth adding to the collection?

- [ ] It's widely-used in the AI Agent community
- [ ] It fills a gap not covered by existing Skills in this repo
- [ ] It's particularly well-maintained upstream
- [ ] It solves a problem I've personally encountered

## ✅ Compatibility Check

- [ ] `SKILL.md` has YAML frontmatter with `name:` and `description:`
- [ ] `description:` clearly describes **when** the skill should be triggered
- [ ] Content is well-organized (≤ 500 lines per file)
- [ ] License is permissive (MIT / Apache-2.0 / BSD)
- [ ] No proprietary/confidential content

## 📋 Implementation Plan

Once approved, the implementation will:

1. Run `./skills add owner/repo/path/to/skill`
2. Verify with `./skills doctor`
3. Install with `./skills install --agent codex --agent hermes`
4. Open PR with `feat(skills): add <name> from <source>` commit

## 📎 Additional Context

Links, screenshots, or worked examples.
