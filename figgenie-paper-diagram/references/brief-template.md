# The figure brief — what the user confirms before anything is drawn

The brief is a short natural-language description of everything the figure will say. It is the
human-facing artifact: the user reads it, corrects it, and only then the agent derives the JSON spec
(`spec-schema.json`) and draws. Write it in the user's language; keep component labels exactly as they will
appear in the figure (usually English, as in the paper). Be complete rather than short: every component and every
flow that will be drawn gets its own clause (typically 200–500 words; a dense double-column figure may need more).
Lists are fine, JSON is not.

Why a brief and not the spec: people judge "is this the right figure?" from prose and a walkthrough far
faster than from field names, and a wrong brief costs one message while a wrong drawing costs a redraw.

## Sections (keep the order, drop a section only when it is truly empty)

1. **What this figure is** — one sentence: the system, what the figure shows (whole system / one subsystem /
   one request path / comparison / deployment), where it sits in the paper (e.g. §3 overview), single or
   double column.
2. **Components** — every box that will appear, in reading order, grouped by container / lane. For each:
   the label as it will be written, one clause on its job, and a tag: **new** (the paper's contribution),
   existing (reused, unmodified), external (another party's system), baseline (only in comparisons).
   Say what encloses what ("Host contains …; the Device side has …"). A picture the figure shows — a sample
   input or output, a photo, a screenshot, a rendered result — is a component too: say which file it is (the
   user's, or one you will produce) and where it came from; a picture found online is downloaded into the
   figure folder, never linked.
3. **Flows and the main path** — narrate the main path as numbered steps (① … ②…), each "from → to: what
   moves". Then the secondary flows in one or two sentences, and which of them are control / feedback /
   optional (these become dashed or dotted).
4. **The one point the figure argues** — what a reader should conclude in five seconds, and where the eye
   should start and travel.
5. **Layout and style intent** — the template and direction you will use and why (name the closest exemplar
   ids from `assets/exemplars/`: some of the template, some from the same field or drawing the same kind of
   objects, found with `scripts/find_exemplars.py`), palette family, whether there is a legend and step numbers, anything the
   user said about house style (fonts, colours, an existing figure to match). If they asked for a named style
   (`references/styles/`, e.g. "Charon 风格"), name it here and, for a series of figures, the identity colour
   of each component kind so later figures reuse it.
6. **Assumptions to confirm** — 3–5 yes/no items for what you inferred rather than read, each with its
   source ("§3.1 says 'we introduce', so Scheduler is new — right?"). These are the only questions the user
   must answer; everything else has a default.
7. **Caption draft** — one to three sentences the paper can use, including the walkthrough of the numbered
   steps if there are any.

## Rules

- Completeness beats brevity: if a box or an arrow will be in the SVG, it is in the brief. The user must be able
  to reconstruct the figure's content from the brief alone.

- Infer first, ask second. Read the paper / notes / chat before writing; mark what you inferred. Ask only
  where the inference would change the figure's structure and you cannot tell from the text.
- Never invent components or flows the source does not support; if the source is thin, say so in §6 and
  propose the smallest figure that is defensible.
- Budgets from the corpus (see `layouts.md`): typical figure 10 components, 6 flows; single column ≤ 13
  labelled boxes, double ≤ 20. If the brief is heavier, say what could be merged or moved to a second figure.
- Names in the brief must be the labels the SVG will carry; the spec ids are derived from them.
- After the user confirms, changes of *content* go into the brief first (then spec, then drawing);
  changes of *layout/style* go into the spec; both stay in the working folder next to the SVG.

## Example (from the minimal example figure)

> **What.** Figure 1 of the Example paper: a single-column request-path figure for §3.1, showing how a span
> travels from a client through the new parser to the pattern library and on to the backend.
>
> **Components.** Inside *Host*: **Client** (emits spans; existing), **Span Parser** (splits a span into a
> pattern and its parameters; **new**), **Pattern Library** (stores patterns; existing). Outside the host:
> **Backend** (external collector).
>
> **Flows.** Main path: ① Client → Span Parser: raw spans. ② Span Parser → Pattern Library: parsed patterns.
> Secondary: Pattern Library → Backend: periodic *sync* (control, dashed red).
>
> **Point.** The parser is the only new part and the only thing that touches every span.
>
> **Layout.** pipeline, left-to-right, single column (240 pt); palette blue-orange with the parser as the one
> accent; no legend (three roles are explained in the caption); one circled step. Closest exemplar:
> asplos26-132_fig6.
>
> **Confirm.** (a) Is Pattern Library existing infrastructure rather than part of the contribution?
> (b) Should Backend appear at all, or is it out of scope?
>
> **Caption.** Figure 1. Example pipeline. ① The client emits spans to the Span Parser (new), which ②
> updates the Pattern Library; the library syncs to the backend.

## Mechanism figures — the same brief, three sections read differently

A mechanism figure (`meta.kind: mechanism`) shows how *one part* works, and the reader's job is different: not
"what are the pieces and how are they wired" but "what is the difference / the order / the state / the shape I am
meant to see". Keep the seven sections; write §2–§4 like this, and keep the rest as above.

2. **What is drawn** — the structure(s) the figure shows (a component's internals, a data structure, a
   timeline of actors, a state machine, a table of values …), then what is **repeated** and what **differs**:
   "the same 4-slot buffer in three frames; only the occupied slots change", "two alternatives on one
   fwd / bwd / update template; ours adds the AllGather bar". Elements still get labels as they will be
   written and new / existing / baseline tags where that matters (a comparison usually has *ours* vs *baseline*
   instead of new vs existing).
3. **The story** — the path the reader follows, in whichever form the figure has: numbered steps along a
   structure (① … with what moves at each step), transitions with their guards ("on timeout → Candidate"),
   before → after deltas per frame ("frame 2: slot 3 evicted, slot 1 highlighted"), or the values of a worked
   example and where each one recurs (input → intermediate → result).
4. **The one point the figure argues** — what the reader must *see* in five seconds and where the eye goes
   first: "the two panels are identical except the red bar", "step ③ is where the copy happens", "the dashed
   states are the ones we add". If a verdict belongs in the figure (✓ / ✗, "ours"), say it here.
5. **Layout and style intent** — the group you lean on (comparison / evolution / logic / walkthrough / anatomy,
   `references/mechanism/layouts.md`), the drawn base (component, data-structure, timeline, state-machine,
   table …), the arrangement (one drawing, panels in a row / column / grid, frames, an inset) and why; the two or
   three closest exemplars from `assets/exemplars/mechanism/<group>/index.json` plus the nearest by domain and
   content from `scripts/find_exemplars.py` (named to learn from, not to
   reproduce — the layout follows this figure's needs); how the difference will be
   marked (colour on the changed element is the corpus default; ghost, strike, callout, badge are the
   alternatives) and whether there is a legend, step markers, a worked example. **"None of the five groups fits
   exactly" is a fine answer**: then describe the reading path in your own words and name the nearest
   exemplar anyway.

Budgets are label-distinct: a structure repeated in every panel counts once (`references/mechanism/style-rules.md`
§12). If a brief needs more than about 12 distinct labelled boxes in a single column, or more than four panels,
say what could be merged, elided (`…`, `×N`) or moved to a second figure.

### Example (from `assets/specs/examples/asplos25-006_fig1.json`)

> **What.** Figure 1 of the paper: a single-column mechanism figure for §2, contrasting two ways of training the
> same model — data parallelism with a full-parameter AllReduce versus the sharded ZeRO-3 / FSDP design.
>
> **What is drawn.** One template: two devices (Device 0 / Device 1, dashed boxes) each running *fwd → bwd →
> update* on a copy of the model, repeated in two stacked panels (a) baseline, (b) ours. What differs: in (b) each
> device holds only a shard, so an **AllGather** bar (new, blue) precedes fwd and bwd and a **ReduceScatter** bar
> replaces the AllReduce after bwd.
>
> **The story.** Read (a) left to right: fwd, bwd, then AllReduce of gradients (red label) across the two devices,
> then update. Read (b) the same way and notice the two added bars and the renamed collective; peak memory drops
> because the full parameters exist only during fwd / bwd.
>
> **Point.** Same pipeline, one added collective per phase — the extra communication is the price of the
> memory saving. The eye should land on the blue bars in (b).
>
> **Layout.** Group comparison, base component, arrangement panels-column (the template is a wide chain, so the
> alternatives stack), frame template aligned; difference marked by colour on the added elements; no legend
> (two colours, both named in the caption); no step numbers. Closest exemplars: `asplos25-038_fig1`,
> `osdi26-040_fig1`.
>
> **Confirm.** (a) Is the update step drawn in both panels, or only where it differs? (b) Should the panels be
> labelled (a)/(b) or by name ("DP", "FSDP")?
>
> **Caption.** Figure 1. Data parallelism (a) AllReduces full gradients after each backward pass; ZeRO-3 / FSDP
> (b) AllGathers the sharded parameters before forward and backward and ReduceScatters gradients, trading
> communication for peak memory.

## AI-venue figures — the same brief, with the content it must carry

An AI-venue Figure 1 (`meta.family: ai`: ICLR, ICML, NeurIPS, CVPR, ACL, AAAI) is read by a reader who expects to see
the paper's material — samples, prompts and answers, pictures, icons, real numbers — not only modules and arrows
(`references/ai/kinds.md`, `domains.md`). Keep the seven sections; write §1, §2 and §5 like this.

1. **What this figure is** — add the venue (its text width is the figure's width: NeurIPS / ICLR 396 pt, ICML 486,
   CVPR 495, ACL 454, AAAI 504; one column of a two-column venue only when the content is a column), the kinds the
   figure is, primary first ("a stage pipeline with a worked example running through it"), and the paper's
   sub-field (and a second one when it straddles two).
2. **Components** — besides the modules: every **sample** the figure shows (which image tiles, which prompt and
   answer, which waveform, which molecule) with its source file or the exact text, every **picture** (a screenshot, a
   rendered result, a photo) with its role, every **icon** and what it stands for, the **worked example**'s real values,
   any **chart** or headline number, and the paper's own **logo or mascot** if it has one. Say which of these the user
   must supply (`meta.ai.materials`) and which you will draw. Name the stock forms you will draw (an LLM box, a
   Transformer block, a LoRA adapter, a token strip, a diffusion chain, an agent loop, chat bubbles: `meta.ai.idioms`)
   and what is trained and what frozen when training state matters.
3. **Flows** — as before; in an actor figure, who exchanges what with whom, and the loop; in a contrast, what each
   lane changes.
4. **The one point** — as before: what the reader must see in five seconds and where the eye goes first.
5. **Layout and style intent** — the arrangement (`references/ai/layouts.md` §1: a row of panels, a grid of cards,
   bands, lanes, a pipeline row, a hub ...) and why; the panels, lettered or titled, prior first and ours last; the
   exemplar candidates you will show the user (`references/ai/exemplar-retrieval.md`: 9-12 by kind, field, tags and
   meaning, at least one from another field; the user picks two to four, and their picks are a strong preference about
   look and feel); the palette (`references/ai/palettes.md` §9) and what colour will mean (one colour per part, per
   actor, a verdict, trainable against frozen); whether there is a legend, step markers, a title in the figure. Then
   what the field usually does and where this figure departs from it (`domains.md`, the two views read together).

Budgets follow the primary kind (`kinds.md`, "Numbers by kind"): a scope overview holds 24 text boxes on median, a
concept schematic 4; more units means smaller units, never type below 6 pt. If a text sample is longer than two or
three lines, say which lines will be quoted and that the rest is elided. A figure that looks like none of the
exemplars is a normal outcome; the paper's material comes before anything an exemplar suggests.

### Example (an LLM-agent paper at ICML)

> **What.** Figure 1 of the paper, ICML (486 pt, full width): a stage pipeline with a worked example running through
> it (`stage-pipeline` + `worked-walkthrough`), sub-field agents (secondary llm-nlp), for §1.
>
> **Components.** Three stages as tinted bands: *Plan* — **Planner** (an LLM box; existing), the user's **task** as a
> quoted text card (the real task from Table 1, two lines, user supplies the text); *Act* — **Tool calls** (a typed
> trace of three calls, our contribution, accent) and the **Browser** as a screenshot thumbnail (user supplies
> `browser.png`, 640 px wide); *Verify* — **Verifier** (an LLM box, frozen: snowflake) and the **answer** as a speech
> bubble with the real answer. Icons: a robot head for the agent, at label size, drawn from the parts library.
> Idioms: llm, typed-trace-blocks, gui-screen, chat-bubbles.
>
> **Flows.** ① task → Planner → ② Tool calls → Browser (an action), Browser → Tool calls (an observation, dashed), ③
> Tool calls → Verifier → answer; a loop back from Verifier to Planner when the check fails (curved, labelled "retry").
>
> **Point.** The typed trace in the middle is new and is what the verifier reads; the eye should land on it.
>
> **Layout.** Arrangement `bands` (three horizontal stages, left to right inside each), panels lettered (a)-(c);
> palette office-pastel with the trace as the one orange; colour by stage tint, a key for the frozen snowflake;
> plain step digits. Exemplar candidates to show the user: 10 from the search (`--kind stage-pipeline,worked-walkthrough
> --subfield agents,llm-nlp --tags typed-trace-blocks,gui-screen,chat-bubbles`), including two from multimodal. The
> field's habit (agents: icons in 92%, bubbles 55%, tinted regions 51%) is followed; its loop is drawn as the retry arc
> rather than a ring, because the stages are the story.
>
> **Confirm.** (a) Is the Verifier frozen, or fine-tuned with the planner? (b) May the real task text and the browser
> screenshot be reproduced in the figure? (c) Should the retry loop be drawn, or left to the caption?
>
> **Caption.** Figure 1. Given a task, the Planner ① issues tool calls that drive a browser ②; the typed trace of calls
> and observations is checked by a frozen Verifier ③, which returns the answer or asks the Planner to retry.
