# sd35l - Stable Diffusion 3.5 Large Image Generation

Generate high-quality images using Stability AI SD3.5 Large on Amazon Bedrock.

## Features

- **Text-to-Image**: Generate images from text descriptions with automatic prompt optimization
- **Image-to-Image**: Style transfer and variations from existing images with adjustable strength
- **Negative Prompts**: Fine-grained control over what to exclude from generation
- **9 Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2, 21:9, 9:21
- **Seed Reproducibility**: Deterministic output with seed parameter
- **Korean Support**: Automatic Korean-to-English prompt translation

## Model Details

| Property | Value |
|----------|-------|
| Model | Stability AI SD3.5 Large |
| Model ID | `stability.sd3-5-large-v1:0` |
| Architecture | MMDiT (Multi-Modal Diffusion Transformer) |
| Region | us-west-2 |
| Status | GA (Generally Available) |
| API | InvokeModel (Stability AI format) |

## Usage Examples

### Text-to-Image
```
이미지 만들어: 해질녘 서울 남산타워, 시네마틱 분위기
```

### Image-to-Image (Style Transfer)
```
이 사진을 수채화 스타일로 변환해줘 (strength 0.6)
```

### With Negative Prompt
```
사람 없는 깨끗한 해변 사진 생성해줘
→ prompt: "Pristine sandy beach with turquoise waves"
→ negative_prompt: "people, humans, figures"
```

## Requirements

- AWS account with Amazon Bedrock access
- SD3.5 Large model enabled in us-west-2 region
- Python 3.8+ with boto3

## Installation

```bash
/plugin install sd35l@my-skills
```

## Version History

- **v1.0.0** - Initial release with text-to-image, image-to-image, and prompt optimization

## License

MIT License - See [LICENSE.txt](LICENSE.txt)

## Author

Jesam Kim (jesamkim@gmail.com)
