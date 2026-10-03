from PIL import Image
import io
from app.quality.heuristic import score


def _make_png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color="white").save(buf, format="PNG")
    return buf.getvalue()


def test_heuristic_returns_score():
    data = _make_png()
    result = score(data)
    assert "final_score" in result
    assert 0.0 <= result["final_score"] <= 1.0
