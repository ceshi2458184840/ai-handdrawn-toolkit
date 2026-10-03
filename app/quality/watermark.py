"""Watermark detection for generated images."""
import re
import io
from PIL import Image


def detect_watermark_text(data: bytes) -> dict:
    """Layer 1: Heuristic text detection in corners/edges.
    
    Conservative: only flag if corner has suspicious patterns
    suggesting a logo or text overlay.
    """
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
        w, h = img.size
        corner_size = max(40, min(w, h) // 5)
        corner = img.crop((w - corner_size, h - corner_size, w, h))
        pixels = list(corner.getdata())
        total = len(pixels)
        if total == 0:
            return {"watermark": False, "confidence": 0.0, "method": "none"}
        
        avg_r = sum(p[0] for p in pixels) / total
        avg_g = sum(p[1] for p in pixels) / total
        avg_b = sum(p[2] for p in pixels) / total
        brightness = (avg_r + avg_g + avg_b) / 3.0
        
        variance = sum(
            (p[0] - avg_r) ** 2 + (p[1] - avg_g) ** 2 + (p[2] - avg_b) ** 2
            for p in pixels
        ) / total
        
        # Case 1: very uniform dark patch in corner (solid logo)
        if variance < 30 and brightness < 150:
            return {
                "watermark": True,
                "confidence": 0.7,
                "location": "bottom_right",
                "method": "heuristic_corner_uniform",
            }
        
        # Case 2: moderate variance + mid brightness (text-like)
        if 5 < variance < 300 and 60 < brightness < 230:
            return {
                "watermark": True,
                "confidence": 0.6,
                "location": "bottom_right",
                "method": "heuristic_corner",
            }
    except Exception:
        pass
    return {"watermark": False, "confidence": 0.0, "method": "none"}


def detect_watermark_vision(data: bytes, api_key: str, model: str = "gemini-2.5-flash-image") -> dict:
    """Layer 2: Use vision model to detect watermarks."""
    try:
        import base64
        import json
        import urllib.request
        b64 = base64.b64encode(data).decode()
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        prompt = (
            "Does this image contain a provider watermark, logo, generation badge, "
            "signature, or platform branding in the corners or edges? "
            "Return JSON: {\"watermark\": true/false, \"confidence\": 0.0-1.0, \"location\": \"...\"}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": "image/png", "data": b64}},
                    ]
                }
            ]
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        try:
            return json.loads(text)
        except Exception:
            return {"watermark": False, "confidence": 0.0, "raw": text}
    except Exception:
        return {"watermark": False, "confidence": 0.0, "error": "vision_check_failed"}


def is_watermarked(data: bytes, vision_api_key: str | None = None) -> tuple[bool, dict]:
    """Run watermark detection. Returns (is_watermarked, details)."""
    # Layer 1: heuristic
    text_result = detect_watermark_text(data)
    if text_result.get("watermark") and text_result.get("confidence", 0) >= 0.5:
        return True, text_result
    
    # Layer 2: vision model (if available)
    if vision_api_key:
        vision_result = detect_watermark_vision(data, vision_api_key)
        if vision_result.get("watermark"):
            return True, vision_result
    
    return False, text_result
