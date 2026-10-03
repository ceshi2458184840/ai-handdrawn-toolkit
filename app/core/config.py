"""Configuration loading and validation."""
import os
import yaml
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "default_provider": "auto",
    "generation": {
        "width": 1536,
        "height": 1024,
        "candidates": 2,
        "timeout": 120,
    },
    "style": {
        "default": "clean_sketch",
    },
    "providers": {
        "gemini": {
            "enabled": True,
            "api_key_env": "GEMINI_API_KEY",
            "model": "gemini-2.5-flash-image",
        },
        "openai": {
            "enabled": True,
            "api_key_env": "OPENAI_API_KEY",
            "model": "gpt-image-2.5",
        },
        "flux": {
            "enabled": False,
            "api_key_env": "BFL_API_KEY",
        },
        "pollinations": {
            "enabled": True,
        },
    },
}


class Config:
    def __init__(self, config_path: str | None = None):
        self.config = DEFAULT_CONFIG.copy()
        self._load_config(config_path)
        self._load_env()

    def _load_config(self, path: str | None):
        if path and Path(path).exists():
            with open(path, "r") as f:
                user_config = yaml.safe_load(f)
            self._deep_merge(self.config, user_config)

    def _load_env(self):
        # Load provider API keys from environment
        for provider_name, provider_config in self.config.get("providers", {}).items():
            if "api_key_env" in provider_config:
                env_var = provider_config["api_key_env"]
                if env_var in os.environ:
                    provider_config["api_key"] = os.environ[env_var]

    def _deep_merge(self, base: dict, override: dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @property
    def default_provider(self) -> str:
        return self.get("default_provider", "auto")

    @property
    def default_style(self) -> str:
        return self.get("style.default", "clean_sketch")

    @property
    def candidates(self) -> int:
        return self.get("generation.candidates", 2)

    @property
    def width(self) -> int:
        return self.get("generation.width", 1536)

    @property
    def height(self) -> int:
        return self.get("generation.height", 1024)
