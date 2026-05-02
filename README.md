# GPT Image CLI

<p align="center">
  <img src="https://camo.githubusercontent.com/3e816c82f93843017c24bcc6cc25a3e8f6becd41c6435e39de4dbc11b0ca1485/68747470733a2f2f6173736574732e687970657273616d706c696e672e636f6d2f68797065722d73616d706c696e672d322e6a7067" alt="hyper-sampling" height="60"/>
  &nbsp;&nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/kjx-talesofai/claude-skill-hypersampling/master/neta_logo.png" alt="neta.art" height="60"/>
</p>

A **Claude Code** skill for generating images with GPT Image 2 via a proxy endpoint. Includes support for local reference images via base64 data URIs — no cloud upload required.

## Install

```bash
git clone <repo-url>
cd gpt-image
# No pip install needed — pure stdlib Python 3
```

## Configure

Set your API key as an environment variable:

```bash
export GPT_IMAGE_API_KEY="your-key-here"
```

> **Security:** Use the env var. Avoid `--api-key` when possible — CLI arguments leak into shell history and process listings (`ps`, `top`). Never commit your key to version control.

## Usage

### Basic generation

```bash
python scripts/generate_image.py "a cyberpunk cat in neon rain" --size 1024x1024
```

### With reference images (URLs)

```bash
python scripts/generate_image.py "same character, smiling" \
  --image https://example.com/ref1.jpg \
  --image https://example.com/ref2.png
```

### With local reference images

The base script only accepts URLs. Use the companion wrapper for local files:

```bash
python scripts/generate_image_with_refs.py "same character, battle pose" \
  --image ./portraits/serra.jpg \
  --image ./portraits/elena.png
```

**How it works:** The wrapper reads local files, base64-encodes them, and sends them as inline `data:image/jpeg;base64,...` URIs in the JSON payload. No cloud upload required.

**Tip:** Resize/compress large references before sending (e.g. ~500px JPEG at quality 55) to keep the request small. The wrapper rejects files larger than 5 MB.

### Output

```json
{
  "created": 1777704944,
  "data": [
    {
      "revised_prompt": "",
      "url": "https://pro.filesystem.site/cdn/..."
    }
  ],
  "usage": {
    "total_tokens": 6430,
    "input_tokens": 2255,
    "output_tokens": 4175
  }
}
```

### URL stability

The proxy may occasionally return a **signed temporary URL** (e.g. `*.volces.com` with `X-Tos-Signature`). These expire. **We prefer clean CDN URLs** (e.g. `pro.filesystem.site/...`).

If a signed URL is returned, **re-run the same prompt** — subsequent calls usually route to the clean CDN backend.

## License

MIT
