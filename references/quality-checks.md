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
- **Anatomy:** no extra fingers, merged hands, duplicated limbs, or broken facial features.
- **Separation:** no sticker crosses a cell boundary or touches another sticker; each sticker, including outline, hair, hands, and raised arms, occupies at most 70 percent of its cell.
- **Single figure:** every cell contains exactly one character with exactly one head and one body — no duplicate heads, overlapping figures, or ghost afterimages left by a previous edit.
- **Margins:** every figure and its white outline fit comfortably inside its cell.
- **Transparency:** after keying with `rebuild_outline.py`, corners and spaces between stickers have real alpha transparency and no key-color halo remains along the edges (raise `--chroma-tol` if it does). A checkerboard drawn into the pixels does not count.
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
