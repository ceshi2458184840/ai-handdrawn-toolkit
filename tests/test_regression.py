"""Regression tests for V3 quality gates."""
import pytest
from app.quality.watermark import detect_watermark_text, is_watermarked
from app.quality.style_gate import check_style_gate
from app.quality.heuristic import score


def test_watermark_heuristic_clean_image():
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGB", (200, 200), color=(255, 255, 255)).save(buf, format="PNG")
    data = buf.getvalue()
    wm, detail = is_watermarked(data)
    assert wm is False


def test_watermark_heuristic_corner():
    from PIL import Image
    import io
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    for x in range(150, 200):
        for y in range(150, 200):
            img.putpixel((x, y), (50, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    wm, detail = is_watermarked(data)
    assert wm is True or detail.get("confidence", 0) >= 0.5


def test_style_gate_clean_sketch_passes():
    positive = "competent human hand-drawn sketch, graphite pencil, fine black ink, confident contour, natural line weight, off-white paper"
    result = check_style_gate("clean_sketch", positive)
    assert result["pass"] is True


def test_style_gate_watercolor_rejected_for_clean_sketch():
    positive = "watercolor wash, soft pigment, paper bleed, storybook illustration"
    result = check_style_gate("clean_sketch", positive)
    assert result["pass"] is False
    assert any("watercolor" in v or "storybook" in v for v in result.get("violations", []))


def test_style_gate_pencil_study_passes():
    positive = "pencil study, graphite, light construction, controlled hatching"
    result = check_style_gate("pencil_study", positive)
    assert result["pass"] is True


def test_monkey_clean_sketch_should_not_be_watercolor():
    prompt = "a monkey sitting on a tree branch holding a banana"
    result = check_style_gate("clean_sketch", prompt)
    assert result["pass"] is True or not any("watercolor" in v for v in result.get("violations", []))


def test_heuristic_score_range():
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), color=(200, 200, 200)).save(buf, format="PNG")
    result = score(buf.getvalue())
    assert 0.0 <= result["final_score"] <= 1.0
