---
name: ai-sticker-pack
description: Turn a user-provided portrait into a consistent transparent-background sticker pack, including style selection, a 3x3 emotion sheet, targeted cell revisions, text variants, and deterministic splitting into individual PNGs. Use for personal avatar stickers and reusable character assets; do not claim that the resulting images are already a complete animated desktop pet.
---

# AI Sticker Pack

Create a coherent set of reusable stickers from one authorized portrait. Preserve identity first; add style, text, and derivative formats only after the base character is stable.

## Inputs and defaults

Require an attached portrait before image generation. If the image depicts someone other than the user, confirm that the user has permission to use the likeness.

Use these defaults when the user does not specify them:

- Layout: 3x3 grid, nine independent stickers.
- Emotions: happy, speechless, acknowledged, grateful, cheering, shocked, angry, giggling, good night.
- Style: cute 3D animated sticker.
- Character framing: head-and-shoulders unless the user requests full body.
- Background: genuinely transparent, not white or checkerboard drawn into the image.
- Finish: consistent thick white sticker outline, even margins, no text, no watermark, no extra people.
- Output: one master grid plus nine separate PNG files.

Ask only for choices that materially affect the result: style, desired emotions, text/no text, head-and-shoulders/full body, and intended use. Offer the defaults instead of forcing a long questionnaire.

For the ten supported visual directions, read [references/style-presets.md](references/style-presets.md). Do not imitate a named living artist or a protected studio/franchise style. Use generic visual descriptions.

## Workflow

1. Inspect the portrait and identify stable features: face shape, hairstyle, glasses, distinctive facial proportions, and clothing.
2. Confirm the selected preset and emotion list. For multiple styles, generate one complete pack per style; never mix different styles inside one grid.
3. Generate the base no-text grid using [references/prompt-templates.md](references/prompt-templates.md).
4. Review the result against [references/quality-checks.md](references/quality-checks.md). Do not call the pack complete when the identity, grid separation, outline, or transparency is inconsistent.
5. If one cell fails, revise only that cell while explicitly preserving the other eight cells, composition, character identity, clothing, palette, and rendering style. If the image tool cannot make a reliable localized edit, crop the failed cell, regenerate it from the same portrait and style constraints, then replace only that cell.
6. Add text only after the no-text pack is approved. Keep phrases short and verify every Chinese character manually. Preserve a no-text master.
7. Split the approved grid into individual files. Prefer `scripts/split_sticker_grid.py` for a regular grid; otherwise use an available deterministic image-cropping tool.
8. Verify every exported sticker and report what was generated, what was corrected, and any remaining limitations.

## Tool behavior

- Use the user's selected image-generation tool or an available image-generation capability. Do not invent access to a model, plugin, or external service.
- Keep the original portrait attached as the identity reference during regeneration.
- Do not promise one-click completion. Describe the first result as a draft until it passes validation.
- Preserve transparency throughout. If the generated master is opaque, regenerate it or use an available background-removal capability before splitting; never describe a white background as transparent.
- Do not upload, publish, or share the user's portrait or generated likeness outside the requested workflow without explicit permission.

## Splitting the grid

When Pillow is available, run:

```bash
python3 scripts/split_sticker_grid.py master.png output-dir --rows 3 --cols 3 --require-alpha --trim
```

The script writes numbered PNGs and a manifest. Inspect the outputs rather than assuming equal cropping was correct.

## Derivatives and boundaries

- Text version: create from the approved no-text pack; use one short phrase per sticker and verify spelling, font size, and placement.
- Animated stickers: select approved individual PNGs and define one small loop per sticker, such as blinking, waving, nodding, or bouncing. Keep motion subtle and preserve identity.
- Merchandise: use high-resolution exports and confirm the user owns the likeness and visual elements before commercial printing.
- Desktop pet: the sticker pack is only source material. A usable desktop pet additionally needs a transparent full-body base, idle and walking cycles, interaction states, transitions, and an application/runtime. State this boundary clearly.

## Completion standard

Deliver only after confirming:

- exactly nine intended emotions are present;
- the same person, hairstyle, glasses, clothing, and art direction persist across all cells;
- every figure is complete, centered, isolated, and surrounded by an intact white outline;
- the background contains real alpha transparency;
- no text, watermark, duplicated limb, stray character, or neighboring-cell residue remains unless explicitly requested;
- the nine exported PNGs open independently and match the approved grid.
