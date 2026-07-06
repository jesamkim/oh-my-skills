#!/usr/bin/env python3
"""
Stable Diffusion 3.5 Large Image Generation Script
Supports: text-to-image, image-to-image
Uses Stability AI API format on Amazon Bedrock.
"""

import argparse
import base64
import json
import os
import random
import sys

import boto3
from botocore.config import Config

# Default configuration
MODEL_ID = "stability.sd3-5-large-v1:0"
DEFAULT_REGION = "us-west-2"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_OUTPUT_FORMAT = "png"
DEFAULT_STRENGTH = 0.7

VALID_ASPECT_RATIOS = [
    "1:1", "16:9", "9:16", "4:3", "3:4",
    "2:3", "3:2", "21:9", "9:21"
]


def create_client(region=DEFAULT_REGION):
    """Create Bedrock Runtime client with appropriate timeout."""
    return boto3.client(
        "bedrock-runtime",
        region_name=region,
        config=Config(
            read_timeout=120,
            retries={"max_attempts": 2}
        ),
    )


def encode_image(image_path):
    """Read and Base64-encode an image file."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def save_image(base64_data, output_path):
    """Decode Base64 image data and save to file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    image_bytes = base64.b64decode(base64_data)
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    return output_path


def generate_output_path(output_dir, prefix="sd35l", index=1):
    """Generate a unique output file path."""
    os.makedirs(output_dir, exist_ok=True)
    while os.path.exists(os.path.join(output_dir, f"{prefix}_{index}.png")):
        index += 1
    return os.path.join(output_dir, f"{prefix}_{index}.png")


def main():
    parser = argparse.ArgumentParser(description="SD3.5 Large Image Generation")
    parser.add_argument("--prompt", required=True, help="Text prompt for image generation")
    parser.add_argument("--negative-prompt", help="Negative prompt (elements to exclude)")
    parser.add_argument("--image", help="Input image path (for image-to-image)")
    parser.add_argument("--strength", type=float, default=DEFAULT_STRENGTH,
                        help="Image-to-image strength 0.0-1.0 (default: 0.7)")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO,
                        choices=VALID_ASPECT_RATIOS, help="Output aspect ratio")
    parser.add_argument("--seed", type=int, default=None,
                        help="Seed for reproducibility (0-4294967294)")
    parser.add_argument("--output-format", default=DEFAULT_OUTPUT_FORMAT,
                        choices=["png", "jpeg"], help="Output image format")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")

    args = parser.parse_args()

    # Determine mode
    mode = "image-to-image" if args.image else "text-to-image"

    # Build request
    request_body = {
        "prompt": args.prompt,
        "mode": mode,
        "output_format": args.output_format,
    }

    if args.negative_prompt:
        request_body["negative_prompt"] = args.negative_prompt

    if args.seed is not None:
        request_body["seed"] = args.seed
    else:
        request_body["seed"] = random.randint(0, 4294967294)

    if mode == "text-to-image":
        request_body["aspect_ratio"] = args.aspect_ratio
    elif mode == "image-to-image":
        request_body["image"] = encode_image(args.image)
        request_body["strength"] = args.strength

    seed = request_body["seed"]

    # Invoke model
    client = create_client(args.region)

    print(f"Model: {MODEL_ID}", file=sys.stderr)
    print(f"Mode: {mode}", file=sys.stderr)
    print(f"Seed: {seed}", file=sys.stderr)
    if mode == "text-to-image":
        print(f"Aspect ratio: {args.aspect_ratio}", file=sys.stderr)
    else:
        print(f"Source: {args.image}", file=sys.stderr)
        print(f"Strength: {args.strength}", file=sys.stderr)
    print("Generating image...", file=sys.stderr)

    try:
        response = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Check for content filtering
    finish_reasons = result.get("finish_reasons", [])
    if finish_reasons and finish_reasons[0] == "CONTENT_FILTERED":
        print("Error: Content was filtered by safety system. Please revise your prompt.",
              file=sys.stderr)
        sys.exit(1)

    # Save images
    images = result.get("images", [])
    seeds = result.get("seeds", [])
    saved_paths = []

    for i, img_data in enumerate(images):
        path = generate_output_path(args.output_dir, "sd35l", i + 1)
        save_image(img_data, path)
        saved_paths.append(path)
        print(f"Saved: {path}", file=sys.stderr)

    # Output JSON result to stdout
    output = {
        "model": MODEL_ID,
        "mode": mode,
        "seed": seeds[0] if seeds else seed,
        "images": saved_paths,
        "count": len(saved_paths),
        "finish_reasons": finish_reasons,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
