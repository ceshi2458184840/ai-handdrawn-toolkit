# AI Handdrawn Toolkit

Natural hand-drawn illustration generation toolkit.

## Features
- Multi-provider image generation (Gemini, OpenAI, FLUX, Pollinations)
- Hand-drawn style presets
- Multi-candidate generation with quality scoring
- Reference image guidance
- Optional image editing
- OpenAI-compatible custom endpoints
- Lightweight post-processing
- CLI

## Quick Start

```bash
pip install -r requirements.txt

# Generate with auto provider fallback
python -m app.cli generate "a cat sitting under a tree" --style clean_sketch

# Old script still works
python scripts/generate_sketch.py "a cat sitting under a tree"

# Check environment
python -m app.cli doctor
```

## Providers

- `auto`: Gemini → OpenAI → FLUX → Pollinations
- `pollinations`: Free, no API key
- `gemini`: Requires GEMINI_API_KEY
- `openai`: Requires OPENAI_API_KEY

## Styles

- clean_sketch
- pencil_sketch
- ink_sketch
- whiteboard
- classroom_doodle
- colored_handdrawn

## Configuration

Copy `config.example.yaml` to `config.yaml` and set API keys in `.env`.

## License

MIT
