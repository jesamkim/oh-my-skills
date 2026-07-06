# SD3.5 Large API Reference

## Model Information

- **Model ID**: `stability.sd3-5-large-v1:0`
- **API**: InvokeModel (bedrock-runtime) with Stability AI format
- **Region**: us-west-2 (direct invocation only)
- **Cross-Region Inference**: Not supported (no `global.` or `us.` prefix)
- **Content Type**: application/json
- **Accept**: application/json
- **Status**: GA (Generally Available)

## Text-to-Image Request

```json
{
  "prompt": "A red cat sitting on a blue sofa, photorealistic, warm lighting",
  "negative_prompt": "blurry, low quality, distorted",
  "mode": "text-to-image",
  "aspect_ratio": "1:1",
  "seed": 42,
  "output_format": "png"
}
```

## Image-to-Image Request

```json
{
  "prompt": "A watercolor painting of a serene landscape",
  "negative_prompt": "photorealistic, photograph",
  "mode": "image-to-image",
  "image": "<base64-encoded-image>",
  "strength": 0.7,
  "seed": 42,
  "output_format": "png"
}
```

## Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | — | Text description of desired image |
| `negative_prompt` | string | No | — | Elements to exclude from generation |
| `mode` | string | Yes | — | `text-to-image` or `image-to-image` |
| `aspect_ratio` | string | No | `1:1` | Output ratio (text-to-image only) |
| `seed` | int | No | random | 0-4294967294, for reproducibility |
| `output_format` | string | No | `png` | `png` or `jpeg` |
| `image` | string | Conditional | — | Base64 source image (image-to-image only) |
| `strength` | float | No | 0.7 | 0.0-1.0, transformation amount (image-to-image only) |

## Supported Aspect Ratios

| Aspect Ratio | Use Case |
|-------------|----------|
| `1:1` | Social media, icons, square format |
| `16:9` | Presentations, video, widescreen |
| `9:16` | Mobile, stories, portrait video |
| `4:3` | General purpose, classic photo |
| `3:4` | Portrait orientation |
| `2:3` | Portrait photography |
| `3:2` | Landscape photography |
| `21:9` | Ultra-wide, cinematic banners |
| `9:21` | Ultra-tall, vertical banners |

## Response Structure

```json
{
  "images": ["<base64-encoded-png>"],
  "seeds": [42],
  "finish_reasons": [null]
}
```

- `images`: Array of Base64-encoded images (usually 1)
- `seeds`: Array of seeds used for each image
- `finish_reasons`: `null` for success, `"CONTENT_FILTERED"` if blocked

## SDK Configuration Notes

- Set `read_timeout` to at least 120 seconds
- Region must be `us-west-2` (no cross-region inference support)
- Use `Config(read_timeout=120)` with boto3

## Pricing (us-west-2)

SD3.5 Large pricing is per-image:
- Standard resolution: ~$0.04 per image

Check AWS Bedrock pricing page for current rates.
