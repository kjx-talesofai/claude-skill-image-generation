# Image Generation CLI

<p align="center">
  <img src="https://camo.githubusercontent.com/3e816c82f93843017c24bcc6cc25a3e8f6becd41c6435e39de4dbc11b0ca1485/68747470733a2f2f6173736574732e687970657273616d706c696e672e636f6d2f68797065722d73616d706c696e672d322e6a7067" alt="hyper-sampling" height="60"/>
  &nbsp;&nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/kjx-talesofai/claude-skill-hypersampling/master/neta_logo.png" alt="neta.art" height="60"/>
</p>

A **Claude Code** skill for generating images via proxy endpoints. Pure stdlib Python 3 — no dependencies.

## Supported Models

- **GPT Image 2** — Photorealistic scenes, high detail. Returns a URL.
- **Gemini Image** (Nano Banana) — Text rendering, infographics, style transfer. Saves to a local file.

## Quick Start

```bash
git clone https://github.com/kjx-talesofai/claude-skill-image-generation.git
cd claude-skill-image-generation
export GPT_IMAGE_API_KEY="your-key-here"
```

> **Security:** Prefer the env var over `--api-key`. CLI arguments leak into shell history and process listings.

## Documentation

- [`SKILL.md`](SKILL.md) — Skill entrypoint with quick start and model selection guide.
- [`references/gpt-image-2.md`](references/gpt-image-2.md) — Full GPT Image 2 reference.
- [`references/gemini-image.md`](references/gemini-image.md) — Full Gemini Image reference.

## License

MIT
