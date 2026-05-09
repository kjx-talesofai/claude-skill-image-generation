---
name: image-generation
description: Generate images using GPT Image 2 or Gemini Image (Nano Banana) via proxy API endpoints. Trigger when the user says "gpt-image", "gemini-image", "nano banana", "use gpt to generate image", "use gemini to generate image", "create an image with gpt", "create an image with gemini", or any request to generate, create, draw, or make images.
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

## Reference Documents

- [`references/gpt-image-2.md`](references/gpt-image-2.md) — Full GPT Image 2 docs (sizes, quality, local refs, URL stability)
- [`references/gemini-image.md`](references/gemini-image.md) — Full Gemini Image docs (aspect ratios, image sizes, multi-turn editing, capabilities)
