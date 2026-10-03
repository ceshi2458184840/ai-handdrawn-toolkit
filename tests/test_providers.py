import pytest

def test_pollinations_import():
    from app.providers.pollinations import PollinationsProvider
    assert PollinationsProvider.name == "pollinations"

def test_gemini_missing_key():
    from app.providers.gemini import GeminiProvider
    from app.core.errors import HanddrawnError, ErrorCode
    p = GeminiProvider(api_key="")
    with pytest.raises(HanddrawnError) as exc:
        p.generate("test")
    assert exc.value.code == ErrorCode.AUTH_ERROR

def test_openai_compatible_import():
    from app.providers.openai_compatible import OpenAICompatibleProvider
    p = OpenAICompatibleProvider(api_key="k", base_url="http://localhost/v1", model="m")
    assert p.name == "openai_compatible"
