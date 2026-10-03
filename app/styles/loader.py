"""Style preset loader."""
import yaml
from pathlib import Path
from typing import Any


class StyleLoader:
    def __init__(self, preset_dir: str = "app/styles/presets"):
        self.preset_dir = Path(preset_dir)
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, name: str) -> dict[str, Any]:
        if name in self._cache:
            return self._cache[name]
        path = self.preset_dir / f"{name}.yaml"
        if not path.exists():
            available = [p.stem for p in self.preset_dir.glob("*.yaml")]
            raise ValueError(f"Style '{name}' not found. Available: {available}")
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        self._cache[name] = data
        return data

    def available_styles(self) -> list[str]:
        return [p.stem for p in self.preset_dir.glob("*.yaml")]
