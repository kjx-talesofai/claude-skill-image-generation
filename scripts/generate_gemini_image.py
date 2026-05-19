#!/usr/bin/env python3
"""Generate images using Gemini Image API via proxy endpoint."""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error


def _download_image(url: str) -> tuple[str, str]:
    """Download an image from URL and return (mime_type, base64_data)."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
        content_type = resp.headers.get("Content-Type", "image/png")
        mime = content_type.split(";")[0].strip()
        if not mime.startswith("image/"):
            mime = "image/png"
        return mime, base64.b64encode(data).decode("ascii")


def _local_to_data_uri(path: str) -> str:
    """Read a local image file and return a data URI."""
    ext = os.path.splitext(path)[1].lower()
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(ext, "image/png")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _image_to_part(image: str) -> dict:
    """Convert an image string (URL, local path, or data URI) to a Gemini part."""
    if image.startswith("data:"):
        match = re.match(r"data:([^;]+);base64,(.+)", image)
        if not match:
            raise ValueError(f"Invalid data URI: {image[:50]}...")
        mime, data = match.group(1), match.group(2)
        return {"inlineData": {"mimeType": mime, "data": data}}
    elif image.startswith("http://") or image.startswith("https://"):
        mime, data = _download_image(image)
        return {"inlineData": {"mimeType": mime, "data": data}}
    elif os.path.isfile(image):
        mime, data = _local_to_data_uri(image).split(";base64,")
        mime = mime.split(":")[1]
        return {"inlineData": {"mimeType": mime, "data": data}}
    else:
        raise ValueError(f"Image not found: {image}")


def _extract_image_from_text(text: str) -> tuple[bytes, str] | None:
    """Extract base64 image data from markdown image syntax."""
    match = re.search(r"!\[image\]\(data:([^;]+);base64,([^)]+)\)", text)
    if match:
        mime, b64 = match.group(1), match.group(2)
        return base64.b64decode(b64), mime
    return None


def generate_image(
    prompt: str,
    api_key: str | None = None,
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    images: list[str] | None = None,
    output_path: str | None = None,
) -> dict:
    if api_key is None:
        api_key = os.environ.get("GPT_IMAGE_API_KEY")
    if not api_key:
        raise ValueError("API key must be provided via --api-key or GPT_IMAGE_API_KEY env var")

    url = "https://new-api.talesofai.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent"

    parts: list[dict] = [{"text": prompt}]
    if images:
        for img in images:
            parts.append(_image_to_part(img))

    payload: dict = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
        },
    }

    if aspect_ratio or image_size:
        payload["generationConfig"]["responseFormat"] = {
            "image": {},
        }
        if aspect_ratio:
            payload["generationConfig"]["responseFormat"]["image"]["aspectRatio"] = aspect_ratio
        if image_size:
            payload["generationConfig"]["responseFormat"]["image"]["imageSize"] = image_size

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
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e

    # Parse response to extract image
    if not data.get("candidates"):
        raise RuntimeError("No candidates in response")

    candidate = data["candidates"][0]
    content = candidate.get("content", {})
    parts_out = content.get("parts", [])

    image_bytes: bytes | None = None
    image_mime: str = "image/png"

    for part in parts_out:
        if "text" in part:
            result = _extract_image_from_text(part["text"])
            if result:
                image_bytes, image_mime = result
                break
        elif "inline_data" in part or "inlineData" in part:
            inline = part.get("inline_data") or part.get("inlineData")
            image_bytes = base64.b64decode(inline["data"])
            image_mime = inline.get("mime_type") or inline.get("mimeType", "image/png")
            break

    if image_bytes is None:
        raise RuntimeError("No image found in response")

    ext = image_mime.split("/")[-1]
    if ext == "jpeg":
        ext = "jpg"

    if output_path is None:
        timestamp = int(time.time())
        output_path = f"gemini_output_{timestamp}.{ext}"

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return {
        "file_path": output_path,
        "mime_type": image_mime,
        "prompt": prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate images via Gemini Image proxy")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--api-key", help="API key (or set GPT_IMAGE_API_KEY env var)")
    parser.add_argument("--aspect-ratio", help="Aspect ratio, e.g. 1:1, 16:9, 4:3")
    parser.add_argument("--image-size", choices=["512", "1K", "2K", "4K"], help="Image resolution")
    parser.add_argument("--image", action="append", dest="images", help="Reference image (URL or local path, can be used multiple times)")
    parser.add_argument("--output", help="Output file path (default: auto-named)")
    args = parser.parse_args()

    try:
        result = generate_image(
            args.prompt,
            args.api_key,
            args.aspect_ratio,
            args.image_size,
            args.images,
            args.output,
        )
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
