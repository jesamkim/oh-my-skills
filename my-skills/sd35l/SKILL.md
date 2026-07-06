---
name: sd35l
description: |
  Stable Diffusion 3.5 Large image generation on Amazon Bedrock.
  This skill should be used when the user asks to "generate image", "create image",
  "make image", "draw", "image generation", "stable diffusion", "sd3", "sd35",
  "text to image", "image to image", "style transfer",
  "이미지 생성", "이미지 만들어", "그림 그려", "스타일 변환",
  "사진 만들어", "그림 생성", "SD 이미지".
  Uses Stability AI SD3.5 Large on Amazon Bedrock (us-west-2) — a GA model
  with strong prompt adherence, high-quality photorealistic output, and
  improved text rendering. Supports text-to-image and image-to-image (style
  transfer / variation) with seed-based reproducibility.
license: MIT License
metadata:
    skill-author: jesamkim
    version: 1.0.0
allowed-tools: [Bash, Read, Write, Glob]
---

# sd35l - Stable Diffusion 3.5 Large Image Generation

## Overview

Generate high-quality images using Stability AI SD3.5 Large on Amazon Bedrock.
SD3.5 Large uses the MMDiT (Multi-Modal Diffusion Transformer) architecture,
delivering strong prompt adherence, photorealistic quality, and improved text
rendering over previous Stable Diffusion models.

**Model**: `stability.sd3-5-large-v1:0`
**Region**: us-west-2 (direct invocation, no cross-region inference)
**API**: InvokeModel (bedrock-runtime) with Stability AI format
**Status**: GA (Generally Available)

## Workflow

### Step 1: Analyze User Request

Determine the task type from the user's request:

| User Intent | Mode |
|-------------|------|
| Generate new image from text | `text-to-image` |
| Transform existing image style / create variation | `image-to-image` |

### Step 2: Optimize the Prompt

Transform the user's raw input into an optimized prompt.
Consult `references/prompt_best_practices.md` for the full transformation rules.

Core transformation rules:

1. **Caption style** - Convert commands ("make X", "draw X") to descriptive captions
2. **Six-element structure** - Subject, Environment, Pose/Action, Lighting, Camera, Style
3. **Negative prompt separation** - Extract negation words into `negative_prompt`
4. **Korean to English** - Translate Korean input to English, preserving visual intent
5. **Concrete language** - Replace vague terms with specific visual descriptors

### Step 3: Determine Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| aspect_ratio | 1:1 | Options: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2, 21:9, 9:21 |
| seed | random | 0-4294967294 for reproducibility |
| output_format | png | png or jpeg |
| mode | text-to-image | text-to-image or image-to-image |
| strength | 0.7 | image-to-image only, 0.0-1.0 (higher = more change) |

### Step 4: Present Plan for Confirmation

Before calling the API, show the user:

```
## Image Generation Plan

**Model**: SD3.5 Large
**Optimized Prompt**: [transformed prompt in English]
**Negative Prompt**: [extracted negative elements, if any]
**Aspect Ratio**: 1:1
**Seed**: [random or specified]

Proceed with generation?
```

Wait for user confirmation before proceeding.

### Step 5: Generate Image

Run the generation script:

```bash
python3 ${SKILL_PATH}/scripts/generate_image.py \
  --prompt "optimized prompt here" \
  --negative-prompt "negative elements here" \
  --aspect-ratio 1:1 \
  --seed 42 \
  --output-dir ./output
```

For image-to-image:

```bash
python3 ${SKILL_PATH}/scripts/generate_image.py \
  --prompt "description of desired result" \
  --image path/to/source.png \
  --strength 0.7 \
  --output-dir ./output
```

### Step 6: Present Results

After generation, display the result:
- Show the saved file path
- Show the seed used (for reproducibility)
- Read and display the generated image using the Read tool
- Offer to regenerate with a different seed or adjusted prompt

## Task-Specific Instructions

### Text-to-Image
- Apply the full prompt optimization pipeline
- Default to 1:1 aspect ratio unless user specifies otherwise
- SD3.5 excels with detailed, descriptive prompts — front-load important elements

### Image-to-Image (Style Transfer / Variation)
- Require an existing image path from the user
- `strength` controls how much the output differs from the input:
  - 0.1-0.3: Subtle changes, preserves most of the original
  - 0.4-0.6: Moderate transformation
  - 0.7-0.9: Major changes, only composition preserved
  - 1.0: Completely new image guided only by the prompt
- Describe the desired result in the prompt, not the changes

### Negative Prompts
- Extract negation words from user input into `negative_prompt`
- Common quality negatives: "blurry, distorted, low quality, bad anatomy, disfigured"
- SD3.5 handles negative prompts well — use them to refine output quality

## Additional Resources

### Reference Files

- **`references/prompt_best_practices.md`** - Complete prompt optimization rules, examples, templates
- **`references/api_reference.md`** - SD3.5 Large API parameters and response format

### Scripts

- **`scripts/generate_image.py`** - Main image generation script supporting text-to-image and image-to-image

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Content filter | Prompt triggers safety filter | Revise prompt; check `finish_reasons` for "CONTENT_FILTERED" |
| Access denied | Model not enabled | Enable SD3.5 Large in Bedrock console for us-west-2 |
| Timeout | Generation taking too long | Script sets 120s timeout |
| Invalid aspect ratio | Unsupported ratio | Use one of: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2, 21:9, 9:21 |
