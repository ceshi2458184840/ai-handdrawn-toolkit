"""FLUX provider placeholder."""
from ..providers.base import GeneratedImage, ImageProvider
from ..core.errors import HanddrawnError, ErrorCode


class FLUXProvider(ImageProvider):
    name = "flux"
    supports_image_input = False
    supports_editing = False

    def generate(self, prompt, **kwargs):
        raise HanddrawnError(
            ErrorCode.INVALID_REQUEST,
            "FLUX provider is not implemented yet. Use pollinations or gemini.",
            "Switch to pollinations provider.",
        )
