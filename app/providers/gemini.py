"""Gemini image provider (Google Generative Language API)."""
import os
import json
import urllib.request
import urllib.parse
import base64
from typing import List, Optional

from ..providers.base import GeneratedImage, ImageProvider
from ..core.errors import HanddrawnError, ErrorCode


class GeminiProvider(ImageProvider):
    name = "gemini"
    supports_image_input = True
    supports_editing = True

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image"):
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        prompt: str,
        *,
        negative_prompt: str | None = None,
        width: int = 1536,
        height: int = 1024,
        seed: int | None = None,
        reference_images: List[str] | None = None,
        **kwargs,
    ) -> List[GeneratedImage]:
        if not self.api_key:
            raise HanddrawnError(
                ErrorCode.AUTH_ERROR,
                "Gemini API key is missing.",
                "Set GEMINI_API_KEY environment variable.",
            )

        if negative_prompt:
            prompt = f"{prompt}. Avoid: {negative_prompt}."

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent?key={self.api_key}"
        )

        parts = [{"text": prompt}]

        # Add reference images if supported
        if reference_images:
            for img_path in reference_images[:2]:
                with open(img_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                parts.append({
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": img_data,
                    }
                })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
            },
        }

        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                result = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise HanddrawnError(
                ErrorCode.PROVIDER_ERROR,
                f"Gemini HTTP {e.code}: {body[:200]}",
                "Check API key and model name.",
            )
        except Exception as e:
            raise HanddrawnError(
                ErrorCode.NETWORK_ERROR,
                f"Gemini request failed: {e}",
                "Retry or switch provider.",
            )

        images = []
        if "candidates" in result:
            for candidate in result["candidates"]:
                content = candidate.get("content", {})
                for part in content.get("parts", []):
                    if "inlineData" in part:
                        img_bytes = base64.b64decode(part["inlineData"]["data"])
                        images.append(
                            GeneratedImage(
                                data=img_bytes,
                                provider=self.name,
                                model=self.model,
                                width=width,
                                height=height,
                            )
                        )

        if not images:
            raise HanddrawnError(
                ErrorCode.IMAGE_DECODE_ERROR,
                "Gemini returned no images.",
                "Try a different prompt or model.",
            )

        return images
