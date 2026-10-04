"""Configuration loading and validation."""
import os
import copy
import yaml
from pathlib import Path
from app.core.errors import HanddrawnError, ErrorCode


DEFAULT_CONFIG = {
    "default_style": "clean_sketch",
    "width": 1024,
    "height": 768,
    "candidates": 2,
    "providers": {
        "pollinations": {"enabled": True},
        "gemini": {"enabled": True, "api_key_env": "GEMINI_API_KEY"},
        "openai": {"enabled": False, "api_key_env": "OPENAI_API_KEY"},
        "custom": {"enabled": False, "api_key_env": "CUSTOM_API_KEY", "base_url_env": "CUSTOM_IMAGE_BASE_URL", "model_env": "CUSTOM_IMAGE_MODEL"},
    },
}


class Config:
    def __init__(self, path: str = "config.yaml"):
        self._data = copy.deepcopy(DEFAULT_CONFIG)
        self._path = path
        self._load_file(path)
        self._load_env()

    def _load_file(self, path: str):
        p = Path(path)
        if not p.exists():
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                overrides = yaml.safe_load(f) or {}
            self._deep_merge(self._data, overrides)
        except Exception as e:
            raise HanddrawnError(ErrorCode.CONFIG_ERROR, f"Failed to load config: {e}")

    def _load_env(self):
        prov = self._data.setdefault("providers", {})
        for name in ("gemini", "openai", "custom"):
            section = prov.setdefault(name, {})
            key_env = section.pop("api_key_env", None)
            if key_env and not section.get("api_key"):
                section["api_key"] = os.getenv(key_env)
            base_env = section.pop("base_url_env", None)
            if base_env and not section.get("base_url"):
                section["base_url"] = os.getenv(base_env)
            model_env = section.pop("model_env", None)
            if model_env and not section.get("model"):
                section["model"] = os.getenv(model_env)

    def get(self, path: str, default=None):
        parts = path.split(".")
        cur = self._data
        for p in parts:
            if isinstance(cur, dict):
                cur = cur.get(p)
            else:
                return default
            if cur is None:
                return default
        return cur if cur is not None else default

    def to_dict(self):
        return copy.deepcopy(self._data)


def _deep_merge(base: dict, overrides: dict):
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
