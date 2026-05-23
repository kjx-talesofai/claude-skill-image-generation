---
name: image-generation
description: "Generate images with GPT Image 2 or Gemini Image. Triggers: gpt-image, gemini-image, create image."
---

# Image Generation

Generate images using GPT Image 2 or Gemini Image (Nano Banana) through proxy endpoints.

## Configuration

Set the `GPT_IMAGE_API_KEY` environment variable with your API key.

> **Security note:** Prefer the environment variable over `--api-key`. CLI arguments are visible in shell history and process listings (`ps`, `top`). Never commit your key to version control.

## Quick Start

**GPT Image 2** — returns a URL:

```bash
python scripts/generate_image.py "a cyberpunk cat in neon rain" \
  --size 1024x1024 --quality auto

# With local reference images
python scripts/generate_image_with_refs.py "same character, smiling" \
  --quality high --image ./ref.jpg
```

**Gemini Image** — saves to a local file:

```bash
python scripts/generate_gemini_image.py "a vibrant infographic" \
  --aspect-ratio 16:9 --image-size 2K --output result.png

# With reference images (URL or local path)
python scripts/generate_gemini_image.py "edit this photo" \
  --image ./photo.jpg --output edited.png
```

## Model Selection

Choose the model based on the user's request:

| Model | Best For | Output |
|---|---|---|
| **GPT Image 2** | Photorealistic scenes, high detail, OpenAI-style generation | URL |
| **Gemini Image** | Text rendering, infographics, style transfer, image editing | Local file |

For full parameter tables, size/quality references, and advanced usage, see the reference documents below.

## Execution Model & Expectations

Image generation is a **synchronous long-running POST request**. The script blocks until the API returns the image data.

| Factor | Typical Range |
|---|---|
| Wait time | 2–5 minutes per image |
| Gemini Image size impact | `512`/`1K` faster, `2K`/`4K` slower |
| GPT Image quality impact | `auto`/`low` faster, `high` slower |

The script does not return a task ID — it either succeeds with image data or fails with an error. Use `--submit-only` if the underlying workflow needs fire-and-forget behavior (not supported by current scripts; implement externally if needed).

## Parallel Generation

Submit multiple generation requests in parallel to reduce wall-clock time:

```bash
# Parallel in shell
python scripts/generate_gemini_image.py "character A" --output a.png &
python scripts/generate_gemini_image.py "character B" --output b.png &
python scripts/generate_gemini_image.py "character C" --output c.png &
wait
```

No server-side concurrency limit is enforced for image generation, but do not overwhelm the proxy endpoint.

## Retry Strategy

Failures happen. Common causes and responses:

| Error | Likely Cause | Retry Action |
|---|---|---|
| `HTTP 429` | Rate limited | Wait 30–60 seconds, retry with same prompt |
| `HTTP 500/503` | Server busy | Wait 60 seconds, retry with same prompt |
| `timeout` | Request took too long | Retry with same prompt; for Gemini, try smaller `--image-size` |
| Content policy rejection | Prompt or reference image flagged | Rewrite prompt. For character images, describe as **"fan art of an original character"** or **"original anime-style character"** to distinguish from real persons or protected IP. |

**Always ask the user before retrying** — confirm whether to retry with the same prompt or modify it.

## Reference Documents

- [`references/gpt-image-2.md`](references/gpt-image-2.md) — Full GPT Image 2 docs (sizes, quality, local refs, URL stability)
- [`references/gemini-image.md`](references/gemini-image.md) — Full Gemini Image docs (aspect ratios, image sizes, multi-turn editing, capabilities)
