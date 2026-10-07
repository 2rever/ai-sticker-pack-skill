# Prompt templates

Replace bracketed fields with facts from the portrait and the user's choices. Do not leave brackets in a production prompt.

## Base no-text grid

```text
Use the attached portrait as the identity reference. Preserve the person's [face shape], [hairstyle], [glasses or other distinctive feature], facial proportions, and [clothing]. Create a 3x3 grid containing nine independent Q-style stickers in a consistent [style preset] art direction.

The nine emotions, from left to right and top to bottom, are: [emotion 1], [emotion 2], [emotion 3], [emotion 4], [emotion 5], [emotion 6], [emotion 7], [emotion 8], and [emotion 9]. Make each pose visibly different while keeping the same person, hairstyle, clothing, proportions, palette, lighting, and rendering style in every cell.

Each sticker must be complete, centered, isolated from neighboring cells, surrounded by the same thick white sticker outline, and placed on a genuinely transparent background. Leave generous transparent spacing around every sticker. Do not add text, gibberish, watermarks, logos, extra people, repeated poses, cropped heads, cropped hands, or overlapping cells.
```

## Targeted cell revision

```text
Preserve the other eight cells exactly as they are. Change only the [position] cell to [new emotion/action]. Keep the same identity, face shape, hairstyle, glasses, clothing, proportions, palette, lighting, white sticker outline, transparent background, and overall art direction. Do not alter the grid layout or any other cell.
```

## Text pass

```text
Create a text version from the approved no-text sticker pack. Preserve every character and pose. Add only these short phrases in the corresponding cells: [phrases]. Use one consistent, legible rounded type style, keep the words outside the face and hands, and retain the transparent background and white sticker outline. Do not change the character design. Render every Chinese character exactly as written.
```

## Full-body source for a future desktop pet

```text
Using the approved sticker character as reference, create one neutral full-body turnaround-ready character on a genuinely transparent background. Preserve the same face, hairstyle, glasses, clothing, palette, and art direction. Show the complete body and feet with comfortable transparent margins. Use a relaxed standing pose suitable for later idle, walking, sleeping, and interaction animation states. Do not add text, props, scenery, or a platform shadow.
```
