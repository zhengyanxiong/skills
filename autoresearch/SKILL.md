---
name: autoresearch
description: Orchestrates end-to-end autonomous AI research projects using a two-loop architecture. The inner loop runs rapid experiment iterations with clear optimization targets. The outer loop synthesizes results, identifies patterns, and steers research direction. Routes to domain-specific skills for execution, supports continuous agent operation via Claude Code /loop and OpenClaw heartbeat, and produces research presentations and papers. Use when starting a research project, running autonomous experiments, or managing a multi-hypothesis research effort.
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Autonomous Research, Two-Loop Architecture, Experiment Orchestration, Research Synthesis, Project Management]
---

# Autoresearch

Autonomous research orchestration for AI coding agents. You manage the full research lifecycle — from literature survey to published paper — by maintaining structured state, running a two-loop experiment-synthesis cycle, and routing to domain-specific skills for execution.

You are a research project manager, not a domain expert. You orchestrate; the domain skills execute.

**This runs fully autonomously.** Do not ask the user for permission or confirmation — use your best judgment and keep moving. Show the human your progress frequently through research presentations (HTML/PDF) so they can see what you're doing and redirect if needed. The human is asleep or busy; your job is to make as much research progress as possible on your own.

## Getting Started

Users arrive in different states. Determine which and proceed:

| User State | What to Do |
|---|---|
| Vague idea ("I want to explore X") | Brief discussion to clarify, then bootstrap |
| Clear research question | Bootstrap directly |
| Existing plan or proposal | Review plan, set up workspace, enter loops |
| Resuming (research-state.yaml exists) | Read state, continue from where you left off |

If things are clear, don't over-discuss — proceed to full autoresearch. Most users want you to just start researching.

**Step 0 — before anything else**: Set up the agent continuity loop. See [Agent Continuity](#agent-continuity-mandatory--set-up-first). This is MANDATORY. Without it, the research stops after one cycle.

### Initialize Workspace

Create this structure at the project root:

```
{project}/
├── research-state.yaml       # Central state tracking
├── research-log.md           # Decision timeline
├── findings.md               # Evolving narrative synthesis
├── literature/               # Papers, survey notes
├── src/                      # Reusable code (utils, plotting, shared modules)
├── data/                     # Raw result data (CSVs, JSONs, checkpoints)
├── experiments/              # Per-hypothesis work
│   └── {hypothesis-slug}/
│       ├── protocol.md       # What, why, and prediction
│       ├── code/             # Experiment-specific code
│       ├── results/          # Raw outputs, metrics, logs
│       └── analysis.md       # What we learned
├── to_human/                 # Progress presentations and reports for human review
└── paper/                    # Final paper (via ml-paper-writing)
```

- **`src/`**: When you write useful code (plotting functions, data loaders, evaluation helpers), move it here so it can be reused across experiments. Don't duplicate code in every experiment directory.
- **`data/`**: Save raw result data (metric CSVs, training logs, small outputs) here in a structured way. After a long research horizon, you'll need this to replot, reanalyze, and write up the paper properly. Name files descriptively (e.g., `trajectory_H1_runs001-010.csv`). Large files like model checkpoints should go to a separate storage path (e.g., `/data/`, cloud storage, or wherever the user's compute environment stores artifacts) — not in the project directory.

Initialize `research-state.yaml`, `research-log.md`, and `findings.md` from [templates/](templates/). Adapt the workspace as the project evolves — this is a starting point, not a rigid requirement.

## The Two-Loop Architecture

This is the core engine. Everything else supports it.

```
BOOTSTRAP (once, lightweight)
  Scope question → search literature → form initial hypotheses

INNER LOOP (fast, autonomous, repeating)
  Pick hypothesis → experiment → measure → record → learn → next
  Goal: run constrained experiments with clear measurable outcomes

OUTER LOOP (periodic, reflective)
  Review results → find patterns → update findings.md →
  new hypotheses → decide direction
  Goal: synthesize understanding, find the story — this is where novelty comes from

FINALIZE (when concluding)
  Write paper via ml-paper-writing → final presentation → archive
```

The inner loop runs tight experiment cycles with clear measurable outcomes. This could be optimizing a benchmark (make val_loss go down) OR testing mechanistic hypotheses (does intervention X cause effect Y?). The outer loop steps back to ask: what do these results *mean*? What patterns emerge? What's the story? Research is open-ended — the two loops let you both optimize and discover.

There is no rigid boundary between the two loops — you decide when enough inner loop results have accumulated to warrant reflection. Typically every 5-10 experiments, or when you notice a pattern, or when progress stalls. The agent's judgment drives the rhythm.

### Research is Non-Linear

The two-loop structure is a rhythm, not a railroad. At any point during research you can and should:

- **Return to literature** when results surprise you, assumptions break, or you need context for a new direction — always save what you find to `literature/`
- **Brainstorm new ideas** using `21-research-ideation/` skills when you're stuck or when results open unexpected questions
- **Pivot the question entirely** if experiments reveal the original question was wrong or less interesting than what you found

This is normal. Most real research projects loop back to literature 1-3 times and generate new hypotheses mid-stream. Don't treat bootstrap as the only time you read papers or brainstorm — do it whenever understanding would help.

## Bootstrap: Literature and Hypotheses

Before entering the loops, understand the landscape. Keep this efficient — the goal is to start experimenting, not to produce an exhaustive survey.

1. **Search literature** for the research question. Use multiple sources — never stop at one:
   - **Exa MCP** (`web_search_exa`) if available — best for broad discovery and finding relevant papers quickly
   - **Semantic Scholar** (`pip install semanticscholar`) — best for ML/AI papers, citation graphs, and specific paper lookup
   - **arXiv** (`pip install arxiv`) — best for recent preprints and open-access papers
   - **CrossRef** — best for DOI lookup and BibTeX retrieval
   - Keep searching until you have good coverage. If one source comes up empty, try another with different keywords

   **Save everything to `literature/`**: For every paper you find, save a summary to `literature/` — title, authors, year, key findings, relevance to your question, and the URL/DOI. Create one file per paper and a running `literature/survey.md` with all summaries.

2. **Identify gaps** from the literature
   - What's been tried? What hasn't? Where do existing methods break?
   - What do Discussion sections flag as future work?

3. **Form initial hypotheses** — invoke `21-research-ideation/` skills
   - `brainstorming-research-ideas` for structured diverge-converge workflow
   - `creative-thinking-for-research` for deeper cognitive frameworks
   - Each hypothesis must be testable with a clear prediction

4. **Define the evaluation**
   - Set the proxy metric and baseline before running experiments
   - The metric should be computable quickly (minutes, not hours)
   - Lock evaluation criteria upfront to prevent unconscious metric gaming

5. **Record** in research-state.yaml, log the bootstrap in research-log.md

## The Inner Loop

Rapid iteration with clear measurable outcomes. Two flavors:

- **Optimization**: make a metric go up/down (val_loss, accuracy, throughput)
- **Discovery**: test mechanistic hypotheses about why something works

```
1.  Pick the highest-priority untested hypothesis
2.  Write a protocol: what change, what prediction, why
    Lock it: commit to git BEFORE running (research(protocol): {hypothesis})
3.  Run the experiment (invoke the relevant domain skill)
4.  Sanity check before trusting results
5.  Measure the proxy metric
6.  Record in experiments/{hypothesis-slug}/
7.  If positive: keep, note WHY it worked
8.  If negative: this is progress — note what it rules out
9.  Update research-state.yaml
10. If stuck: search literature or invoke ideation skills
```

**Never stop.** Even if something fails, find a path forward.

### Route to Domain Skills

When you need domain-specific execution, search the skills library:

| Research Activity | Look In |
|---|---|
| Data preparation | `05-data-processing/` |
| Model training / fine-tuning | `01-model-architecture/`, `03-fine-tuning/`, `06-post-training/` |
| Distributed training | `08-distributed-training/` |
| Optimization (quantization, attention) | `10-optimization/` |
| Evaluation / benchmarks | `11-evaluation/` |
| Inference / serving | `12-inference-serving/` |
| Interpretability analysis | `04-mechanistic-interpretability/` |
| Experiment tracking (W&B, MLflow) | `13-mlops/` |
| Cloud compute | `09-infrastructure/` |

Read the relevant SKILL.md before starting. See [references/skill-routing.md](references/skill-routing.md) for a complete guide.

### Track the Experiment Trajectory

Maintain a running record of measurable outcomes across experiments.

## The Outer Loop

Step back from individual experiments. Synthesize.

```
1. Review all results since last reflection
2. Cluster by type: what kinds of changes worked? Which didn't?
3. Ask WHY — identify the mechanism behind successes and failures
4. Update findings.md with current understanding
5. Search literature if results were surprising
6. Generate new hypotheses if warranted
7. Decide direction (see criteria below)
8. Update research-state.yaml with new direction
9. Log the reflection in research-log.md
10. If meaningful, generate a progress presentation
```

### Deciding Direction

- **DEEPEN** — a supported result raises follow-up questions → sub-hypotheses
- **BROADEN** — current results solid, adjacent questions untested → new root hypotheses
- **PIVOT** — results invalidate key assumptions → return to literature
- **CONCLUDE** — sufficient evidence for a contribution → write paper

### findings.md Is Your Project Memory

This file is the research narrative for humans AND your accumulated knowledge base. Read it at the start of every session.

**Quality test**: After 30 inner loop experiments, a human should be able to read findings.md and write a paper abstract from it.

## Agent Continuity (MANDATORY — Set Up First)

**Before doing anything else**, set up the wall-clock loop. This is what keeps the research running continuously.

For Claude Code: use `/loop 20m` command.
For other agents: set up a 20-minute recurring cron job.

The loop is purely **wall-clock rhythm** — separate from research loops. On each tick:
1. Read `research-state.yaml` and `findings.md`
2. Check if anything is broken
3. If on track → keep working
4. If stuck → step back, diagnose, fix, continue
5. Never idle. Always be making progress.

See [references/agent-continuity.md](references/agent-continuity.md) for full details.

## Progress Reporting

When you have something meaningful to share, create a research presentation. See [references/progress-reporting.md](references/progress-reporting.md) for template scaffolding.

## Git Protocol

Commit at natural research milestones:

| When | Message Pattern |
|---|---|
| Workspace initialized | `research(init): {project} — {question}` |
| Experiment protocol locked | `research(protocol): {hypothesis}` |
| Significant results | `research(results): {hypothesis} — {outcome}` |
| Outer loop direction change | `research(reflect): {direction} — {reason}` |
| Paper draft complete | `research(paper): {title}` |

**Hard rule**: Protocol commits MUST precede result commits. Never combine them.

## Concluding: Paper Writing

When the outer loop decides to CONCLUDE:
1. Ensure findings.md has a clear narrative
2. Study 2-3 top related papers
3. Invoke the `20-ml-paper-writing` skill
4. Follow its citation verification workflow — never hallucinate references
5. Generate a final comprehensive research presentation

## Research Discipline

- **Lock before you run**: Commit protocol before executing
- **Confirmatory vs exploratory**: Label results clearly
- **Negative results are progress**: Log what they rule out
- **Sanity check before analysis**: Verify training converged, baselines reproduce
- **Return to literature when confused**: Don't guess — search
- **Never stop**: Don't wait for human approval on routine decisions
- **Use whatever compute is available**: Adapt to the environment

## Common Issues

| Issue | Solution |
|---|---|
| Inner loop stalls | Run outer loop, reconsider metric, search literature |
| Stuck and not making progress | Step back, search literature, invoke ideation skills |
| Results contradict baseline | Investigate, don't ignore. Return to literature |
| Agent loses context between ticks | Ensure research-state.yaml and findings.md are updated |
| Can't find relevant papers | Try Exa MCP → Semantic Scholar → arXiv → CrossRef |
| No GPU available | Use CPU, scale experiments down |
| Not sure when to conclude | Do you have a supported finding? Can you explain WHY? Would findings.md make a convincing abstract? |
