---
name: superpowers-bridge
description: "Bridge integration between CLI/SDD skills and Superpowers plugin. Explains when to use each system, installation, and combined workflows."
---

# skill:superpowers-bridge

## Does exactly this

Guides you through choosing and combining the **Superpowers plugin** and the **agentic-agent CLI/skills** for each phase of development. Provides a decision tree, skill mapping table, and four integrated scenario walkthroughs.

---

## Use this skill when

- You are unsure whether to use Superpowers or CLI tools for a given step
- You want to combine both systems in a single feature workflow
- Setting up Superpowers for the first time alongside the CLI
- Routing a new task to the right execution path

## Do not use this skill when

- You have already decided which system to use and know the commands
- The task is a quick single-file fix (use CLI directly)

---

## Installation check

Run: `ls ~/.claude/skills/ | grep "superpowers:"` — if files appear, Superpowers is installed.
If missing: open Claude Code → `/help` → Marketplace → search "Superpowers" → Install → Restart.

---

## Decision tree

```
START: New feature request
├─ Is the requirement CLEAR? NO  → superpowers:brainstorming
│                           YES → Continue
├─ Do you have a formal PRD?  NO  → /product-wizard skill
│                            YES → Continue
├─ Have you broken down tasks? NO  → superpowers:writing-plans OR dev-plans
│                              YES → agentic-agent openspec init
└─ Ready to implement?
   ├─ Critical logic        → TDD (superpowers or in-house)
   ├─ Parallel components   → superpowers:using-git-worktrees
   ├─ Iterative work        → superpowers:executing-plans OR run-with-ralph
   └─ Found bug             → superpowers:systematic-debugging
```

---

## Strengths at a glance

- **Superpowers** — strict methodology gates, TDD enforcement, human-in-the-loop approval, git worktrees, systematic debugging
- **CLI + in-house skills** — task traceability, context bundles, SDD 5-gate validation, multi-agent support, Ralph loop, autopilot

---

## Skill mapping reference

| Phase | CLI / Skill | Superpowers | Use Case |
|-------|-------------|-------------|----------|
| Brainstorm | brainstorming skill | superpowers:brainstorming | Unclear requirements |
| Plan | dev-plans skill | superpowers:writing-plans | Structured implementation plan |
| TDD | tdd skill | superpowers:test-driven-development | Tests first for critical logic |
| Isolation | — | superpowers:using-git-worktrees | Parallel isolated development |
| Execute | run-with-ralph skill | superpowers:executing-plans | Iterative impl with checkpoints |
| Debug | systematic-debugging skill | superpowers:systematic-debugging | 4-phase root cause analysis |
| Verify | sdd/verifier skill | superpowers:verification-before-completion | Hard gate with evidence |

---

## Done when

- Superpowers installation is confirmed (or consciously skipped)
- You have selected the right tool for each phase of your current task
- You know which scenario walkthrough matches your situation (A, B, C, or D)

---

## If you need more detail

→ `resources/workflows.md` — 4 scenario walkthroughs (A–D), full "when to prefer" bullets, troubleshooting steps, 3 quick-start checklists
