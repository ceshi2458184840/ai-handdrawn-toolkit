"""Provider resolution."""
from app.providers.pollinations import PollinationsProvider
from app.providers.gemini import GeminiProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.core.errors import HanddrawnError, ErrorCode


def resolve_provider(name: str, config):
    name = (name or "auto").lower()
    providers = build_providers(config)
    if name == "auto":
        return providers
    mapping = {p.name: p for p in providers}
    if name not in mapping:
        raise ValueError(f"{name.upper()} provider is not available. Available: {list(mapping.keys())}")
    return [mapping[name]]


def build_providers(config):
    out = []
    prov_cfg = config.get("providers", {})

    def _try_append(provider):
        try:
            out.append(provider)
        except HanddrawnError:
            pass
        except Exception:
            pass

    if prov_cfg.get("pollinations", {}).get("enabled"):
        out.append(PollinationsProvider())
    if prov_cfg.get("gemini", {}).get("enabled"):
        _try_append(GeminiProvider(api_key=(prov_cfg.get("gemini", {}).get("api_key") or "")))
    if prov_cfg.get("openai", {}).get("enabled"):
        _try_append(OpenAICompatibleProvider(api_key=(prov_cfg.get("openai", {}).get("api_key") or ""), base_url=prov_cfg.get("openai", {}).get("base_url"), model=prov_cfg.get("openai", {}).get("model"), name="openai"))
    if prov_cfg.get("custom", {}).get("enabled"):
        c = prov_cfg.get("custom", {})
        _try_append(OpenAICompatibleProvider(api_key=(c.get("api_key") or ""), base_url=c.get("base_url"), model=c.get("model"), name="custom"))
    if not out:
        out.append(PollinationsProvider())
    return out
