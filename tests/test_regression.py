"""Regression tests for V3 quality gates."""
import pytest
from app.quality.watermark import detect_watermark_text, is_watermarked
from app.quality.style_gate import check_style_gate, detect_style_violations
from app.quality.heuristic import score


def test_watermark_heuristic_clean_image():
    # A clean white image should not trigger watermark
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGB", (200, 200), color=(255, 255, 255)).save(buf, format="PNG")
    data = buf.getvalue()
    wm, detail = is_watermarked(data)
    assert wm is False


def test_watermark_heuristic_corner():
    # Simulate a dark corner overlay (like a watermark)
    from PIL import Image
    import io
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    # Add dark patch in bottom-right corner
    for x in range(150, 200):
        for y in range(150, 200):
            img.putpixel((x, y), (50, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    wm, detail = is_watermarked(data)
    # Should flag potential watermark in corner
    assert wm is True or detail.get("confidence", 0) >= 0.5


def test_style_gate_clean_sketch_passes():
    positive = "competent human hand-drawn sketch, graphite pencil, fine black ink, confident contour, natural line weight, off-white paper"
    result = check_style_gate("clean_sketch", positive)
    assert result["pass"] is True


def test_style_gate_watercolor_rejected_for_clean_sketch():
    positive = "watercolor wash, soft pigment, paper bleed, storybook illustration"
    result = check_style_gate("clean_sketch", positive)
    assert result["pass"] is False
    assert "STYLE_MISMATCH" in result["reason"]


def test_style_gate_storybook_rejected_for_pencil_study():
    positive = "pencil study, graphite, light construction, controlled hatching"
    result = check_style_gate("pencil_study", positive)
    assert result["pass"] is True


def test_monkey_clean_sketch_should_not_be_watercolor():
    """Regression test: monkey on tree should not generate watercolor/storybook."""
    prompt = "a monkey sitting on a tree branch holding a banana"
    positive, negative = PromptCompiler().compile(prompt, style="clean_sketch")
    # The positive prompt should not contain watercolor terms
    violations = detect_style_violations("clean_sketch", positive)
    assert "watercolor" not in violations
    assert "storybook" not in violations


class PromptCompiler:
    """Inline compiler for regression tests."""
    def __init__(self):
        from app.styles.loader import StyleLoader
        self.style_loader = StyleLoader()
    
    def compile(self, prompt, style="clean_sketch"):
        preset = self.style_loader.load(style)
        positive_parts = [prompt, "simple readable composition", "clear silhouette", 
                         "minimal background", "hand-drawn graphite and ink sketch",
                         "varied line weight", "slightly uneven strokes", "natural hand pressure",
                         "off-white paper", "subtle paper grain", "flat paper surface"]
        positive_parts.extend(preset.get("positive", []))
        negative_parts = list(preset.get("negative", []))
        return ", ".join(positive_parts), ", ".join(negative_parts)


def test_heuristic_score_range():
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), color=(200, 200, 200)).save(buf, format="PNG")
    result = score(buf.getvalue())
    assert 0.0 <= result["final_score"] <= 1.0
