#!/usr/bin/env python3
"""Generate images using Gemini Image API with local reference image support."""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error

_MAX_REF_SIZE = 5 * 1024 * 1024  # 5 MB


def _local_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(ext, "image/png")
    size = os.path.getsize(path)
    if size > _MAX_REF_SIZE:
        raise ValueError(
            f"Reference image too large: {path} ({size / 1024 / 1024:.1f} MB > {_MAX_REF_SIZE / 1024 / 1024:.0f} MB limit). "
            "Resize or compress before sending."
        )
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate images via Gemini Image proxy with local refs")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--api-key", help="API key (or set GPT_IMAGE_API_KEY env var)")
    parser.add_argument("--aspect-ratio", help="Aspect ratio, e.g. 1:1, 16:9, 4:3")
    parser.add_argument(
        "--image-size",
        choices=["512", "1K", "2K", "4K"],
        help="Image resolution",
    )
    parser.add_argument(
        "--image",
        action="append",
        dest="images",
        help="Reference image file or URL (can be used multiple times)",
    )
    parser.add_argument("--output", help="Output file path (default: auto-named)")
    args = parser.parse_args()

    # Import the core function from the base script
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from generate_gemini_image import generate_image

    refs: list[str] = []
    if args.images:
        for img in args.images:
            if img.startswith("http://") or img.startswith("https://") or img.startswith("data:"):
                refs.append(img)
            elif os.path.isfile(img):
                try:
                    refs.append(_local_to_data_uri(img))
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    return 1
            else:
                print(f"Error: file not found: {img}", file=sys.stderr)
                return 1

    try:
        result = generate_image(
            args.prompt,
            args.api_key,
            args.aspect_ratio,
            args.image_size,
            refs,
            args.output,
        )
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
