"""Optional vision judge for generated images."""
import os
import json
import urllib.request
import urllib.parse
import base64


def judge_with_gemini(data: bytes, api_key: str, model: str = "gemini-2.5-flash-image") -> dict:
    prompt = (
        "You are evaluating a hand-drawn educational illustration. "
        "Score the image from 0 to 10 on: 1) does it look hand-drawn, 2) does it look like a competent human sketch, "
        "3) is the main subject immediately understandable, 4) is the composition clean, 5) is the background simple, "
        "6) does it avoid glossy AI-art aesthetics, 7) does it avoid photorealism/3D/anime, "
        "8) are the lines natural rather than mechanically perfect. Return JSON only with keys: handdrawn, human_sketch_quality, clarity, simplicity, ai_glossiness, composition, final."
    )
    b64 = base64.b64encode(data).decode()
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
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
        return {"raw": text}
