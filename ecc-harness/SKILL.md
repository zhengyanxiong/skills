---
name: ecc-harness
description: ECC (Everything Claude Code) integration hub — surfaces the curated subset of ECC skills installed in this repo and explains how they extend existing skills. Use when the user mentions "ECC", asks about a specific ECC sub-skill (council, dmux-workflows, agent-eval, context-budget, etc.), or wants to know which ECC skill to reach for in cross-language TDD / multi-agent orchestration / agent self-improvement / research workflows.
metadata:
  origin: hermes
  upstream: affaan-m/ECC
  upstream_path: skills/
  upstream_stars: 227000
  installed_sub_skills: 31
---

# ECC Harness Integration Hub

ECC (`affaan-m/ECC`, ⭐227k) is a production-grade Agent Harness with **277 Skills / 67 Agents / 93 Commands / 34+ language-specific Rules**. It is too large to install wholesale without diluting the existing curated skills repo, so this hub installs a **31-skill curated subset** that fills gaps without overlap.

> **Upstream:** `https://github.com/affaan-m/ECC` — for the full 277-skill set, browse upstream directly.

## Why this subset

Selection criteria:
1. **Zero overlap** with the 73 pre-existing skills (verified via name diff).
2. **Aligns with ECC's stated strengths:** cross-language review, research-driven development, security scanning, multi-agent orchestration.
3. **Non-trivial SKILL.md size** (>2 KB) — filters out stubs.
4. **Each fills a real gap** rather than restating existing capability.

## What was NOT installed (and why)

- **`market-research`** — already installed locally from a previous ECC subset (path `.agents/skills/market-research`).
- **Niche domain skills** (healthcare, energy, defi, etc.) — too vertical for a general-purpose harness.
- **Style/UI skills** — overlap with `taste-skill` (just installed) and existing `frontend-design` / `canvas-design`.
- **Single-file scaffolds** (claude-devfleet, hookify-rules, ck, etc.) — utilities, not reusable knowledge.
- **Agent-prompt .md files** — ECC keeps many agent persona files outside `skills/`; we only took SKILL.md units.
- **Duplicate function** (e.g. multiple TDD skills for languages where one already exists).

## Installed sub-skills (31)

### Multi-Agent Orchestration (5)
| Skill | What it adds |
|-------|--------------|
| `council` | Convene four-voice (Skeptic/Pragmatist/Critic/in-context) council for ambiguous decisions. Distinct from `dispatching-parallel-agents` (which splits work) — `council` runs structured disagreement on a single decision. |
| `dmux-workflows` | Worktree-based multi-agent orchestration — each agent runs in isolated git worktree. Complements `dispatching-parallel-agents`. |
| `plan-orchestrate` | Plan-then-orchestrate pattern for multi-step agent workflows. |
| `team-agent-orchestration` | Higher-level team-of-agents coordination pattern. |
| `team-builder` | Compose multi-agent teams from specialist agents. |

### Agent Self-Improvement (4)
| Skill | What it adds |
|-------|--------------|
| `agent-eval` | Head-to-head agent comparison CLI (pass rate, cost, time, consistency). |
| `agent-introspection-debugging` | Debug agents by tracing their own reasoning. |
| `context-budget` | Token/context budget management across long-running tasks. |
| `prompt-optimizer` | Systematic prompt tuning with measured outcomes. |

### Cross-Language TDD/Testing (12)
| Skill | Language |
|-------|----------|
| `cpp-testing` | C++ |
| `csharp-testing` | C# |
| `fsharp-testing` | F# |
| `golang-testing` | Go |
| `kotlin-testing` | Kotlin |
| `python-testing` | Python (complements generic `test-driven-development`) |
| `react-testing` | React |
| `rust-testing` | Rust |
| `django-tdd` | Django (Python) |
| `laravel-tdd` | Laravel (PHP) |
| `quarkus-tdd` | Quarkus (Java) |
| `springboot-tdd` | Spring Boot (Java) |

### Security (4)
| Skill | What it adds |
|-------|--------------|
| `security-review` | Generic security review workflow (complements `security-and-hardening`). |
| `security-scan` | Run security scans with structured output. |
| `django-security` | Django-specific security patterns. |
| `laravel-security` | Laravel-specific security patterns. |

### Research & Verification (4)
| Skill | What it adds |
|-------|--------------|
| `deep-research` | Multi-source deep research with synthesis. Complements `autoresearch`. |
| `research-ops` | Research operations — sourcing, citation, archival. |
| `verification-loop` | Systematic verification before claiming completion. Reinforces `verification-before-completion`. |
| `continuous-learning` | Extract learnings from completed sessions (overlaps with `continuous-learning-v2` style). |

### Backend Patterns (2)
| Skill | What it adds |
|-------|--------------|
| `backend-patterns` | Cross-language backend architecture patterns. |
| `deployment-patterns` | Deployment patterns across platforms. |

## When to reach for which

- **Decision under ambiguity** → `council`
- **Parallel investigation across worktrees** → `dmux-workflows`
- **Comparing which coding agent is best** → `agent-eval`
- **Long task, watching context** → `context-budget`
- **Tuning a prompt** → `prompt-optimizer`
- **Code review for non-Python/TS** → `cpp-testing` / `golang-testing` / `rust-testing` / `springboot-tdd` etc.
- **Generic security review (not framework-specific)** → `security-review`
- **Django/Laravel security** → framework-specific skill
- **Deep multi-source research** → `deep-research` (lightweight single-source → use existing `market-research`)

## How this stays current

The 31 skills are **frozen at the version installed today** (ECC `main`, 2026-07-08). To upgrade:

```bash
cd ~/workspace/skills
python3 skills.py outdated           # check upstream drift
python3 skills.py sync ecc-harness   # sync this hub + sub-skills (when sync supports paths)
```

For now, refresh = rerun `python3 skills.py add affaan-m/ECC` against the cache and re-curate.

## Source attribution

All 31 sub-skills carry `metadata.origin: ECC` in their SKILL.md frontmatter. Do not strip this — it tells future curators where the skill came from and how to re-sync.