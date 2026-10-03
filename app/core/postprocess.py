"""Lightweight post-processing helpers."""
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import io


def apply_postprocess(data: bytes, mode: str = "none") -> bytes:
    if mode == "none":
        return data
    img = Image.open(io.BytesIO(data)).convert("RGB")
    if mode == "sketch":
        img = img.convert("L").convert("RGB")
        img = img.filter(ImageFilter.FIND_EDGES)
        img = ImageEnhance.Contrast(img).enhance(1.5)
    elif mode == "pencil":
        img = img.convert("L").convert("RGB")
        img = ImageEnhance.Contrast(img).enhance(1.2)
        inv = Image.eval(img, lambda x: 255 - x)
        img = Image.blend(img, inv, 0.3)
    elif mode == "ink":
        img = img.convert("L").convert("RGB")
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = ImageEnhance.Brightness(img).enhance(1.05)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
