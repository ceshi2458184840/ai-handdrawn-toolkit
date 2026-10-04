"""CLI 冒烟测试：验证 stdout/stderr 隔离、exit code、输出 JSON schema。"""

import json
import subprocess
import sys
from pathlib import Path


def _run(*args, **kwargs):
    """Helper: run CLI and return CompletedProcess."""
    return subprocess.run(
        [sys.executable, "-m", "ai_handdrawn_toolkit"] + list(args),
        capture_output=True, text=True, timeout=30,
        **kwargs,
    )


def test_cli_help_exits_zero():
    """--help 应返回 exit code 0 并输出帮助信息到 stderr"""
    result = _run("--help")
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower()


def test_cli_output_is_pure_json(tmp_path):
    """正常执行时，stdout 必须只有纯净 JSON，stderr 可有日志"""
    result = _run("--prompt", "test chair sketch", "--style", "pencil_sketch",
                   "--output-dir", str(tmp_path))
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert "png_path" in payload["data"]
    assert Path(payload["data"]["png_path"]).suffix == ".png"
    assert "style_used" in payload["data"]
    assert result.stderr != ""


def test_stdout_no_extra_output(tmp_path):
    """stdout 整段必须是单行 JSON，前后不能有无关文本"""
    result = _run("--prompt", "modern building", "--style", "architectural_pen_ink",
                   "--output-dir", str(tmp_path))
    stdout_lines = [l for l in result.stdout.strip().split("\n") if l]
    for line in stdout_lines:
        parsed = json.loads(line)
        assert "success" in parsed


def test_cli_invalid_style_error(tmp_path):
    """传不存在的 style 应返回 exit code 非0 且 stdout 是 JSON error"""
    result = _run("--prompt", "test", "--style", "nonexistent_style",
                   "--output-dir", str(tmp_path))
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["success"] is False
    assert "error" in payload


def test_no_vectorize_flag(tmp_path):
    """--no-vectorize 应不产出 svg_path"""
    result = _run("--prompt", "simple tree", "--style", "vector_minimalist",
                   "--output-dir", str(tmp_path), "--no-vectorize")
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert "svg_path" not in payload["data"]


def test_no_shading_flag(tmp_path):
    """--no-shading 跳过纹理着色，直接输出原始 PNG"""
    result = _run("--prompt", "line art", "--style", "pencil_sketch",
                   "--output-dir", str(tmp_path), "--no-shading", "--no-vectorize")
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert "png_path" in payload["data"]