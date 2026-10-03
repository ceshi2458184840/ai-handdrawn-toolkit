"""Style mismatch detection."""
from app.styles.loader import StyleLoader


_STYLE_SIGNALS = {
    "watercolor": ["watercolor", "wash", "pigment", "paper bleed", "soft edge"],
    "storybook": ["storybook", "children's illustration", "soft painted", "picture book"],
    "3d": ["3d render", "CGI", "3d model", "octane", "blender"],
    "photorealistic": ["photorealistic", "photo", "photograph", "DSLR", "realistic"],
    "anime": ["anime", "manga", "cel shading", "thick cel"],
    "glossy": ["glossy", "digital painting", "polished", "cinematic lighting"],
    "doodle": ["doodle", "casual marker", "loose shapes"],
}


def detect_style_violations(requested_style: str, positive_prompt: str) -> list[str]:
    """Detect if the compiled prompt contains forbidden style signals."""
    loader = StyleLoader()
    preset = loader.load(requested_style)
    forbidden = preset.get("forbidden", [])
    positive_lower = positive_prompt.lower()
    violations = []
    for term in forbidden:
        if term.lower() in positive_lower:
            violations.append(term)
    return violations


def check_style_gate(requested_style: str, positive_prompt: str) -> dict:
    """Check if the prompt violates the style contract."""
    violations = detect_style_violations(requested_style, positive_prompt)
    if violations:
        return {
            "pass": False,
            "reason": "STYLE_MISMATCH",
            "violations": violations,
            "requested": requested_style,
        }
    return {"pass": True, "reason": "OK", "violations": []}
