# SD3.5 Large Prompt Best Practices

## Core Principle

SD3.5 Large uses the MMDiT architecture which understands natural language well.
Prompts should be descriptive captions that paint a vivid picture of the desired image.
Front-load the most important elements since they have the strongest influence.

## Prompt Optimization Rules

### Rule 1: Caption Style Conversion

Convert command-based input to descriptive caption format.

| Input (command) | Output (caption) |
|-----------------|------------------|
| "Make a beautiful sunset" | "A vibrant sunset over mountains, golden rays streaming through pink clouds, low angle shot" |
| "Create a photo of a coffee cup" | "White ceramic coffee cup on wooden table, natural morning light, shallow depth of field, product photography" |

### Rule 2: Six-Element Structure

1. **Subject** (required) - Be specific: "golden retriever" not "a dog"
2. **Environment** (recommended) - "in a modern kitchen", "on a mountain trail"
3. **Pose/Action** (optional) - "standing with arms crossed", "running through rain"
4. **Lighting** (optional) - "soft diffused lighting", "golden hour backlight"
5. **Camera/Framing** (optional) - "low angle", "close-up", "macro", "bokeh"
6. **Style/Medium** (optional) - "photorealistic", "oil painting", "watercolor", "3D render"

### Rule 3: Negative Prompt Separation

Extract negation words from the main prompt and move to `negative_prompt` parameter.

**Negation words**: "no", "not", "without", "except", "excluding",
Korean: "없는", "없이", "빼고", "제외하고", "말고"

| User Input | Prompt | negative_prompt |
|------------|--------|----------------|
| "A fruit basket with no bananas" | "A fruit basket with apples, oranges, and grapes" | "bananas" |
| "사람 없는 해변 사진" | "Pristine sandy beach with turquoise waves, golden sunlight" | "people, humans, figures, crowds" |

### Rule 4: Concrete Language

| Vague | Concrete |
|-------|----------|
| "pretty flower" | "vibrant red roses with morning dewdrops on petals" |
| "nice lighting" | "soft golden hour light casting long warm shadows" |
| "big building" | "towering glass skyscraper reflecting the sunset sky" |

### Rule 5: Korean to English Translation

| Korean Input | English Prompt |
|-------------|----------------|
| "비오는 도시 풍경" | "Rain-soaked urban cityscape at dusk, wet reflections on asphalt, neon signs glowing through rain, cinematic" |
| "따뜻한 카페 내부" | "Cozy cafe interior with warm ambient lighting, wooden furniture, steaming coffee cups, soft afternoon light" |

## Common Negative Prompts

### Quality (recommended default)
"blurry, distorted, low quality, bad anatomy, disfigured, pixelated, noisy, grainy"

### No People
"people, humans, figures, crowds, faces, hands"

### No Text/Watermarks
"text, watermarks, logos, signatures, captions"

### Photorealistic (exclude illustration)
"cartoon, sketch, drawing, anime, illustration, painting"

### Illustration (exclude photo)
"photorealistic, photograph, photo, camera"

## Prompt Templates by Use Case

### Product Photography
"[Product] on [surface], [background], professional product photography, studio lighting, [angle] shot, high resolution"

### Portrait
"[Subject], [setting], [lighting] lighting, [camera angle], editorial photography, sharp focus"

### Landscape
"[Scene], [time of day], [weather], [camera] shot, vivid colors, high detail"

### Concept Art
"[Subject], [art style] style, [color palette], [mood], detailed illustration"

## Image-to-Image Tips

When using image-to-image mode:
- Describe the **desired result**, not the changes you want
- Use `strength` to control transformation amount:
  - 0.1-0.3: Color correction, subtle style change
  - 0.4-0.6: Noticeable style transfer, some structural change
  - 0.7-0.9: Major transformation, composition loosely preserved
- Combine with negative_prompt to exclude unwanted elements from the result
