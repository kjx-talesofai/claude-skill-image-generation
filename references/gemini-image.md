# Gemini Image (Nano Banana)

## Usage

1. **Extract the prompt** from the user's request.
2. **Optional**: Determine aspect ratio. Default is model-dependent (typically `1:1`).
3. **Optional**: Determine image size/resolution. Default is `1K` (1024x1024 for 1:1). Choices: `512`, `1K`, `2K`, `4K`.
4. **Optional**: Identify any reference images (local files or URLs) the user wants to use.
5. **Call the script** at `scripts/generate_gemini_image.py` with the prompt and any options.

## Script Arguments

```
python scripts/generate_gemini_image.py "prompt here" \
  --api-key <key> \
  --aspect-ratio 16:9 \
  --image-size 2K \
  --image https://example.com/ref1.jpg \
  --image ./local/ref2.png \
  --output ./my_image.jpg
```

- `prompt` (required): The text description of the image to generate.
- `--api-key`: API key. Falls back to `GPT_IMAGE_API_KEY` env var.
- `--aspect-ratio`: Aspect ratio. See table below for supported values.
- `--image-size`: Image resolution. Choices: `512`, `1K` (default), `2K`, `4K`.
- `--image`: Reference image (URL or local path). Can be specified multiple times.
- `--output`: Output file path. Default: auto-named (`gemini_output_{timestamp}.{ext}`).

## Aspect Ratio and Image Size Reference

**Supported aspect ratios**

| Ratio | Description |
|---|---|
| `1:1` | Square (default) |
| `16:9` | Widescreen / landscape |
| `4:3` | Standard landscape |
| `3:2` | Photo landscape |
| `3:4` | Standard portrait |
| `2:3` | Photo portrait |
| `9:16` | Vertical / mobile |
| `5:4` | Classic photo |
| `4:5` | Portrait photo |
| `21:9` | Ultrawide |
| `1:4` | Tall vertical (Gemini 3.1 Flash only) |
| `4:1` | Wide banner (Gemini 3.1 Flash only) |
| `1:8` | Very tall (Gemini 3.1 Flash only) |
| `8:1` | Very wide (Gemini 3.1 Flash only) |

**Image size options**

| Size | Description | Typical dimensions (1:1) |
|---|---|---|
| `512` | Small, fast | 512x512 (Gemini 3.1 Flash only) |
| `1K` | Default, balanced | 1024x1024 |
| `2K` | High resolution | 2048x2048 |
| `4K` | Max resolution | 4096x4096 |

> **Note:** Higher resolutions (`2K`, `4K`) take longer to generate and consume more tokens. For Gemini 3.1 Flash Image, the default resolution is `1K`.

**When to use:**
- User wants a quick draft / icon / thumbnail → `512` or `1K`
- User wants a balanced result or hasn't specified → `1K`
- User wants high detail, print-quality, or wallpaper → `2K` or `4K`
- User wants a specific composition → pick an appropriate aspect ratio

## Reference Images

The base `generate_gemini_image.py` script directly accepts both **URLs** and **local file paths** for reference images. Each `--image` argument can be:

- A URL (`https://...`)
- A local file path (`./portrait.jpg`)
- A data URI (`data:image/jpeg;base64,...`)

```
python scripts/generate_gemini_image.py "same character, battle pose" \
  --aspect-ratio 3:4 \
  --image-size 2K \
  --image ./portraits/serra.jpg \
  --image ./portraits/elena.png
```

**How it works:** Images are base64-encoded and sent as inline `inline_data` parts in the Gemini native API payload. No cloud upload is required.

**Tip for large files:** Resize/compress local references before sending (e.g. down to ~500px JPEG at quality 55) to keep the request payload small and avoid timeouts. The wrapper script `generate_gemini_image_with_refs.py` enforces a 5 MB limit per reference image.

## Local Image References Wrapper

For convenience, use `scripts/generate_gemini_image_with_refs.py` which provides the same interface but with explicit file-size validation (rejects files > 5 MB):

```
python scripts/generate_gemini_image_with_refs.py "same character, smiling" \
  --aspect-ratio 1:1 \
  --image-size 1K \
  --image ./portraits/serra.jpg
```

## Output

Unlike GPT Image (which returns a URL), Gemini Image returns the image as **base64-encoded inline data**. The script automatically decodes and saves it to a local file.

The script prints JSON:

```json
{
  "file_path": "gemini_output_1778312169.jpg",
  "mime_type": "image/jpeg",
  "prompt": "a simple blue circle on white background"
}
```

**Important:**
- `file_path` is the path where the image was saved. If `--output` was provided, this is the exact path specified. If auto-named, the extension is derived from the API-returned `mime_type`.
- `mime_type` is the actual image format returned by the API, which may differ from the file extension. For example, if you specify `--output result.png` but the API returns `image/jpeg`, the file is saved as `result.png` but `mime_type` reports `image/jpeg`. The file content is always the correct binary data.

Present the generated image file path to the user. You can describe what was generated.

## Multi-turn Image Editing

Gemini Image supports conversational image editing. After generating an initial image, you can pass it back as a reference in subsequent calls to iterate:

```
# First generation
python scripts/generate_gemini_image.py "a vibrant infographic about photosynthesis" \
  --aspect-ratio 16:9 --image-size 2K --output photosynthesis.png

# Follow-up edit
python scripts/generate_gemini_image.py "Update this infographic to be in Spanish. Do not change any other elements." \
  --image ./photosynthesis.png --output photosynthesis_es.png
```

## Cross-Skill Workflow: Image → Video

Gemini Image outputs local files, which can be used directly with the **video-generation** skill's `--image` parameter (auto-converted to data URI). For `--first-frame`, `--last-frame`, and `--reference-image`, upload to a public URL first.

```bash
# Generate with Gemini
python scripts/generate_gemini_image.py "a warrior in a dark forest" \
  --aspect-ratio 16:9 --output warrior.png

# Pass directly to video-generation --image (local file supported)
python ../video-generation/scripts/generate_video.py "slow pan across the warrior" \
  --image ./warrior.png --model seedance-2-0
```

## Model Capabilities

- **Text rendering:** Excellent at generating legible, stylized text for infographics, menus, and logos.
- **Style transfer:** Can recreate content in different artistic styles (e.g. "Transform this photo into Van Gogh style").
- **Inpainting:** Can modify specific parts of an image while keeping the rest unchanged.
- **Up to 14 reference images:** Mix multiple reference images for complex compositions.
