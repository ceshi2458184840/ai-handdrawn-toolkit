"""OpenAI-compatible image provider."""
import json
import base64
import urllib.request
import urllib.error
from typing import List, Optional

from ..providers.base import GeneratedImage, ImageProvider
from ..core.errors import HanddrawnError, ErrorCode


class OpenAICompatibleProvider(ImageProvider):
    name = "openai_compatible"
    supports_image_input = False
    supports_editing = False

    def __init__(self, api_key: str, base_url: Optional[str] = None, model: Optional[str] = None, name: str = "openai_compatible"):
        self.name = name
        self.api_key = api_key
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.model = model or "gpt-image-1"

    def generate(self, prompt: str, *, negative_prompt: str | None = None, width: int = 1024, height: int = 1024, seed: int | None = None, reference_images: List[str] | None = None, **kwargs) -> List[GeneratedImage]:
        if not self.api_key:
            raise HanddrawnError(ErrorCode.AUTH_ERROR, "API key missing for OpenAI-compatible provider.", "Set API key in config or env.")

        url = f"{self.base_url}/images/generations"
        payload = {
            "model": self.model,
            "prompt": prompt + (f" Avoid: {negative_prompt}." if negative_prompt else ""),
            "n": 1,
            "size": f"{width}x{height}",
        }
        if seed is not None:
            payload["seed"] = seed
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                result = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise HanddrawnError(ErrorCode.PROVIDER_ERROR, f"HTTP {e.code}: {body[:200]}", "Check API key/endpoint/model.")
        except Exception as e:
            raise HanddrawnError(ErrorCode.NETWORK_ERROR, str(e), "Retry later.")

        items = result.get("data", [])
        out = []
        for item in items:
            if item.get("b64_json"):
                out.append(GeneratedImage(base64.b64decode(item["b64_json"]), provider=self.name, model=self.model))
            elif item.get("url"):
                try:
                    with urllib.request.urlopen(item["url"], timeout=60) as r:
                        out.append(GeneratedImage(r.read(), provider=self.name, model=self.model))
                except Exception:
                    pass
        if not out:
            raise HanddrawnError(ErrorCode.PROVIDER_ERROR, "Empty image response", "Model may not support this endpoint.")
        return out
