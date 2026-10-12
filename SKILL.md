---
name: PersonaStickerSkill
description: Turn a user-provided portrait into a consistent transparent-background 3x3 sticker sheet, with full style selection, targeted cell revisions, optional text variants, and optional splitting into individual PNGs only when explicitly requested. Use for personal avatar stickers and reusable character assets; do not claim that the resulting images are already a complete animated desktop pet.
---

# PersonaStickerSkill

Create a coherent set of reusable stickers from one authorized portrait. Preserve identity first; add style, text, and derivative formats only after the base character is stable.

## Inputs and defaults

Require an attached portrait before image generation. If the image depicts someone other than the user, confirm that the user has permission to use the likeness.

Use these defaults when the user does not specify them:

- Layout: 3x3 grid, nine independent stickers.
- Emotions: happy, speechless, acknowledged, grateful, cheering, shocked, angry, giggling, good night.
- Style: ask the user to choose from the complete ten-preset list below. Use cute 3D animated sticker only when the user explicitly accepts the default.
- Character framing: head-and-shoulders unless the user requests full body.
- Background at generation time: one solid key color chosen per portrait with `scripts/pick_chroma_color.py` — maximum contrast with the person's hair, clothing, and skin. White is never used because the outline is white. After generation, `scripts/rebuild_outline.py --chroma <hex>` keys the background to genuine transparency; the delivered master is always truly transparent, never a white or painted checkerboard background.
- Finish: consistent thick white sticker outline, even margins, no text, no watermark, no extra people.
- Default output: one unsplit master grid only, generated in a single pass on the chosen key color and then keyed to transparency deterministically. Never generate two versions (for example an opaque or white-background draft plus a transparent version). Individual PNG files are optional and require a separate, explicit user request to split, crop, or export the cells.

Ask only for choices that materially affect the result: style, desired emotions, text/no text, head-and-shoulders/full body, and intended use. Offer the defaults instead of forcing a long questionnaire.

When the user has not already selected a style, present all ten options below in one numbered list. Do not shorten the list, show only a subset, or replace it with four recommended options:

1. 3D animated sticker
2. Japanese manga
3. Hand-drawn watercolor
4. Pixel art
5. Clay figure
6. Cyberpunk neon
7. Flat vector
8. Retro print
9. Soft crayon
10. Felt doll

Wait for the user's selection before generating unless the user explicitly asks the skill to choose. For the visual attributes of each option, read [references/style-presets.md](references/style-presets.md). Do not imitate a named living artist or a protected studio/franchise style. Use generic visual descriptions.

## Workflow

1. Inspect the portrait and identify stable features: face shape, hairstyle, glasses, distinctive facial proportions, and clothing.
2. Confirm the selected preset and emotion list. For multiple styles, generate one complete pack per style; never mix different styles inside one grid. Generate every additional pack from the original portrait only — never attach, reference, or imitate a previously generated pack — and require each new pack to differ visibly from earlier packs in at least three rendering attributes, such as line work, shading method, material/texture, palette, and outline treatment. Only identity anchors (face shape, hairstyle, glasses, clothing) carry over across styles; rendering, palette, and lighting follow the new preset alone.
3. Pick the key color: run `python3 scripts/pick_chroma_color.py <portrait>` and fill the reported hex into the template's [key color] field. Generate the base no-text grid using [references/prompt-templates.md](references/prompt-templates.md) — exactly once, on that solid key color, with no second variant. Then key the background and rebuild the outline deterministically: `python3 scripts/rebuild_outline.py master-raw.png master.png --chroma <hex>`. The keyed result is the one and only master grid.
4. Review the result against [references/quality-checks.md](references/quality-checks.md). Do this review silently, before any user-facing display; never show the grid to the user while anything fails. Do not call the pack complete when the identity, grid separation, outline, or transparency is inconsistent.
5. If one cell fails, revise only that cell while explicitly preserving the other eight cells, composition, character identity, clothing, palette, and rendering style. If the image tool cannot make a reliable localized edit, crop the failed cell, regenerate it from the same portrait and style constraints, then replace only that cell. Overlapping figures, duplicate heads, and ghost residue from a previous edit always count as unreliable localized edits: use the crop-regenerate-replace path for them instead of another inpainting pass, and verify the replacement cell contains exactly one character with one head and one body, fully inside its cell. Re-run the full quality review on the repaired grid before showing anything.
6. Add text only after the no-text pack is approved. Keep phrases short and verify every Chinese character manually. Preserve a no-text master.
7. Present the approved master grid and stop. This presentation is the first and only time the grid is shown to the user — failed drafts, intermediate regenerations, and repair passes are never displayed. Do not split, crop, or export individual cells automatically.
8. Only after the user explicitly asks to split, crop, or export the grid, use `scripts/split_sticker_grid.py` for a regular grid or another deterministic image-cropping tool. Then verify every exported sticker.

## Tool behavior

- Use the user's selected image-generation tool or an available image-generation capability. Do not invent access to a model, plugin, or external service.
- Keep the original portrait attached as the identity reference during regeneration.
- Do not promise one-click completion. Treat every first result as a draft: validate it internally and repair failures silently. Show the grid to the user exactly once, only after it passes all quality checks; never display a failed draft and then its replacement.
- Generate the grid exactly once, on the chosen solid key color. Transparency comes from deterministic keying afterwards — never from a second generation, an opaque preview, or a white-background variant; never describe a white background as transparent, and never keep two versions.
- Choose the key color from the portrait with `scripts/pick_chroma_color.py`: it must be far from hair, clothing, and skin (clearance at least 90 in the report). White is forbidden because it would take the outline with it; black only when the portrait has no dark hair or clothing.
- Key and repair with `scripts/rebuild_outline.py` (`--chroma <hex>`, or `--chroma auto` for solid backgrounds of unknown color): it keys the background, strips any broken outline, and repaints a closed, uniform outline from the figure silhouette, so the result is correct by construction. Never fix outline or alpha problems by re-generating or by re-running a matting tool that eats white edges.
- Treat splitting as a distinct optional action. Approval of the grid, a request to save it, or silence after generation does not authorize splitting. Ask whether the user wants nine separate PNGs if that next step may be useful, then wait for an explicit answer.
- Do not upload, publish, or share the user's portrait or generated likeness outside the requested workflow without explicit permission.

## Splitting the grid

Do not enter this stage unless the user explicitly requests separate images. Generating or approving the master grid is not permission to run the splitting script.

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

For the default unsplit master grid, deliver only after confirming:

- exactly nine intended emotions are present;
- the same person, hairstyle, glasses, clothing, and art direction persist across all cells;
- every figure is complete, centered, isolated, and surrounded by an intact white outline;
- the background contains real alpha transparency;
- no text, watermark, duplicated limb, stray character, or neighboring-cell residue remains unless explicitly requested;

If the user explicitly requested splitting, additionally confirm that the nine exported PNGs open independently and match the approved grid.
