#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error

_MAX_REF_SIZE = 5 * 1024 * 1024  # 5 MB

def local_to_data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/png")
    size = os.path.getsize(path)
    if size > _MAX_REF_SIZE:
        raise ValueError(f"Reference image too large: {path} ({size / 1024 / 1024:.1f} MB > {_MAX_REF_SIZE / 1024 / 1024:.0f} MB limit). Resize or compress before sending.")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"

def generate_image(prompt, api_key=None, size="1024x1024", quality="auto", images=None):
    if api_key is None:
        api_key = os.environ.get("GPT_IMAGE_API_KEY")
    if not api_key:
        raise ValueError("API key must be provided via --api-key or GPT_IMAGE_API_KEY env var")
    url = "https://new-api.talesofai.com/v1/images/generations"
    payload = {"model": "gpt-image-2", "prompt": prompt, "size": size, "quality": quality}
    if images:
        payload["image"] = images
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    parser = argparse.ArgumentParser(description="Generate images via GPT Image proxy")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--size", default="1024x1024", help="Image size")
    parser.add_argument(
        "--quality",
        default="auto",
        choices=["auto", "low", "medium", "high"],
        help="Image quality: auto (default), low, medium, or high",
    )
    parser.add_argument("--image", action="append", dest="images", help="Reference image file or URL")
    args = parser.parse_args()
    refs = []
    if args.images:
        for img in args.images:
            if img.startswith("http://") or img.startswith("https://") or img.startswith("data:"):
                refs.append(img)
            elif os.path.isfile(img):
                refs.append(local_to_data_uri(img))
            else:
                print(f"Error: file not found: {img}", file=sys.stderr)
                return 1
    try:
        result = generate_image(args.prompt, args.api_key, args.size, args.quality, refs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
