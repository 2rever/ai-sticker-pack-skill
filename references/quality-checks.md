# Sticker pack quality checks

## Before generation

- The portrait is sharp enough to identify the face shape, hairstyle, glasses, and clothing.
- The key color was chosen with `scripts/pick_chroma_color.py`, its clearance is at least 90, and the character does not wear or hold anything near the key color.
- The user selected or accepted a style, framing, emotion list, and text preference.
- The source likeness is authorized for the requested use.

## Master-grid review

Inspect at full size:

- **Identity:** all nine cells depict the same person.
- **Consistency:** hairstyle, glasses, clothing, palette, lighting, proportions, and outline match.
- **Expression:** every requested emotion is distinct and in the correct grid position.
- **Anatomy:** no extra fingers, merged hands, duplicated limbs, or broken facial features. Both eyes are fully drawn and visible in every cell — lenses are transparent when the character wears glasses, and closed-eye expressions still show eyelid lines and lashes. Solid black, blank, frosted, or skin-colored lenses and any glasses rendering that fully hides the eyes count as broken faces and fail the review.
- **Separation:** no sticker crosses a cell boundary or touches another sticker; each sticker, including outline, hair, hands, and raised arms, occupies at most 70 percent of its cell. No grid lines, divider lines, cell borders, panels, or cards are drawn behind or between stickers, and no glow or rim light in the key color surrounds the stickers.
- **Coverage:** transparent pixels should make up roughly half the image or more for a 3x3 pack at 70 percent cell fill. Substantially less means background panels leaked through — treat it as a failed generation and regenerate, never as a repair job.
- **Single figure:** every cell contains exactly one character with exactly one head and one body — no duplicate heads, overlapping figures, or ghost afterimages left by a previous edit.
- **Margins:** every figure and its white outline fit comfortably inside its cell.
- **Transparency:** corners and spaces between stickers have real alpha transparency. When keying was necessary, no key-color halo, fiber fringe, or detached residue remains along the edges (raise `--chroma-tol`, or use `--erode 2-4` for fuzzy styles and `--keep-largest` on single stickers — never on a grid). A checkerboard drawn into the pixels does not count.
- **Outline integrity:** the white outline is closed and uniform around every figure, including between fingers and around hair tips. Repair breaks with `scripts/rebuild_outline.py` instead of re-generating or re-keying; verify the repaired alpha channel afterwards.
- **Cleanliness:** no watermark, logo, stray mark, unexpected person, unwanted text, or gibberish.

Revise the smallest possible area when a single cell fails. Regenerate the full grid only when the identity or style is inconsistent across several cells. Never fix overlap or ghost residue with a second inpainting pass — crop the cell, regenerate it alone, and replace it.

## Cross-style review — only when the user ordered multiple styles

- each pack was generated from the original portrait alone, without the previous pack attached as reference;
- every pack differs visibly from the others in at least three rendering attributes (line work, shading, texture, palette, outline);
- reject results that look like the same render with a color filter or minor glow added, and regenerate that pack with the additional-style template.

## Individual-file review — only after an explicit split request

Do not run the splitting script as part of ordinary generation or master-grid approval. Enter this review stage only when the user explicitly asks for separate, cropped, split, or individually exported files.

After splitting:

- exactly nine PNG files exist;
- each file contains one complete sticker;
- neighboring cells do not leak into the crop;
- the white outline is intact on every side;
- transparent padding is consistent;
- canvas dimensions are consistent;
- filenames follow reading order from top-left to bottom-right;
- every PNG opens successfully and retains an alpha channel.

## Text review

- compare every phrase character by character with the requested copy;
- keep typography consistent across the pack;
- do not cover eyes, mouth, hands, or signature clothing details;
- preserve the approved no-text master separately.
