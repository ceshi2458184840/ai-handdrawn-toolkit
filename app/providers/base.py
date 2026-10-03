"""Base provider class for image generation."""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class GeneratedImage:
    """Represents a generated image."""
    data: bytes
    provider: str
    model: str
    width: int
    height: int
    seed: int | None = None
    metadata: dict | None = None


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    name: str = "base"
    supports_image_input: bool = False
    supports_editing: bool = False

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        negative_prompt: str | None = None,
        width: int = 1024,
        height: int = 1024,
        seed: int | None = None,
        reference_images: list[str] | None = None,
        **kwargs,
    ) -> list[GeneratedImage]:
        """Generate one or more images."""
        raise NotImplementedError

    def capabilities(self) -> dict:
        """Return provider capabilities."""
        return {
            "text_to_image": True,
            "image_input": self.supports_image_input,
            "editing": self.supports_editing,
        }
