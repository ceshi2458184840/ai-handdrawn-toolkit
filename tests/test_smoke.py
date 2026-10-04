"""Smoke test: given valid input, CLI produces a PNG and a JSON without crashing."""
import os
import json
import subprocess
import sys
import tempfile


def test_generate_smoke():
    env = os.environ.copy()
    env.pop("GEMINI_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    env.pop("CUSTOM_API_KEY", None)

    with tempfile.TemporaryDirectory() as tmp:
        out_png = os.path.join(tmp, "out.png")
        meta_path = out_png.rsplit(".", 1)[0] + ".json"
        cmd = [
            sys.executable, "-m", "app.cli", "generate",
            "a simple cat sketch",
            "--style", "clean_sketch",
            "--provider", "pollinations",
            "--output", out_png,
            "--candidates", "1",
        ]
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd="/home/ubuntu/.hermes/cache/scratch/ai-handdrawn-toolkit-work")
        assert proc.returncode == 0, f"CLI failed: {proc.stderr}"
        assert os.path.exists(out_png), "PNG not written"
        assert os.path.getsize(out_png) > 1000, "PNG too small"
        assert os.path.exists(meta_path), f"JSON metadata not written at {meta_path}"
        with open(meta_path, "r") as f:
            meta = json.load(f)
        assert meta["provider"] == "pollinations"
        assert isinstance(meta["style_score"], (int, float))
