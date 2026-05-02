#!/usr/bin/env python3
"""Generate images using GPT Image API via proxy endpoint."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def generate_image(prompt: str, api_key: str | None = None, size: str = "1024x1024", images: list[str] | None = None) -> dict:
    if api_key is None:
        api_key = os.environ.get("GPT_IMAGE_API_KEY")
    if not api_key:
        raise ValueError("API key must be provided via --api-key or GPT_IMAGE_API_KEY env var")

    url = "https://new-api.talesofai.com/v1/images/generations"
    payload: dict = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "size": size,
    }
    if images:
        payload["image"] = images

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate images via GPT Image proxy")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--api-key", help="API key (or set GPT_IMAGE_API_KEY env var)")
    parser.add_argument("--size", default="1024x1024", help="Image size (default: 1024x1024)")
    parser.add_argument("--image", action="append", dest="images", help="Reference image URL (can be used multiple times)")
    args = parser.parse_args()

    try:
        result = generate_image(args.prompt, args.api_key, args.size, args.images)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
