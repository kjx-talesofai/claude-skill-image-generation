# GPT Image 2

## Usage

1. **Extract the prompt** from the user's request.
2. **Optional**: Identify any reference image URLs the user wants to use.
3. **Optional**: Determine image size. Default is `1024x1024`. The proxy accepts any resolution where max edge ≤ 3840px, both edges are multiples of 16px, and the long:short ratio is ≤ 3:1.
4. **Optional**: Determine image quality. Default is `auto` (model picks the best). You can also set `low` (fast drafts), `medium`, or `high` (best detail, more tokens).
5. **Optional**: Identify any local reference images the user wants to use (see Local Image References below).
6. **Call the script** at `scripts/generate_image.py` with the prompt and any options.

## Script Arguments

```
python scripts/generate_image.py "prompt here" \
  --api-key <key> \
  --size 1024x1024 \
  --quality auto \
  --image https://example.com/ref1.jpg \
  --image https://example.com/ref2.jpg
```

- `prompt` (required): The text description of the image to generate.
- `--api-key`: API key. Falls back to `GPT_IMAGE_API_KEY` env var.
- `--size`: Image dimensions. Default: `1024x1024`.
- `--quality`: Image quality. Choices: `auto` (default), `low`, `medium`, `high`.
- `--image`: Reference image URL. Can be specified multiple times.

## Size and Quality Reference

`gpt-image-2` accepts any resolution in the `size` parameter when it satisfies the constraints below. **Square images are typically fastest to generate.**

**Popular sizes**

| Size | Aspect | Notes |
|---|---|---|
| `1024x1024` | Square | **Fastest to generate**; good default for most use cases |
| `1536x1024` | Landscape | Wider compositions |
| `1024x1536` | Portrait | Taller compositions |
| `2048x2048` | 2K square | Experimental; slower, more tokens |
| `2048x1152` | 2K landscape | Experimental |
| `3840x2160` | 4K landscape | Experimental; max resolution |
| `2160x3840` | 4K portrait | Experimental; max resolution |
| `auto` | — | Default; model picks dimensions |

**Size constraints**

Any custom resolution must satisfy all of the following:
- Maximum edge length ≤ `3840px`
- Both edges must be multiples of `16px`
- Long edge : short edge ratio ≤ `3:1`
- Total pixels between `655,360` and `8,294,400`

> Outputs larger than `2560x1440` (≈ 2K, 3,686,400 pixels) are considered experimental and may take significantly longer.

**Quality options**

| Value | Speed | Cost | When to use |
|---|---|---|---|
| `auto` | Varies | Varies | **Default** — model selects best quality for the prompt |
| `low` | Fastest | Lowest | Fast drafts, thumbnails, and quick iterations. Works well for many common use cases before you move to `medium` or `high` for final assets |
| `medium` | Moderate | Moderate | Balanced quality for general use |
| `high` | Slowest | Highest | Final assets, fine details, photorealistic output |

**Rule of thumb for choosing:**
- User wants a quick preview / draft → `low`
- User wants a balanced result or hasn't specified → `auto` or `medium`
- User wants the best possible quality, fine art, or photorealism → `high`
- User wants a large print or wallpaper → pick a 2K/4K size + `high`

## Local Image References

The base `generate_image.py` script only accepts URLs for reference images. To use **local image files** (e.g. character portraits saved on disk), use the companion script `scripts/generate_image_with_refs.py`:

```
python scripts/generate_image_with_refs.py "prompt here" \
  --quality high \
  --image /path/to/local/portrait1.jpg \
  --image /path/to/local/portrait2.png
```

**How it works:** The wrapper reads local files, base64-encodes them, and sends them as inline `data:image/jpeg;base64,...` URIs in the JSON payload. No cloud upload is required.

**Tip for large files:** Resize/compress local references before sending (e.g. down to ~500px JPEG at quality 55) to keep the request payload small and avoid timeouts.

## Output

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

## URL Stability Note

The proxy may occasionally return a **signed temporary URL** (e.g. `*.volces.com` with long query parameters like `X-Tos-Signature`). These links expire and may not be shareable. **We prefer clean CDN URLs** (e.g. `pro.filesystem.site/...`).

If a signed URL is returned and the user needs a stable link, **re-run the same prompt** — subsequent calls usually route to the clean CDN backend.
