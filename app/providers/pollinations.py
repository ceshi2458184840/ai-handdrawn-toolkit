"""Pollinations.ai provider - free, no API key required."""
import urllib.parse
import urllib.request
import time
from typing import List

from ..providers.base import GeneratedImage, ImageProvider


class PollinationsProvider(ImageProvider):
    name = "pollinations"
    supports_image_input = False
    supports_editing = False

    def generate(
        self,
        prompt: str,
        *,
        negative_prompt: str | None = None,
        width: int = 1536,
        height: int = 1024,
        seed: int | None = None,
        reference_images: list[str] | None = None,
        **kwargs,
    ) -> list[GeneratedImage]:
        encoded = urllib.parse.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width={width}&height={height}&nologo=true"
        )
        if seed is not None:
            url += f"&seed={seed}"

        headers = {"User-Agent": "AI-Handdrawn-Toolkit/1.0"}
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                data = resp.read()
        except Exception as e:
            from ..core.errors import HanddrawnError, ErrorCode
            raise HanddrawnError(
                ErrorCode.NETWORK_ERROR,
                f"Pollinations failed: {e}",
                "Check network or try another provider.",
            )

        if len(data) < 1000:
            from ..core.errors import HanddrawnError, ErrorCode
            raise HanddrawnError(
                ErrorCode.PROVIDER_ERROR,
                "Pollinations returned too little data.",
                "Retry or switch provider.",
            )

        return [
            GeneratedImage(
                data=data,
                provider=self.name,
                model="pollinations-default",
                width=width,
                height=height,
                seed=seed,
            )
        ]
