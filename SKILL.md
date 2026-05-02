---
name: gpt-image
description: Generate images using GPT Image 2 via a proxy API endpoint. Trigger when the user says "gpt-image", "use gpt to generate image", "create an image with gpt", or any request to generate, create, draw, or make images using GPT.
---

# GPT Image Generation

Generate images using GPT Image 2 through a proxy endpoint.

## Configuration

Set the `GPT_IMAGE_API_KEY` environment variable with your API key.

> **Security note:** Prefer the environment variable over `--api-key`. CLI arguments are visible in shell history and process listings (`ps`, `top`). Never commit your key to version control.

## Usage

When the user asks to generate an image:

1. **Extract the prompt** from the user's request.
2. **Optional**: Identify any reference image URLs the user wants to use.
3. **Optional**: Determine image size. Default is `1024x1024`. Supported sizes depend on the model; common options include `1024x1024`, `1792x1024`, `1024x1792`.
4. **Optional**: Identify any local reference images the user wants to use (see Local Image References below).
5. **Call the script** at `scripts/generate_image.py` with the prompt and any options.

### Script Arguments

```
python scripts/generate_image.py "prompt here" \
  --api-key <key> \
  --size 1024x1024 \
  --image https://example.com/ref1.jpg \
  --image https://example.com/ref2.jpg
```

- `prompt` (required): The text description of the image to generate.
- `--api-key`: API key. Falls back to `GPT_IMAGE_API_KEY` env var.
- `--size`: Image dimensions. Default: `1024x1024`.
- `--image`: Reference image URL. Can be specified multiple times.

### Local Image References (Optional)

The base `generate_image.py` script only accepts URLs for reference images. To use **local image files** (e.g. character portraits saved on disk), use the companion script `scripts/generate_image_with_refs.py`:

```
python scripts/generate_image_with_refs.py "prompt here" \
  --image /path/to/local/portrait1.jpg \
  --image /path/to/local/portrait2.png
```

**How it works:** The wrapper reads local files, base64-encodes them, and sends them as inline `data:image/jpeg;base64,...` URIs in the JSON payload. No cloud upload is required.

**Tip for large files:** Resize/compress local references before sending (e.g. down to ~500px JPEG at quality 55) to keep the request payload small and avoid timeouts.

### Output

The script prints JSON matching the API response:

```json
{
  "created": 1777704944,
  "data": [
    {
      "revised_prompt": "",
      "url": "https://..."
    }
  ],
  "usage": {
    "total_tokens": 6430,
    "input_tokens": 2255,
    "output_tokens": 4175,
    "input_tokens_details": {
      "text_tokens": 45,
      "image_tokens": 2210
    }
  }
}
```

Present the generated image URL(s) to the user. If the response includes a `revised_prompt`, you may share it as well.

### URL Stability Note

The proxy may occasionally return a **signed temporary URL** (e.g. `*.volces.com` with long query parameters like `X-Tos-Signature`). These links expire and may not be shareable. **We prefer clean CDN URLs** (e.g. `pro.filesystem.site/...`).

If a signed URL is returned and the user needs a stable link, **re-run the same prompt** — subsequent calls usually route to the clean CDN backend.
