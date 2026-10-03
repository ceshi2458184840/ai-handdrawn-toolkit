"""OpenAI Image provider placeholder."""
from ..providers.base import GeneratedImage, ImageProvider
from ..core.errors import HanddrawnError, ErrorCode


class OpenAIImageProvider(ImageProvider):
    name = "openai"
    supports_image_input = False
    supports_editing = True

    def __init__(self, api_key: str, model: str = "gpt-image-2.5"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt, **kwargs):
        raise HanddrawnError(
            ErrorCode.INVALID_REQUEST,
            "OpenAI Image provider is not implemented yet. Use openai_compatible with base_url https://api.openai.com/v1.",
            "Switch to openai_compatible provider.",
        )
