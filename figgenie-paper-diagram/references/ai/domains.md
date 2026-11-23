# Sub-fields: what each field's Figure 1s do differently

An AI-venue figure is planned from two references read together: the family as a whole (the figure's kind, the
general conventions of layout, colour and encoding in the other `references/ai/` pages) and the paper's sub-field (what
that field tends to show and how). This page is the second one. It lists only what a sub-field does measurably
differently from the family; everything it does not mention follows the family. Neither view is a filter: a vision
paper whose story is a dialogue is drawn as a dialogue, and a figure that looks like none of the numbers below is a
normal outcome. The paper's own content and material come first; the field only says what readers of that field are
used to seeing. The `domain` field of a spec is descriptive: the checker never warns because of it.

## Reading the numbers

- Source: the Figure 1s of ICLR, ICML, NeurIPS, CVPR, ACL and AAAI 2023-2026. "x% (family y%)" is the share of the
  field's designed Figure 1s with that feature against the share of all 3,274 of them, from a first labelling pass over
  every figure (kinds, layout, pictures, icons, samples, the vocabulary tags of `exemplar-retrieval.md`, the paper's
  topic). A difference is listed only when it is clear (a Fisher test against the rest of the family, Benjamini-Hochberg
  q < 0.01, and at least 6 points).
- Lines marked *records* come from the 336 figures with a deep semantic record (21-69 per field; q < 0.10 and at least
  15 points); read them as indications. Colour lines come from the measured fill area of the 2,470 figures with a
  vector source.
- *Parts* are the 998 parts of the AI parts library, cut from 271 of these figures; each carries the sub-field of its
  figure (`domain`). A family is named when the field supplied at least 3 of its parts and more than twice the field's
  share of the library ("6/8" = 6 of the family's 8 parts). Parts of one figure are not independent, so this is a
  description of what the library holds, not a test.
- A paper counts under its primary field; two thirds also have a secondary one, and each section says which fields it
  is usually paired with. When a paper straddles two fields, read both sections and weigh them by what the figure has
  to show.
- The exemplars are deep-record figures rated good that carry most of the field's distinctive features, spread over
  kinds; open one with `python3 scripts/find_ai_exemplars.py card ID` or `files ID`. They show the field's habits, not
  the figure to draw. Pick the exemplars for a figure with the search in `exemplar-retrieval.md` (`--subfield` takes
  the primary field first, then the secondary), with at least one from another field.

## At a glance

| field (`--subfield`) | share | kinds that stand out (primary kind; "any" = primary or secondary) | what the figure usually holds |
|---|---:|---|---|
| `llm-nlp` | 22% | pipeline 40% (26%) | text samples, an LLM, prompts and responses, bubbles; pictures rare |
| `multimodal` | 14% | scope 13% (5%); mosaic 11% (5%) any | image + text samples together, many small pictures, bubbles, benchmark cards |
| `vision` | 15% | anatomy 38% (27%), contrast 31% (22%) | many image samples and dense maps; few icons |
| `generative` | 6% | as the family | generated images as results, a diffusion chain |
| `agents` | 4% | actors 22% (3%); walkthrough 34% (16%) any | many icons and avatars, robots and logos for models, tools, screenshots |
| `rl-robotics` | 8% | actors 15% (7%) any | robots, environments, trajectories, maps and rendered scenes; the RL loop |
| `audio` | 2% | anatomy 68% (27%) | waveforms and spectrograms, a model drawn as boxes with frozen / trainable marks |
| `science-engineering` | 14% | anatomy 43% (27%) | graphs, molecules, fields and series in the domain's own notation, formulas |
| `ml-core` | 14% | concept 24% (10%) | formulas, matrices and networks drawn schematically; little colour, few pictures |

## llm-nlp — language models and NLP

- **Kinds.** A stage pipeline is the primary kind in 40% (family 26%); a worked walkthrough is primary or secondary in
  27% (16%). Model anatomy is less common: 16% (27%).
- **Content.** The samples are text: 52% show text (14%), as prompt boxes, responses, documents, question-answer pairs,
  code snippets. Only 8% hold any picture (53%). Speech or thought bubbles 43% (25%); icons 66% (54%), many icons 42%
  (30%). An LLM is tagged on 43% (18%); *records:* the LLM idiom in 52% (29%), drawn as a box, a robot, an icon or a
  logo in roughly the family's proportions. The few pictures are rarely bitmaps (*records* 29% vs 64%) and almost
  never photographs (1% vs 24%).
- **Reading.** Serif labels 35% (44%); panels lettered (a), (b) in 14% (22%).
- **Colour.** Red is used more often (31% vs 25%); across the records its most common meaning is an error. Pictures
  cover a tenth of the canvas in 31% (55%), so the colour fields carry more of the look.
- **Papers.** Reasoning and prompting 19% (12%); also benchmarks, safety, parameter-efficient tuning, code and
  retrieval, at the family's rates.
- **Objects that stand out:** LLM, prompt, response, question and answer, document, sentence, token, card, code
  snippet, user, judge, preference, knowledge, llama, logo.
- **Parts.** 183 parts in 89 families (most: block arrows, token strips, LLM boxes). Supplied far more than its share:
  frame-border-titles 6/8, retrieval-store 4/6, search-tree 4/7, thought-bubble 3/7, positive-negative-pairs 3/8.
- **Pairs with:** ml-core 30%, agents 6%; no secondary field in 58%.
- **When it differs.** Papers on model internals (attention, representations, circuits) draw anatomy with token grids
  and heat maps rather than a pipeline; a paper whose inputs are images belongs with `multimodal` as well, and an
  agent paper with `agents` (65% of those carry `llm-nlp` as their secondary field).
- **Exemplars:** `acl25-0148_fig1` pipeline / stage chain with detail panels · `acl25-0044_fig1` walkthrough / real
  input-output trace · `iclr26-0140_fig1` actors / multi-party exchange · `iclr25-0219_fig1` contrast / paired lanes ·
  `neurips24-0070_fig1` mosaic / paper roadmap · `acl23-0008_fig1` anatomy / multi-branch fusion.

## multimodal — vision-language and other mixed-modality models

- **Kinds.** Scope overviews 13% (5%) are more common, and contribution mosaics (primary or secondary) 11% (5%); a
  plain pipeline less, 19% (26%); walkthroughs (any) 24% (16%). Figures are built as panels in 39% (30%), as boxes and
  arrows in 44% (58%), and are dense in 63% (52%).
- **Content.** Mixed samples, image and text together, in 79% (27%): 89% hold pictures (53%), 44% five or more (30%),
  mostly small (66% vs 35%) and used as sample inputs and outputs (64% vs 34%) or data thumbnails (19% vs 10%).
  Bubbles 55% (25%); icons 66% (54%), many 40% (30%), flat-colour 37% (29%); frozen / trainable marks 16% (9%); six or
  more hues 38% (30%). Tagged: a VLM 18% (4%), benchmark cards 15% (4%), film strips 11% (3%); the example-gallery
  variant 9% (2%). Formulas are rarer: 27% (50%). *Records:* natural photos 53% (24%), video frames 37% (10%) with the
  film-strip idiom 37% (10%), benchmark task cards 30% (10%), a worked example with real values in 83% (66%); the
  pictures are bitmaps in 92% (64%); units drawn as cards 48% (28%); a medium share of text 42% (23%) rather than a small
  one 40% (68%); circle nodes 17% (36%) and solid main-flow arrows 12% (28%) are named less often.
- **Reading.** Left to right only in 44% (54%).
- **Colour.** Pictures cover a tenth of the canvas in 71% (55%).
- **Papers.** Vision-language 62% (12%); reasoning and prompting 27% (12%); benchmarks 22% (11%); video 17% (6%);
  retrieval 11% (5%).
- **Objects that stand out:** image and text, question and answer, photo, video frame, caption, chart, task card, text
  and vision encoders, CLIP, VLM, crop, sunburst of tasks.
- **Parts.** 143 parts in 73 families (most: benchmark cards, token strips, zoom call-outs). Supplied far more than its
  share: benchmark-card 9/16, zoom-callout 5/15, vlm 4/4, verdict-marks 4/12, gridworld-map 4/7, dual-encoder 4/8,
  annotated-record-card 4/7, radar-chart 3/5, teacher-student 3/7, error-callouts 3/6, filmstrip 3/7,
  sunburst-taxonomy 3/5.
- **Pairs with:** vision 30%, llm-nlp 23%, ml-core 14%; no secondary field in 16%.
- **When it differs.** A paper about the model's architecture is drawn as anatomy like any encoder stack; a benchmark
  paper leans on a gallery or sunburst of tasks rather than a pipeline.
- **Exemplars:** `acl26-0044_fig1` mosaic / deliverables triptych · `neurips24-0037_fig1` scope / example gallery ·
  `icml26-0234_fig1` walkthrough / tiers on one example · `cvpr25-0073_fig1` contrast / design family ·
  `neurips25-0369_fig1` actors / single agent loop · `icml26-0365_fig1` anatomy / end-to-end network.

## vision — images, video, 3D

- **Kinds.** Model anatomy 38% (27%) and side-by-side contrast 31% (22%); pipelines 18% (26%), walkthroughs (any) 8%
  (16%), actor interaction (any) 1% (7%).
- **Content.** Pictures in 91% (53%), five or more in 62% (30%), and larger than elsewhere (a medium share of the
  canvas in 35% vs 15%, small in 52% vs 35%); image samples 53% (18%), 3D scenes 12% (3%), video frames 9% (3%); tagged
  point clouds 18% (4%) and CNN stacks 11% (3%). Icons are rarer, 38% (54%), many icons 12% (30%); bubbles 9% (25%);
  an LLM tagged on 3% (18%); text samples 0% (14%). *Records:* dense maps (attention, saliency, depth, segmentation)
  62% (11%), natural images 62% (24%), 3D renders 26% (10%), point clouds 21% (4%); the point-cloud idiom 38% (5%), the
  encoder-decoder idiom 24% (7%), the LLM idiom 3% (29%); pictures are bitmaps in 97% (64%); text takes a small share
  of the canvas in 97% (68%).
- **Reading.** Left to right 66% (54%); panels lettered (a), (b) in 31% (22%); serif labels 53% (44%); a legend 38%
  (30%).
- **Colour.** Pictures cover a tenth of the canvas in 75% (55%).
- **Papers.** Detection and segmentation 29% (8%); 3D scenes and point clouds 29% (7%); video 12% (6%); pose and
  motion 9% (2%).
- **Objects that stand out:** image, feature map, mask, segmentation, depth, camera, point cloud, Gaussians, patch,
  pose, backbone, ViT, image encoder, prototype, rendered view.
- **Parts.** 124 parts in 63 families (most: typed flow arrows, operator nodes, encoder-decoder pairs). Supplied far
  more than its share: flow-type-arrows 7/24, operator-nodes 5/12, encoder-decoder 5/14, notation-key 4/12, gnn-graph
  4/16, cnn-stack 4/6, filmstrip 3/7, vit-patchify 3/6, cycle-ring 3/7, frozen-trainable 3/6; only from this field:
  point-cloud 2, support-query-sets 2.
- **Pairs with:** ml-core 32%, multimodal 14%, generative 10%; no secondary field in 37%.
- **When it differs.** The pictures carry the story here; where the method is a dialogue or an agent, the icon and
  bubble habits of `agents` and `multimodal` apply instead.
- **Exemplars:** `neurips24-0087_fig1` anatomy / end-to-end network · `iclr25-0140_fig1` contrast / paired lanes ·
  `cvpr26-0015_fig1` pipeline / stage chain · `cvpr26-0003_fig1` mosaic / bento highlights · `cvpr26-0010_fig1`
  walkthrough / real input-output trace · `aaai25-0057_fig1` concept / formal diagram.

## generative — diffusion, flows, image and video generation

- **Kinds.** As the family; nothing stands out.
- **Content.** Pictures in 83% (53%), five or more in 61% (30%), image samples 46% (18%), pictures shown as results
  (rendered outputs) in 25% (7%) and as sample inputs and outputs in 49% (34%), small in 49% (35%) and medium-sized in
  28% (15%). A diffusion chain is tagged on 41% (7%), a U-Net on 7% (1%). Text samples 2% (14%) and an LLM 7% (18%)
  are rare. *Records:* generated images 52% (7%), the diffusion-chain idiom 36% (7%).
- **Colour.** Pictures cover a tenth of the canvas in 80% (55%), the highest share of any field.
- **Papers.** Diffusion and flow models 60% (9%); text-to-image and editing 30% (3%); video 17% (6%).
- **Objects that stand out:** generated image or video, text prompt, noisy input, denoising steps, timestep, latent,
  VAE encoder, U-Net, DiT, guidance, condition, faces and portraits, image grids.
- **Parts.** 69 parts in 51 families (most: diffusion chains, embedding spaces). Supplied far more than its share:
  diffusion-chain 4/14.
- **Pairs with:** vision 30%, ml-core 23%, multimodal 17%; no secondary field in 19%.
- **When it differs.** A generative paper about a language model or a policy follows that field; the diffusion chain is
  a reference drawing, not a requirement (records draw it the common way, as a variant, or the figure's own way).
- **Exemplars:** `iclr26-0034_fig1` anatomy / overview plus zoom · `neurips24-0077_fig1` contrast / problem then fix ·
  `icml26-0039_fig1` concept / geometric intuition · `cvpr26-0033_fig1` mosaic / bento highlights ·
  `cvpr26-0083_fig1` actors / multi-party exchange · `neurips25-0054_fig1` pipeline / phase bands.

## agents — LLM agents, tool use, multi-agent systems

- **Kinds.** Actor interaction is primary in 22% (3%) and present in 51% (7%); walkthroughs (any) 34% (16%); concept
  schematics (any) 8% (21%). Model anatomy almost never: 1% (27%) primary, 2% (41%) any. Variants: single agent loop
  11% (1%), multi-agent organisation 8% (0%).
- **Content.** Icons in 92% (54%), many in 75% (30%), flat-colour 54% (29%), mixed styles 20% (8%); bubbles 55% (25%);
  screenshots 19% (2%) and GUI screens tagged 20% (1%); tinted regions as ground 51% (32%), white ground 42% (61%).
  Tagged: an LLM 45% (18%), chat bubbles 49% (23%), a model pictogram 18% (5%), tool use 17% (1%), a brand logo 17%
  (4%), an agent loop 15% (2%), a mascot 13% (3%), several agents 11% (1%), typed trace blocks 11% (2%). Samples are
  mixed 44% (27%) or text 24% (14%). Formulas are rarer, 19% (50%); frozen / trainable marks 1% (9%); pictures 39%
  (53%), five or more 14% (30%), as sample inputs and outputs 13% (34%). *Records:* the LLM drawn in 73% (29%), as a
  robot in 33% (11%); icons in logo style 42% (15%) and cartoon style 39% (12%), bitmaps in 88% (61%); the agent loop
  42% (6%), tool use 30% (5%), several agents 24% (4%), chat bubbles 30% (12%); token strips 0% (21%). Colour tells the
  actors apart in 64% (21%); grouping by tinted regions 88% (60%), a white ground 39% (63%); a loop in the composition
  36% (10%); emphasis by size 61% (36%); cards and documents 46% (22%), bubbles 30% (10%); screenshots 24% (5%); a
  medium share of text 46% (23%) rather than a small one 39% (68%).
- **Reading.** Left to right only in 36% (54%), circular 10% (3%); serif labels 28% (44%).
- **Colour.** Pictures (mostly icons and screenshots) cover a tenth of the canvas in 71% (55%).
- **Papers.** Agents and tools 92% (7%); benchmarks 25% (11%); code 13% (3%); robot manipulation 11% (4%).
- **Objects that stand out:** agent, robot and avatar, tool, action, environment, planner, user, task, history, speech
  bubble, screenshot, code, loop, card.
- **Parts.** 115 parts in 53 families (most: chat bubbles, agent loops, typed trace blocks). Supplied far more than its
  share: chat-bubbles 9/16, agent-loop 8/11, typed-trace-blocks 5/9, pill-title-headers 4/8, tool-use 4/4,
  memory-store 3/8, thought-bubble 3/7, code-snippet-box 3/7, gui-screen 3/3; only from this field: tool-use 4,
  gui-screen 3.
- **Pairs with:** llm-nlp 65%, multimodal 20%; no secondary field in 2%.
- **When it differs.** An agent paper about training (RL fine-tuning, reward models) often draws a pipeline with few
  icons; logos and mascots are the paper's to supply (the parts library keeps grey slots for them).
- **Exemplars:** `acl25-0048_fig1` actors / single agent loop · `iclr25-0080_fig1` contrast / problem then fix ·
  `acl26-0041_fig1` scope / hub and spoke · `icml24-0039_fig1` walkthrough / real input-output trace ·
  `icml26-0016_fig1` pipeline / data construction · `icml25-0076_fig1` mosaic / bento highlights.

## rl-robotics — reinforcement learning, robots, embodied tasks

- **Kinds.** Actor interaction (primary or secondary) in 15% (7%); otherwise as the family.
- **Content.** Pictures 70% (53%), five or more 42% (30%), often as data thumbnails 18% (10%); trajectories and maps as
  samples 13% (2%). The RL loop is tagged on 25% (5%), a grid world on 8% (1%). *Records:* the RL-loop idiom 31% (5%),
  rendered 3D scenes 34% (10%), maps 21% (3%). Text samples (1% vs 14%), bubbles (15% vs 25%), chat bubbles tagged
  (14% vs 23%) and LLMs tagged (11% vs 18%) are rarer, and figures are less often dense (42% vs 52%).
- **Colour.** Pictures cover a tenth of the canvas in 68% (55%).
- **Papers.** Reinforcement learning 56% (8%); robot manipulation and navigation 38% (4%); agents and tools 18% (7%);
  world models 10% (1%).
- **Objects that stand out:** robot and robot arm, policy, environment, observation, state, action, reward, trajectory,
  rollout, replay buffer, actor and critic, goal, scene, game, world, frame.
- **Parts.** 84 parts in 54 families (most: equation boxes, token strips, encoder-decoder pairs). Supplied far more
  than its share: equation-boxes 4/10, encoder-decoder 4/14, option-catalog 3/11, rl-loop 3/6, database-cylinder 3/12,
  diffusion-chain 3/14.
- **Pairs with:** ml-core 27%, multimodal 16%, generative 12%; no secondary field in 22%.
- **When it differs.** Language-conditioned robotics borrows the prompt and bubble habits of `llm-nlp`; theory papers
  on RL look like `ml-core`.
- **Exemplars:** `iclr23-0028_fig1` actors / multi-party exchange · `iclr26-0145_fig1` mosaic / bento highlights ·
  `neurips25-0185_fig1` pipeline / fan out · `icml26-0187_fig1` concept / phenomenon on examples ·
  `iclr26-0104_fig1` contrast / paired lanes · `neurips23-0131_fig1` anatomy / end-to-end network.

## audio — speech, music, sound

- **Kinds.** Model anatomy dominates: primary in 68% (27%), present in 78% (41%); concept schematics (any) 3% (21%).
  Built as boxes and arrows 86% (58%), rarely as panels (12% vs 30%); the overview-plus-zoom variant 20% (8%) and the
  objective-graph variant 17% (4%). The reading direction is mixed in 51% (29%): bottom-up stacks next to
  left-to-right flows (*records:* bottom-up composition 46% vs 5%, reading starts top-left only in 36% vs 75%).
- **Content.** A waveform is tagged on 52% (2%), spectrogram samples 37% (1%); frozen / trainable marks 27% (9%);
  tagged token strips 27% (6%), diffusion chains 24% (7%), Transformer blocks 24% (5%), encoder-decoder 22% (5%),
  loss and gradient arrows 22% (6%), colour-coded groups 20% (6%), module state coding 15% (4%), masked input 12% (1%),
  a VAE codebook 10% (2%), skip connections 8% (1%). No image samples (0% vs 18%); chat bubbles 7% (23%). *Records:*
  the model as plain boxes 82% (29%), spectrogram pictures 41% (3%), waveform pictures 41% (4%), discrete units as
  token strips 54% (21%), Transformer blocks 36% (9%), diffusion chains 32% (7%), frozen / trainable idiom 32% (10%),
  snowflake and fire marks 27% (6%), repeat counts (xN) 32% (10%); colour tells modalities apart in 36% (8%).
- **Colour.** Pale fills in 80% (52%), orange in 76% (51%); a single-hue figure is rare (8% vs 28%). *Records:* a pale
  palette 68% (31%), a strong one 9% (38%).
- **Papers.** Speech, audio and music 97% (3%); diffusion and flow models 29% (9%); self-supervised pre-training 22%
  (9%); distillation 15% (4%); multilingual and translation 12% (2%).
- **Objects that stand out:** waveform, spectrogram, speech, feature extractor, encoder, decoder, Transformer, masked
  units, diffusion, loss.
- **Parts.** 91 parts in 41 families (most: token strips, masked inputs, diffusion chains). Supplied far more than its
  share: token-strip 8/35, masked-input 6/11, diffusion-chain 6/14, transformer-block 5/14, audio-waveform 4/4,
  loss-gradient 4/14, skip-connection 4/6, vae-codebook 4/7, notation-key 4/12, toy-values-inline 3/8; only from this
  field: audio-waveform 4.
- **Pairs with:** generative 36%, llm-nlp 24%, multimodal 19%; no secondary field in 12%.
- **When it differs.** The field is small (59 figures); speech-language papers about dialogue or evaluation follow
  `llm-nlp`, audio-visual ones `multimodal`.
- **Exemplars:** `aaai25-0124_fig1` anatomy / overview plus zoom · `neurips25-0092_fig1` anatomy / overview plus zoom ·
  `neurips25-0073_fig1` anatomy / overview plus zoom · `acl26-0047_fig1` contrast / paired lanes ·
  `iclr25-0207_fig1` pipeline / stage chain · `iclr24-0056_fig1` pipeline / closed loop.

## science-engineering — molecules, physics, biology, medicine, time series, graphs

- **Kinds.** Model anatomy 43% (27%) primary and 56% (41%) any, often an end-to-end network (16% vs 9%); contrasts are
  rarer, 12% (22%) primary and 18% (30%) any; walkthroughs (any) 8% (16%).
- **Content.** Graphs and molecules as samples 36% (6%), tables and numbers 12% (6%); formulas 60% (50%); a GNN tagged
  on 11% (3%); dense in 59% (52%); built as boxes and arrows 66% (58%). *Records:* molecule pictures 24% (2%) and the
  field's own notation drawn as an idiom 24% (3%). Bubbles (5% vs 25%), chat bubbles tagged (5% vs 23%), LLMs tagged
  (7% vs 18%), icons (44% vs 54%; many 22% vs 30%), text samples (4% vs 14%) and mixed samples (20% vs 27%) are rarer.
- **Reading.** Panels lettered (a), (b) in 30% (22%).
- **Papers.** Graph learning 29% (9%); molecules, proteins and drugs 25% (4%); medical 13% (3%); neuroscience 13%
  (4%); time series 11% (2%).
- **Objects that stand out:** graph, node and edge, subgraph, molecule and structure, time series, signal, field,
  brain and fMRI, latent, encoder and decoder, sequence, rendered field.
- **Parts.** 61 parts in 47 families (most: vector cells, token strips, GNN graphs). Supplied far more than its share:
  vector-cells 4/15, gnn-graph 3/16, encoder-decoder 3/14.
- **Pairs with:** ml-core 50%, generative 16%, llm-nlp 9%; no secondary field in 8%.
- **When it differs.** The field is a mix of sciences; the domain's own notation (a molecular graph, a PDE field, a
  brain map, a circuit) is the main content and comes from the paper, not from the corpus. The record group is small
  (21 figures).
- **Exemplars:** `icml23-0036_fig1` anatomy / multi-branch fusion · `iclr23-0081_fig1` walkthrough / state snapshots ·
  `cvpr25-0092_fig1` actors / single agent loop · `iclr23-0022_fig1` pipeline / stage chain ·
  `iclr26-0025_fig1` mosaic / finding cards · `iclr26-0239_fig1` concept / phenomenon on examples.

## ml-core — learning theory, optimisation, efficiency, federated and graph learning

- **Kinds.** Concept schematics are primary in 24% (10%) and present in 40% (21%), often a formal diagram (14% vs 4%);
  pipelines (any) 33% (44%).
- **Content.** Formulas 75% (50%), serif labels 55% (44%), tables and numbers 14% (6%); medium rather than dense
  (49% vs 41% medium, 40% vs 52% dense). Bubbles (3% vs 25%), pictures (32% vs 53%; five or more 15% vs 30%; as sample
  inputs and outputs 17% vs 34%; small 24% vs 35%), icons (36% vs 54%; many 18% vs 30%; flat-colour 19% vs 29%), text
  samples (2% vs 14%), mixed samples (11% vs 27%), LLMs tagged (2% vs 18%) and chat bubbles tagged (2% vs 23%) are rare.
  *Records:* a worked example with real values in 34% (66%); pictures are bitmaps in 40% (64%), icons in 37% (61%);
  the LLM idiom 6% (29%).
- **Colour.** No colour field at all in 22% (14%); pale fields less often (39% vs 52%); pictures cover a tenth of the
  canvas in 37% (55%).
- **Papers.** Theory and optimisation 20% (8%); federated learning 11% (2%).
- **Objects that stand out:** network and neural network, matrix, tensor, weight and parameter, layer and neuron,
  kernel, loss, update, classifier, vector, client and server (federated learning), formula.
- **Parts.** 104 parts in 60 families (most: block arrows, brace grouping, embedding spaces). Supplied far more than
  its share: block-arrows 6/27, brace-grouping 4/10, federated-round 3/4, schematic-plot 3/14, small-multiples 3/8;
  only from this field: new:formula-as-tree 2.
- **Pairs with:** vision 20%, llm-nlp 12%, science-engineering 9%; no secondary field in 50%.
- **When it differs.** Efficiency papers about LLMs (quantisation, KV cache, pruning) mix this field's matrices with the
  token strips of `llm-nlp`; federated learning draws clients and a server as actors.
- **Exemplars:** `iclr26-0017_fig1` contrast / problem then fix · `iclr26-0116_fig1` concept / formal diagram ·
  `neurips23-0232_fig1` anatomy / overview plus zoom · `iclr25-0069_fig1` mosaic / paper roadmap ·
  `acl24-0005_fig1` walkthrough / state snapshots · `cvpr25-0093_fig1` pipeline / phase bands.
