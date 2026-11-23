# Whole-model architecture figures: how the corpus draws each model type

A model-anatomy Figure 1 often draws one complete model (`kinds.md`, `model-anatomy`, variants `end-to-end-network`,
`overview-plus-zoom`, `multi-branch-fusion`, `unrolled-chain`). For sixteen model types that recur in the corpus,
this page says how such figures are usually drawn and names a handful of figures of each type to look at: 86
figures picked by hand on 2026-10-07 from candidate sheets of the AI exemplar library, every one with a vector
original (`assets/exemplars/ai/figures/<id>/source.svg`, `print.webp`; open with
`python3 scripts/find_ai_exemplars.py files ID`). The descriptions are the common form, as the corpus draws it; the
paper's own model decides what is drawn, and its change is what the figure must make visible.

How to use this page: find the paper's model type below, look at two or three of its figures next to the exemplars
the content search returns (`exemplar-retrieval.md`), and take the parts of that form from the library
(`assets/symbols/`, `subtype: ai`; the families named in brackets). A model of a type not listed is drawn from its
own structure with the same habits: boxes named by their function, tensors as strips or slabs, frozen and trainable
parts told apart, the new part the one strong colour.

| type | the common drawing | parts families |
|---|---|---|
| `mllm` — multimodal LLM (vision encoder + projector + LLM) | A vision encoder (a trapezoid or a box, usually with a snowflake) turns the image into a row of visual tokens; a projector maps them next to the text tokens, and both run into one large LLM box with the output written above it. Frozen and trainable parts are told apart by snowflake and fire glyphs. | `vlm`, `llm`, `token-strip`, `frozen-trainable`, `trapezoid-module` |
| `transformer` — encoder / decoder stacks | Two drawings dominate: one layer stacked vertically (multi-head attention → Add & Norm → feed-forward → Add & Norm, `xN` beside it, residual lines around the sub-blocks), or an encoder column and a decoder column side by side with K, V arrows between them for cross-attention. The paper's change is a coloured block or a formula note beside it. | `transformer-block`, `attention`, `skip-connection`, `operator-nodes` |
| `diffusion` — U-Net / DiT denoisers | The spine is a horizontal chain from noise x_T to the clean sample x_0, forward and reverse arrows of two kinds; latent diffusion adds an encoder and a decoder trapezoid at the ends. The denoiser opened up is a U-Net drawn symmetric with skip connections, or a vertical stack of DiT blocks. | `diffusion-chain`, `unet`, `vae-codebook`, `encoder-decoder` |
| `vit` — vision Transformer | A row of image patches along the bottom → patch embedding → a stack of blocks, the cls token at one end of the sequence, a classification head on top; often drawn next to BERT to show the same structure. | `vit-patchify`, `transformer-block`, `token-strip`, `mlp-head` |
| `clip-dual` — dual encoders, contrastive models | An image encoder and a text encoder (trapezoids or boxes) side by side, each emitting a row of vectors that meet in a similarity matrix or a contrastive loss in the middle; in downstream use one encoder is marked frozen. | `dual-encoder`, `contrastive-pair`, `matrix-cell-grid`, `frozen-trainable` |
| `vae-vq` — autoencoders, VAE, VQ | An encoder (narrowing trapezoid) → the latent or a codebook → a decoder (widening trapezoid), mirror-symmetric; the codebook is a row of small coloured cells, and VQ methods often draw a prior Transformer beside it. | `vae-codebook`, `encoder-decoder`, `trapezoid-module`, `vector-cells` |
| `moe` — mixture of experts | A small Router box fans out to a row of same-coloured Expert boxes; the chosen experts are highlighted or carry their weights, then a weighted sum. The MoE layer usually sits in the place of a Transformer layer. | `new:fork-arrows-from-one-input`, `transformer-block`, `module-state-coding` |
| `ssm-rnn` — state-space and recurrent models (Mamba, RNN, LSTM) | The same block repeated along time steps with hidden-state arrows linking them and an ellipsis for the middle steps; a Mamba block opened up shows its SSM, convolution and gating branches. | `transformer-block`, `token-strip`, `skip-connection` |
| `gnn` — graph neural networks | An input graph (coloured dots and edges) → GNN layer boxes → node or graph representations → a prediction head; or message passing drawn directly on the graph, arrows from the neighbours into the centre node. | `gnn-graph`, `knowledge-graph`, `mlp-head`, `vector-cells` |
| `audio-speech` — speech and audio models | A text or phoneme encoder → duration and prosody predictors → a decoder, with waveforms or spectrograms at both ends; a codec is drawn symmetric top and bottom around a row of discrete tokens, with the language model working on the tokens. | `audio-waveform`, `token-strip`, `masked-input`, `encoder-decoder` |
| `cnn` — convolutional networks (ResNet, feature pyramids) | Convolution layers as 3D slabs shrinking from large to small, or a vertical stack of Conv / BN / ReLU boxes; a feature pyramid as levels linked sideways, dilated convolutions as links widening level by level. | `cnn-stack`, `skip-connection`, `vector-cells` |
| `llm-arch` — language-model internals (decoder-only, KV cache, layers) | A vertical stack (Embedding → layers → LM Head) with the paper's change drawn on it: an extra prediction head, a KV-cache sidebar, layers skipped or selected. | `llm`, `transformer-block`, `layer-probe-taps`, `token-strip` |
| `nerf-3d` — 3D representations (NeRF, Gaussians, point-cloud networks) | An image encoder → a tri-plane or point features → an MLP → volume rendering, usually with small real renders; point-cloud networks as encoder and decoder trapezoids with point clouds at both ends. | `camera-frustums`, `point-cloud`, `mlp-head`, `encoder-decoder` |
| `rl-policy` — policy networks and world models | A sequence model unrolled over time steps, each step taking observation and action tokens, with actor and critic heads above; a world model as three parts: encoder, latent dynamics, decoder. | `rl-loop`, `token-strip`, `encoder-decoder`, `new:hierarchical-policy-stack` |
| `gan` — generative adversarial networks | A generator (widening trapezoid) and a discriminator (narrowing trapezoid) one after the other, the discriminator ending in real or fake, real and generated images between them. | `trapezoid-module`, `verdict-marks`, `before-after-pair` |
| `detection-seg` — detection and segmentation | A backbone (CNN or ViT) → an encoder → a decoder carrying a row of small object-query boxes → box or mask predictions, usually with an example image drawn with boxes; segmentation models mostly as encoder and decoder mirror-symmetric. | `cnn-stack`, `encoder-decoder`, `token-strip`, `picture-overlays` |

## Figures to look at

Ids are exemplar ids of `assets/exemplars/ai/` (cards carry `architecture: <type>`); the count in brackets is how
many candidates of that type were screened to pick them.

- `mllm` (34): `icml26-0370_fig1`, `icml25-0080_fig1`, `iclr24-0008_fig1`, `icml26-0122_fig1`, `neurips25-0084_fig1`, `icml24-0008_fig1`, `acl25-0127_fig1`
- `transformer` (132): `acl24-0024_fig1`, `neurips25-0285_fig1`, `iclr24-0108_fig1`, `icml26-0162_fig1`, `icml24-0110_fig1`, `aaai25-0072_fig1`
- `diffusion` (78): `aaai25-0110_fig1`, `neurips24-0121_fig1`, `iclr25-0065_fig1`, `iclr26-0034_fig1`, `icml26-0210_fig1`, `neurips23-0063_fig1`
- `vit` (11): `acl23-0016_fig1`, `iclr23-0019_fig1`, `iclr23-0049_fig1`, `icml24-0065_g1`, `neurips24-0259_fig1`
- `clip-dual` (57): `iclr24-0079_fig1`, `neurips24-0206_fig1`, `cvpr23-0050_fig1`, `neurips23-0138_fig1`, `cvpr25-0085_fig1`
- `vae-vq` (22): `iclr24-0037_fig1`, `aaai25-0082_fig1`, `neurips23-0080_fig2`, `neurips24-0257_fig1`, `neurips25-0047_fig1`
- `moe` (22): `acl25-0003_fig1`, `icml26-0334_fig1`, `neurips23-0009_fig1`, `aaai25-0118_fig1`, `aaai25-0078_fig1`
- `ssm-rnn` (28): `iclr25-0071_fig1`, `aaai25-0122_fig1`, `acl25-0139_fig1`, `icml26-0081_fig1`, `iclr26-0139_fig1`, `aaai23-0042_fig1`
- `gnn` (40): `neurips23-0001_fig1`, `neurips24-0357_fig1`, `neurips25-0236_fig1`, `icml25-0175_fig1`, `iclr24-0111_fig1`
- `audio-speech` (31): `icml24-0058_fig1`, `iclr25-0086_fig1`, `icml23-0003_fig1`, `neurips25-0073_fig1`, `iclr24-0119_fig1`, `acl23-0074_fig1`
- `cnn` (21): `cvpr24-0011_fig1`, `iclr23-0089_fig1`, `aaai23-0036_fig1`, `icml24-0103_fig1`, `aaai24-0045_fig1`
- `llm-arch` (10): `acl25-0028_fig1`, `icml24-0126_fig1`, `iclr25-0213_fig2`, `neurips25-0027_fig1`, `acl24-0040_fig1`
- `nerf-3d` (29): `iclr24-0053_fig1`, `iclr25-0082_fig1`, `cvpr23-0032_fig1`, `neurips23-0033_fig1`, `aaai25-0049_fig1`
- `rl-policy` (22): `iclr24-0007_fig1`, `neurips23-0131_fig1`, `icml24-0104_fig1`, `icml26-0197_fig1`, `iclr25-0246_fig1`
- `gan` (7): `aaai24-0025_fig1`, `cvpr23-0022_fig1`, `cvpr23-0047_fig1`, `aaai25-0084_fig1`
- `detection-seg` (10): `neurips23-0017_fig1`, `cvpr25-0052_fig1`, `cvpr26-0011_fig1`, `cvpr26-0031_fig1`, `aaai25-0016_g1`, `cvpr23-0039_fig1`

Two pairs of the candidates were the same paper indexed twice (`iclr24-0053` / `iclr24-0131`, `iclr25-0082` /
`iclr25-0273`); the first of each is kept. The two `_g1` ids are figures whose PDF extraction did not match the
published picture; their vector comes from the arXiv source and the card says so.

## What the records add

Across the deep records of model-anatomy figures: the model is drawn as plain boxes in 52%, trapezoids in 17%, a
layer stack in 13%; circle operators (⊕, ⊗, concat) in 63%; token or cell strips in 50%; formulas in 78%; a zoom
call-out in 37% (a wedge 15%, a lettered sub-panel named in the main drawing 12%); frozen / trainable marks in 15%
(snowflake and fire) and a colour key for state in 6%; a legend in 56%; the reading starts top-left in only 50%
(bottom-up stacks in 23%); few or no icons (none in 66%); 17 labelled boxes and 16 arrowheads on median, more than
any other kind (`kinds.md`, `encoding.md`, `layouts.md`). Audio and science-engineering figures draw anatomy as
plain boxes bottom-up; vision as encoder-decoder pairs around pictures (`domains.md`).
