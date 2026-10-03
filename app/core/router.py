"""Provider router with auto-fallback chain and quality-aware selection."""
from app.core.errors import HanddrawnError, ErrorCode
from app.providers.pollinations import PollinationsProvider
from app.providers.gemini import GeminiProvider
from app.providers.openai_compatible import OpenAICompatibleProvider


_PROFILES = {
    "gemini": {
        "quality_tier": "high",
        "watermark_risk": "none",
        "supports_reference": True,
        "supports_edit": True,
        "supports_negative": True,
        "multiple_outputs": True,
    },
    "openai": {
        "quality_tier": "high",
        "watermark_risk": "none",
        "supports_reference": False,
        "supports_edit": True,
        "supports_negative": True,
        "multiple_outputs": True,
    },
    "pollinations": {
        "quality_tier": "medium",
        "watermark_risk": "possible",
        "supports_reference": False,
        "supports_edit": False,
        "supports_negative": True,
        "multiple_outputs": False,
    },
}


def build_providers(config, quality_mode: str = "normal"):
    """Build provider list ordered by quality and watermark risk."""
    providers = []
    # Gemini
    gemini_key = config.get("providers.gemini.api_key")
    if gemini_key:
        providers.append(
            GeminiProvider(
                api_key=gemini_key,
                model=config.get("providers.gemini.model", "gemini-2.5-flash-image"),
            )
        )
    # OpenAI-compatible custom endpoint
    custom_key = config.get("providers.custom.api_key")
    custom_url = config.get("providers.custom.base_url")
    custom_model = config.get("providers.custom.model")
    if custom_key and custom_url and custom_model:
        providers.append(
            OpenAICompatibleProvider(
                api_key=custom_key, base_url=custom_url, model=custom_model
            )
        )
    # Pollinations fallback
    if config.get("providers.pollinations.enabled", True):
        providers.append(PollinationsProvider())
    return providers


def resolve_provider(name: str, config):
    if name == "auto":
        return build_providers(config)
    if name == "pollinations":
        return [PollinationsProvider()]
    if name == "gemini":
        key = config.get("providers.gemini.api_key")
        if not key:
            raise HanddrawnError(
                ErrorCode.AUTH_ERROR,
                "Gemini provider selected but GEMINI_API_KEY is missing.",
                "Set GEMINI_API_KEY or use --provider pollinations.",
            )
        return [
            GeminiProvider(
                api_key=key,
                model=config.get("providers.gemini.model", "gemini-2.5-flash-image"),
            )
        ]
    if name == "openai":
        key = config.get("providers.openai.api_key")
        base_url = config.get("providers.openai.base_url", "https://api.openai.com/v1")
        model = config.get("providers.openai.model", "gpt-image-2.5")
        if not key:
            raise HanddrawnError(
                ErrorCode.AUTH_ERROR,
                "OpenAI provider selected but OPENAI_API_KEY is missing.",
                "Set OPENAI_API_KEY.",
            )
        return [OpenAICompatibleProvider(api_key=key, base_url=base_url, model=model)]
    if name == "flux":
        raise HanddrawnError(
            ErrorCode.INVALID_REQUEST,
            "FLUX provider is not implemented yet.",
            "Use pollinations or gemini.",
        )
    raise HanddrawnError(
        ErrorCode.INVALID_REQUEST,
        f"Unknown provider: {name}",
        "Use auto, pollinations, gemini, or openai.",
    )
