# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is a collection of Agent Skills following the Anthropic Agent Skills open standard. Each skill is a directory containing a `SKILL.md` (the core instruction file) plus optional `references/`, `scripts/`, and `assets/` subdirectories.

Skills currently in this repo:
- `skill-authoring-guide/` -- teaches how to write high-quality Skills (meta-skill)
- `coross-platform-vim-nvim-deploy/` -- cross-platform Vim/Neovim configuration deployment

## Skill structure

Every skill directory follows this convention:

```
skill-name/
├── SKILL.md          # Required: YAML frontmatter + markdown instructions
├── scripts/          # Optional: executable code (Python/Bash/JS)
├── references/       # Optional: documentation loaded on demand
└── assets/           # Optional: templates and resources
```

### SKILL.md format

The frontmatter must include `name` and `description`. The `name` must match the parent directory name.

```yaml
---
name: skill-name
description: >
  What this skill does and when to use it. Include trigger keywords.
---
```

Naming rules for `name` and directory: lowercase, digits, hyphens only (1-64 chars). No leading/trailing hyphens, no consecutive hyphens.

## Design principles

When creating or modifying skills, follow these rules (from `skill-authoring-guide/`):

1. **Three-layer progressive loading**: L1 (name + description) loaded at session start; L2 (SKILL.md body) loaded on activation; L3 (references/scripts/assets) loaded on demand. Keep SKILL.md under 500 lines -- split detailed content into `references/`.
2. **Model-driven triggering**: The `description` field determines when the skill activates. Make it specific, include trigger keywords, and cover multiple user phrasings.
3. **Explain "why", not "must"**: Explain the rationale behind rules rather than stacking ALWAYS/NEVER/MUST commands.
4. **Generalize, don't overfit**: Design skills to handle diverse inputs, not just the test cases.
5. **Include evals**: Each skill should have `evals.json` (2-3 test cases) and `assertions.json` (5-10 quantifiable assertions) for A/B testing skill effectiveness.

## Five design patterns

- **Tool Wrapper**: Load conventions from `references/` to make the agent a domain expert
- **Generator**: Produce standardized output from structured input (templates + boundary handling)
- **Reviewer**: Score code against a checklist with severity levels and fix suggestions
- **Inversion** (Interactive): Interview the user before executing, with defaults to reduce friction
- **Pipeline**: Enforce strict multi-step workflows with checkpoints between stages
