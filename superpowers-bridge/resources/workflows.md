# superpowers-bridge: Detailed Workflows

Full detail extracted from the superpowers-bridge skill. Reference this file when you need scenario walkthroughs, preference guidance, troubleshooting, or checklists.

---

## When to Prefer Superpowers

- **Brainstorming** — Use Superpowers if requirements are vague; its structured interview surfaces unknowns
- **Planning** — Use Superpowers if you want human-in-the-loop checkpoints before implementation starts
- **TDD** — Use Superpowers if implementing payment, auth, or safety-critical code; it enforces test-first discipline
- **Worktrees** — Use Superpowers if multiple agents are working in parallel and need isolated workspaces
- **Execution** — Use Superpowers if you want automated verification between implementation iterations
- **Debugging** — Use Superpowers if the bug is subtle and requires methodical 4-phase isolation
- **Verification** — Use Superpowers if you need hard gates that refuse to mark done without evidence

## When to Prefer In-House Skills (CLI)

- **Planning** — Use `dev-plans` if you already have clear, accepted requirements; faster with less overhead
- **Execution** — Use `run-with-ralph` if you want simple iterative convergence without human checkpoints
- **Traceability** — Use `task claim / task complete` for automatic git branch + commit tracking
- **Multi-agent** — Use CLI if switching between Claude, Cursor, Windsurf, Gemini; multi-agent rules built in
- **Automation** — Use `autopilot` for fully automated task queue processing with no human gates
- **Spec verification** — Use `sdd/verifier` if you need SDD 5-gate compliance checks

---

## Scenario A: New Feature from Scratch (Unknown Requirements)

**When:** Requirements are vague, no PRD exists, discovery is needed.
**Timeline:** 2–3 hours

**Step 1 — Clarify Intent** (Superpowers)
```
/brainstorming
```
Output: Detailed brainstorm with personas, user flows, edge cases. Duration: 20–30 min.

**Step 2 — Formalize Proposal**
```
/product-wizard
```
Output: Formal PRD at `.agentic/spec/prd-<feature>.md`. Duration: 15–20 min.

**Step 3 — Create Development Plan** (Superpowers or CLI)
```
/writing-plans                            # Superpowers: human-in-the-loop checkpoints
OR
openspec init --from prd-<feature>.md     # CLI: faster, automated
```

**Step 4 — Execute Tasks**
```bash
agentic-agent task list
agentic-agent task claim TASK-ID
/executing-plans      # Superpowers: verification between iterations
OR
/ralph-loop           # CLI: iterative convergence
agentic-agent task complete TASK-ID
```

**Step 5 — Verify**
```
/verification-before-completion   # Superpowers: hard gate
OR
sdd/verifier skill                # CLI: SDD 5-gate compliance
agentic-agent openspec complete
```

---

## Scenario B: Well-Defined Feature with Critical Business Logic

**When:** You have clear specs, but the logic is payment/auth/safety-critical.
**Timeline:** 1–2 hours

**Step 1 — Initialize Change**
```bash
agentic-agent openspec init "Payment Processor" --from requirements.md
agentic-agent task list
```

**Step 2 — Implement First Task with TDD**
```
agentic-agent task claim TASK-1
/test-driven-development    # Superpowers: enforces test-first
OR
tdd skill                   # CLI: same discipline, more flexibility
```

**Step 3 — Iterative Implementation**
```bash
agentic-agent task complete TASK-1
agentic-agent task claim TASK-2
/executing-plans              # Superpowers: verification between each iteration
agentic-agent task complete TASK-2
```

**Step 4 — Final Verification**
```
/verification-before-completion     # Superpowers: hard stop until evidence
agentic-agent openspec complete
```

---

## Scenario C: Complex Debugging Session

**When:** Implementation hits an error, tests fail, or behavior is unexpected.

```
Encounter bug
    ↓
/systematic-debugging (Superpowers)
    ↓
Phase 1: Identify   — What is the symptom?
Phase 2: Isolate    — Where is the problem?
Phase 3: Narrow     — What is the root cause?
Phase 4: Apply & Test — Fix and verify
    ↓
Update code and re-run tests
```

---

## Scenario D: Parallel Component Development

**When:** Multiple services or components can be developed simultaneously.

```
agentic-agent openspec init "Multi-Service Feature"
    ↓
For each component in parallel:
├─ Agent 1: superpowers:using-git-worktrees  (Component A)
├─ Agent 2: superpowers:using-git-worktrees  (Component B)
└─ Agent 3: superpowers:using-git-worktrees  (Component C)
    ↓
All components complete (in isolation)
    ↓
Merge worktrees back to main
    ↓
Run integration tests → /verification-before-completion
```

---

## Troubleshooting

### "Superpowers skill not found"

**Fix:**
1. Verify: `/help` → Marketplace → "Superpowers" should show as installed
2. Restart Claude Code
3. Check: `ls ~/.claude/skills/ | grep "superpowers:"` should show files

### "Which skill should I use?"

- Discovering requirements → Superpowers
- Building from clear specs → CLI + in-house skills
- Debugging a mystery → `superpowers:systematic-debugging`
- Multiple agents running → CLI for multi-agent rules

### "Can I skip Superpowers and use only CLI?"

**Yes.** All Superpowers skills have in-house equivalents:

| Superpowers | CLI / In-House Skill |
|-------------|----------------------|
| `superpowers:brainstorming` | `brainstorming` skill |
| `superpowers:writing-plans` | `dev-plans` skill |
| `superpowers:test-driven-development` | `tdd` skill |
| `superpowers:executing-plans` | `run-with-ralph` skill |
| `superpowers:systematic-debugging` | `systematic-debugging` skill |
| `superpowers:verification-before-completion` | `sdd/verifier` skill |

Difference: Superpowers = stricter methodology gates. In-house = more flexible automation.

### "When should I NOT use Superpowers?"

- Quick bug fixes (typos, single-line changes)
- Well-understood features with clear specs
- Simple UI tweaks (colors, spacing, copy)
- Running fully automated mode — use `agentic-agent autopilot` instead

---

## Quick-Start Checklists

### Checklist: Using CLI + Superpowers Together

- [ ] Brainstorm unclear requirements: `/brainstorming` (Superpowers)
- [ ] Formalize into PRD: `/product-wizard`
- [ ] Create plan: `/writing-plans` (Superpowers) OR `dev-plans` skill
- [ ] Initialize change: `agentic-agent openspec init ...`
- [ ] List tasks: `agentic-agent task list`
- [ ] For each task:
  - [ ] `agentic-agent task claim TASK-ID`
  - [ ] Implement with `/executing-plans` (Superpowers) OR `/ralph-loop`
  - [ ] `agentic-agent task complete TASK-ID`
- [ ] Verify: `/verification-before-completion` (Superpowers) OR `sdd/verifier`
- [ ] Finalize: `agentic-agent openspec complete`

### Checklist: Using CLI Only (No Superpowers)

- [ ] Start with clear requirements (PRD or spec already exists)
- [ ] `agentic-agent openspec init --from <requirements.md>`
- [ ] `agentic-agent task list`
- [ ] For each task:
  - [ ] `agentic-agent task claim TASK-ID`
  - [ ] Implement with `tdd` skill OR `run-with-ralph` skill
  - [ ] `agentic-agent task complete TASK-ID`
- [ ] Verify: `sdd/verifier` skill
- [ ] Finalize: `agentic-agent openspec complete`

### Checklist: Installing Superpowers

- [ ] Open Claude Code
- [ ] Run `/help` → Marketplace
- [ ] Search for "Superpowers"
- [ ] Click Install
- [ ] Restart Claude Code
- [ ] Verify: `ls ~/.claude/skills/ | grep "superpowers:"` shows results
- [ ] Try: `/brainstorming` or `/help superpowers`

---

*This file is the detailed companion to `../SKILL.md`. Reference it when you need full scenario walkthroughs, preference guidance, or troubleshooting.*
