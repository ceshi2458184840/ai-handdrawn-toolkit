# AI 手绘工具包

基于 Linux / macOS / Windows 的手绘风格 AI 插画生成工具。

## 特性

- 多 provider 生图（Gemini、OpenAI 兼容、Pollinations）
- 手绘风格预设 + 质量门禁
- 多候选生成 + 自动评分
- OpenAI 兼容自定义端点
- CLI + Agent Skill Manifest

## 快速开始

```bash
pip install -e .

python -m app.cli generate "一只猫坐在树下" --style clean_sketch

python -m app.cli doctor
```

## Providers

- `auto`: Gemini → OpenAI 兼容 → Pollinations
- `pollinations`: 免费，无需 API key
- `gemini`: 需要 GEMINI_API_KEY
- `openai`: 需要 OPENAI_API_KEY
- `custom`: 需要 CUSTOM_API_KEY + CUSTOM_IMAGE_BASE_URL

## 样式

- clean_sketch
- pencil_study
- ink_sketch
- whiteboard
- classroom
- watercolor
- storybook
- doodle
- colored_handdrawn

## 配置

复制 `config.example.yaml` 为 `config.yaml`，在 `.env` 中设置 API key。

## 许可

MIT

详见 [SKILL.md](SKILL.md) 获取 Agent 集成说明。
