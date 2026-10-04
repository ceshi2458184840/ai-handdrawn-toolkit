"""Optional vision judge for generated images."""
import os
import json
import re
import urllib.request
import urllib.parse
import base64


def _extract_json(text: str) -> dict:
    """Extract JSON from model output with fallback heuristics."""
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try fenced code block
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Try any {...}
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {"raw": text}


def judge_with_gemini(
    data: bytes,
    api_key: str,
    model: str = "gemini-2.5-flash-image",
    timeout: int = 60,
) -> dict:
    prompt = (
        "You are evaluating a hand-drawn educational illustration. "
        "Score ONLY from 0 to 10 on: 1) handdrawn feel, 2) human sketch quality, "
        "3) clarity of main subject, 4) simplicity, 5) low AI gloss/photorealism. "
        "Return JSON only with keys: handdrawn, human_sketch_quality, clarity, simplicity, ai_glossiness, final. "
        "final should be the overall hand-drawn quality score."
    )
    b64 = base64.b64encode(data).decode()
    # Avoid putting key in URL to reduce leak risk in logs/stack traces
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
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
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read())
    text = result["candidates"][0]["content"]["parts"][0]["text"]
    parsed = _extract_json(text)

    # Normalize to known contract
    final = parsed.get("final")
    handdrawn = parsed.get("handdrawn")
    # Fallback chain: final -> handdrawn -> average of available -> 5
    score = None
    for key in ("final", "handdrawn"):
        val = parsed.get(key)
        if isinstance(val, (int, float)):
            score = float(val)
            break
    if score is None:
        nums = re.findall(r"\d+(?:\.\d+)?", text)
        if nums:
            try:
                score = float(nums[0])
            except Exception:
                score = 5.0
        else:
            score = 5.0
    parsed["final"] = score
    parsed["handdrawn"] = parsed.get("handdrawn", score)
    return parsed
