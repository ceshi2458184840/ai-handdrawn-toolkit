"""Prompt compiler: builds positive/negative prompts from style presets."""
from app.styles.loader import StyleLoader


_COMPOSITION = [
    "simple readable composition",
    "clear silhouette",
    "main subject centered or intentionally offset",
    "minimal background",
]

_MEDIUM = {
    "clean_sketch": "hand-drawn graphite and ink sketch",
    "pencil_sketch": "pencil sketch, graphite shading",
    "ink_sketch": "black ink line drawing",
    "whiteboard": "whiteboard marker drawing",
    "classroom_doodle": "classroom hand-drawn illustration",
    "colored_handdrawn": "hand-drawn colored illustration",
}

_LINE_QUALITY = [
    "varied line weight",
    "slightly uneven strokes",
    "natural hand pressure",
    "occasional construction lines",
    "subtle wobble",
    "organic contours",
]

_PAPER = [
    "off-white paper",
    "subtle paper grain",
    "flat paper surface",
]


class PromptCompiler:
    def __init__(self, style_loader: StyleLoader | None = None):
        self.style_loader = style_loader or StyleLoader()

    def compile(
        self,
        prompt: str,
        style: str = "clean_sketch",
        aspect_ratio: str | None = None,
    ) -> tuple[str, str]:
        preset = self.style_loader.load(style)
        positive_parts = [prompt]
        positive_parts.extend(_COMPOSITION)
        positive_parts.append(_MEDIUM.get(style, "hand-drawn sketch"))
        positive_parts.extend(_LINE_QUALITY)
        positive_parts.extend(_PAPER)
        positive_parts.extend(preset.get("positive", []))

        negative_parts = list(preset.get("negative", []))

        positive = ", ".join(positive_parts)
        negative = ", ".join(negative_parts) if negative_parts else ""
        return positive, negative
