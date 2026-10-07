# Sticker pack quality checks

## Before generation

- The portrait is sharp enough to identify the face shape, hairstyle, glasses, and clothing.
- The user selected or accepted a style, framing, emotion list, and text preference.
- The source likeness is authorized for the requested use.

## Master-grid review

Inspect at full size:

- **Identity:** all nine cells depict the same person.
- **Consistency:** hairstyle, glasses, clothing, palette, lighting, proportions, and outline match.
- **Expression:** every requested emotion is distinct and in the correct grid position.
- **Anatomy:** no extra fingers, merged hands, duplicated limbs, or broken facial features.
- **Separation:** no sticker crosses a cell boundary or touches another sticker.
- **Margins:** every figure and its white outline fit comfortably inside its cell.
- **Transparency:** corners and spaces between stickers have alpha transparency. A checkerboard drawn into the pixels does not count.
- **Cleanliness:** no watermark, logo, stray mark, unexpected person, unwanted text, or gibberish.

Revise the smallest possible area when a single cell fails. Regenerate the full grid only when the identity or style is inconsistent across several cells.

## Individual-file review

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
