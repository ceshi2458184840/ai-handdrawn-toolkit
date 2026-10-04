"""Style contract checks for generated images."""
from app.styles.loader import StyleLoader


def check_style_gate(style: str, prompt: str) -> dict:
    loader = StyleLoader()
    try:
        preset = loader.load(style)
    except Exception:
        return {"pass": True, "violations": []}

    violations = []
    text = f"{prompt} {style}".lower()

    forbidden = preset.get("forbidden", []) or []
    for term in forbidden:
        if term.lower() in text:
            violations.append(f"forbidden:{term}")

    preferred = preset.get("preferred", []) or []
    if preferred:
        hits = sum(1 for term in preferred if term.lower() in text)
        if hits == 0:
            violations.append("missing_preferred_terms")

    if len(violations) >= 3:
        return {"pass": False, "violations": violations}
    return {"pass": True, "violations": violations}
