<p align="center">
  <a href="./README.md">🇨🇳 简体中文</a> | <a href="./README_ZH.md">🇨🇳 中文备选</a> | <a href="./README_EN.md">🇬🇧 English</a>
</p>

# 🎨 AI Handdrawn Toolkit — Production Skill

> This document is the English equivalent of [README.md](./README.md).

## Overview

Production-ready AI Agent Skill for Linux / Windows users, supporting CLI pipeline interaction and native MCP Agent Skill protocol. Integrates with cloud text-to-image APIs, featuring a hand-drawn prompt enhancement engine and vectorization post-processing pipeline — one command turns text descriptions into high-quality PNG bitmaps and lossless SVG vectors.

## Core Features

- **Three master hand-drawn styles**: Pencil sketch, architectural pen & ink, vector minimalist
- **Physical texture processing**: Graphite grain, paper texture simulation, removes AI plastic feel
- **High-precision vectorization**: Spline curve fitting, broken-line auto repair
- **Native MCP support**: Direct mount to Claude Desktop or LangChain Agent
- **Pipeline-safe design**: stdout outputs pure JSON only, logs go to stderr

## Quick Start

```bash
pip install -e .

# Basic generation (outputs PNG + SVG)
ai-handdrawn-toolkit --prompt "modern architecture sketch" --style architectural_pen_ink

# Linux pipeline (parse JSON with jq)
ai-handdrawn-toolkit --prompt "wooden chair" --style pencil_sketch | jq .data.svg_path

# Agent MCP deployment (add to Claude Desktop mcp.json):
{
  "mcpServers": {
    "ai-handdrawn-toolkit": {
      "command": "python",
      "args": ["-m", "ai_handdrawn_toolkit.mcp_server"]
    }
  }
}
```

## Repo Structure

```
ai-handdrawn-toolkit/
├── pyproject.toml
├── src/ai_handdrawn_toolkit/
│   ├── cli.py
│   ├── exceptions.py
│   ├── payload.py
│   ├── styles.py
│   ├── shading.py
│   ├── vectorizer.py
│   └── mcp_server.py
├── tests/
├── README.md
├── README_ZH.md
├── README_EN.md
└── SKILL.md
```

## Style Presets

| Style ID | Description | Output |
|---|---|---|
| `pencil_sketch` | Fine graphite pencil sketch | Detailed hatching, graphite texture |
| `architectural_pen_ink` | Master architectural pen & ink | High-contrast lines, building design |
| `vector_minimalist` | Minimalist vector line art | Bold strokes, SVG-optimized |

## Tech Highlights

### Modern Python Project
- `pyproject.toml` single-file build
- `src/` layout isolates dev from runtime
- PEP 621 compliant packaging

### Pipeline Safety
- **stdout** — pure JSON only
- **stderr** — logs and progress
- **exit codes** — POSIX standard

### Agent Native
- manifest.json AI Skill contract
- MCP protocol support
- Claude Desktop native integration

### Defensive Programming
- Unified exception hierarchy
- Pydantic parameter validation
- Retry strategy for transient errors

## CLI Reference

| Argument | Default | Description |
|---|---|---|
| `--prompt` | *required* | Description of the drawing |
| `--style` | `pencil_sketch` | Style preset |
| `--output-dir` | `/tmp` | Output directory |
| `--no-vectorize` | false | Skip vectorization |
| `--no-shading` | false | Skip texture shading |

## Output Contract

```json
{
  "success": true,
  "data": {
    "png_path": "/tmp/sketch_example_pencil_sketch.png",
    "svg_path": "/tmp/sketch_example_pencil_sketch.svg",
    "style_used": "pencil_sketch",
    "enhanced_prompt": "example, detailed graphite pencil sketch..."
  }
}
```

## License

MIT