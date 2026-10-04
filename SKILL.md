# AI Handdrawn Toolkit — Agent Skill Manifest

## Skill Identity
- name: ai-handdrawn
- version: 0.1.0
- entrypoint: python -m app.cli generate <prompt>
- transport: cli (stdio)
- protocol: argument-print

## Capabilities
- generate: Create a hand-drawn style image from a text prompt.
- providers: List available image providers.
- styles: List available style presets.
- doctor: Check environment and configuration.

## Parameters Schema
{
  "prompt": "string (required)",
  "style": "string (optional, default: clean_sketch)",
  "provider": "string (optional, default: auto)",
  "width": "integer (optional, default: 1024)",
  "height": "integer (optional, default: 768)",
  "candidates": "integer (optional, default: 2)",
  "output": "string (optional, default: generated/{style}_{prompt_slice}.png)",
  "output_dir": "string (optional, default: generated/)",
  "config": "string (optional, default: config.yaml)"
}

## Output Contract
- On success (exit 0):
  - stdout: single line with the saved image path
  - stderr: progress logs (candidate pass/reject, scores)
  - sidecar: {output_path}.json with provider/model/style/score/rejected_candidates
- On failure (exit 1):
  - stdout: empty
  - stderr: structured error message
  - no image file written

## Environment Variables
- GEMINI_API_KEY: Google Generative AI key (optional, enables Gemini provider)
- OPENAI_API_KEY: OpenAI API key (optional, enables OpenAI provider)
- CUSTOM_API_KEY: Custom OpenAI-compatible API key (optional)
- CUSTOM_IMAGE_BASE_URL: Custom endpoint base URL (optional)
- CUSTOM_IMAGE_MODEL: Custom model name (optional)

## Installation
pip install -e .

## Notes
- Pollinations provider requires no API key (free fallback).
- All logging goes to stderr; only the final image path goes to stdout.
