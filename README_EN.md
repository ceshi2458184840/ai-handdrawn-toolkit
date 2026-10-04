# AI Handdrawn Toolkit

Natural hand-drawn illustration generation toolkit for Linux / macOS / Windows.

## Features

- Multi-provider image generation (Gemini, OpenAI-compatible, Pollinations)
- Hand-drawn style presets with quality gates
- Multi-candidate generation with scoring
- OpenAI-compatible custom endpoints
- CLI + Agent skill manifest

## Quick Start

```bash
pip install -e .

python -m app.cli generate "a cat sitting under a tree" --style clean_sketch

python -m app.cli doctor
```

## Providers

- `auto`: Gemini → OpenAI-compatible → Pollinations
- `pollinations`: Free, no API key
- `gemini`: Requires GEMINI_API_KEY
- `openai`: Requires OPENAI_API_KEY
- `custom`: Requires CUSTOM_API_KEY + CUSTOM_IMAGE_BASE_URL

## Styles

- clean_sketch
- pencil_study
- ink_sketch
- whiteboard
- classroom
- watercolor
- storybook
- doodle
- colored_handdrawn

## Configuration

Copy `config.example.yaml` to `config.yaml` and set API keys in `.env`.

## License

MIT

See [SKILL.md](SKILL.md) for Agent integration.
