"""Heuristic quality scoring for generated images."""
from PIL import Image
import io


def score(data: bytes) -> dict:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    pixels = list(img.getdata())
    w, h = img.size
    total = w * h

    unique_colors = len(set(pixels))
    colorfulness = unique_colors / 65536.0

    # simple background simplicity: count near-white pixels
    white_count = sum(1 for r, g, b in pixels if r > 240 and g > 240 and b > 240)
    background_simplicity = white_count / total if total else 0.0

    # artifact penalty: very small or very flat images
    artifact_penalty = 0.0
    if total < 512 * 512:
        artifact_penalty += 0.3
    if unique_colors < 20:
        artifact_penalty += 0.2

    simplicity = max(0.0, min(1.0, background_simplicity))
    handdrawn = max(0.0, min(1.0, 1.0 - colorfulness + 0.3))

    final = round(
        max(0.0, min(1.0, (handdrawn * 0.4 + simplicity * 0.4 + (1 - artifact_penalty) * 0.2))),
        2,
    )
    return {
        "composition": round(handdrawn, 2),
        "simplicity": round(simplicity, 2),
        "handdrawn": round(handdrawn, 2),
        "artifact_penalty": round(artifact_penalty, 2),
        "final_score": final,
    }
