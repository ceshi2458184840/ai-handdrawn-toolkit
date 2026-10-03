"""OpenAI-compatible image provider (works with OpenAI, custom gateways, etc.)."""
import json
import urllib.request
import urllib.error
from typing import List, Optional

from ..providers.base import GeneratedImage, ImageProvider
from ..core.errors import HanddrawnError, ErrorCode


class OpenAICompatibleProvider(ImageProvider):
    name = "openai_compatible"
    supports_image_input = False
    supports_editing = False

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(
        self,
        prompt: str,
        *,
        negative_prompt: str | None = None,
        width: int = 1024,
        height: int = 1024,
        seed: int | None = None,
        reference_images: List[str] | None = None,
        **kwargs,
    ) -> List[GeneratedImage]:
        if not self.api_key:
            raise HanddrawnError(
                ErrorCode.AUTH_ERROR,
                "API key missing for OpenAI-compatible provider.",
                "Set CUSTOM_API_KEY in .env.",
            )

        url = f"{self.base_url}/images/generations"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": kwargs.get("n", 1),
            "size": f"{width}x{height}",
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        data = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                result = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise HanddrawnError(
                ErrorCode.PROVIDER_ERROR,
                f"HTTP {e.code}: {body[:200]}",
                "Check endpoint and model.",
            )
        except Exception as e:
            raise HanddrawnError(
                ErrorCode.NETWORK_ERROR,
                f"Request failed: {e}",
                "Retry or switch provider.",
            )

        images: List[GeneratedImage] = []
        for item in result.get("data", []):
            if "url" in item:
                try:
                    req = urllib.request.Request(item["url"], headers={"User-Agent": "AI-Handdrawn/1.0"})
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        img = resp.read()
                    images.append(
                        GeneratedImage(
                            data=img,
                            provider=self.name,
                            model=self.model,
                            width=width,
                            height=height,
                        )
                    )
                except Exception as e:
                    raise HanddrawnError(
                        ErrorCode.DOWNLOAD_ERROR,
                        f"Failed to download image: {e}",
                        "Check network or provider.",
                    )
            elif "b64_json" in item:
                import base64
                img = base64.b64decode(item["b64_json"])
                images.append(
                    GeneratedImage(
                        data=img,
                        provider=self.name,
                        model=self.model,
                        width=width,
                        height=height,
                    )
                )

        if not images:
            raise HanddrawnError(
                ErrorCode.IMAGE_DECODE_ERROR,
                "Provider returned no images.",
                "Try another provider.",
            )

        return images
