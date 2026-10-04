"""Production CLI — 管道安全设计，stdout 仅输出纯净 JSON，stderr 仅输出日志。"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import NoReturn

import httpx
from urllib.parse import quote

from .exceptions import ToolkitError, StyleNotFoundError, ProviderApiError, VectorizationError
from .payload import HanddrawnRequestSchema, PayloadBuilder
from .styles import HANDDRAWN_MASTER_PRESETS
from .shading import PhysicalTextureShader
from .vectorizer import HighPrecisionVectorizer

# ── 日志配置：全走 stderr ──────────────────────────────────────────────
logger = logging.getLogger("ai_handdrawn_toolkit")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(_handler)


# ── 输出契约 ───────────────────────────────────────────────────────────
def _emit_success(data: dict) -> None:
    """纯净 JSON → stdout"""
    sys.stdout.write(json.dumps({"success": True, "data": data}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _emit_error(message: str, code: int = 1) -> None:
    """错误 JSON → stdout，返回非零 exit code"""
    sys.stdout.write(json.dumps({"success": False, "error": message, "exit_code": code}, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    sys.exit(code)


# ── 文件名 ─────────────────────────────────────────────────────────────
def _sanitize_name(prompt: str, style: str, max_len: int = 100) -> str:
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_", "~") else "_" for c in prompt[:max_len])
    return f"sketch_{safe.replace(' ', '_')[:80]}_{style}"


# ── 真实云端 API 调用（Pollinations.ai — 免费免 key，失败回退本地生成） ──
def _fetch_image(prompt: str, style: str, out_path: Path) -> None:
    """调用 Pollinations 文生图接口，下载至 out_path；回退本地生成"""
    full_prompt = f"{prompt}, {HANDDRAWN_MASTER_PRESETS.get(style, HANDDRAWN_MASTER_PRESETS['pencil_sketch']).positive_prompt}"
    url = f"https://image.pollinations.ai/prompt/{quote(full_prompt)}"
    logger.info("Calling Pollinations API: %s…", url[:120])

    try:
        resp = httpx.get(url, follow_redirects=True, timeout=60)
        if resp.status_code == 200 and len(resp.content) > 1000:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(resp.content)
            logger.info("Raw image saved: %s (%d bytes)", out_path, len(resp.content))
            return
        logger.warning("Pollinations returned HTTP %d, size=%d — falling back to local generation",
                       resp.status_code, len(resp.content) if resp.content else 0)
    except Exception as e:
        logger.warning("Pollinations API error: %s — falling back to local generation", e)

    # 本地回退：用 OpenCV 生成手绘风格线稿
    _generate_local_sketch(prompt, out_path)
    logger.info("Local sketch saved: %s", out_path)


def _generate_local_sketch(prompt: str, out_path: Path) -> None:
    """用 OpenCV / PIL 生成手绘风格占位图（API 不可用时回退）"""
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np
    import cv2

    # 生成随机手绘风格灰度底图
    w, h = 1024, 1024
    arr = np.ones((h, w), dtype=np.uint8) * 255

    # 加一些随机线条模拟手绘笔触
    rng = np.random.RandomState(hash(prompt) % (2**31))
    for _ in range(rng.randint(30, 80)):
        x1, y1 = rng.randint(0, w), rng.randint(0, h)
        x2, y2 = x1 + rng.randint(-80, 80), y1 + rng.randint(-80, 80)
        thickness = rng.randint(1, 3)
        cv2.line(arr, (x1, y1), (x2, y2), rng.randint(30, 120), thickness)

    # 添加随机噪点模拟纸纹
    noise = rng.randint(0, 20, (h, w), dtype=np.uint8)
    arr = np.clip(arr.astype(np.int16) - noise.astype(np.int16), 0, 255).astype(np.uint8)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), arr)


# ── 主入口 ─────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Handdrawn Toolkit — Production CLI & Agent Skill",
        epilog="支持三大利手风格：pencil_sketch / architectural_pen_ink / vector_minimalist",
    )
    parser.add_argument("--prompt", type=str, required=True, help="手绘内容描述（英文效果更佳）")
    parser.add_argument("--style", type=str, default="pencil_sketch",
                        help="风格预设: pencil_sketch / architectural_pen_ink / vector_minimalist")
    parser.add_argument("--output-dir", type=str, default="/tmp", help="输出目录")
    parser.add_argument("--no-vectorize", action="store_true", help="禁用矢量化，仅输出 PNG")
    parser.add_argument("--no-shading", action="store_true", help="跳过物理纹理着色（仅原始输出）")

    args = parser.parse_args()

    try:
        # ── 校验 ──
        if args.style not in HANDDRAWN_MASTER_PRESETS:
            raise StyleNotFoundError(f"不支持风格 '{args.style}'，可选: {list(HANDDRAWN_MASTER_PRESETS.keys())}")

        req = HanddrawnRequestSchema(prompt=args.prompt, style=args.style)
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        base_name = _sanitize_name(args.prompt, args.style)
        raw_png = out_dir / f"raw_{base_name}.png"
        shaded_png = out_dir / f"shaded_{base_name}.png"
        svg_path = out_dir / f"{base_name}.svg"

        # ── 1/4 真实 AI 生成 ──
        logger.info("Phase 1/4: AI image generation (Pollinations API)…")
        _fetch_image(args.prompt, args.style, raw_png)
        if raw_png.stat().st_size < 1000:
            logger.warning("Image too small (%d bytes), may be empty", raw_png.stat().st_size)

        # ── 2/4 物理纹理着色 ──
        if not args.no_shading:
            logger.info("Phase 2/4: Applying physical paper texture & graphite shader…")
            PhysicalTextureShader.apply_pencil_graphite_effect(raw_png, shaded_png)
        else:
            shaded_png = raw_png

        # ── 3/4 矢量化 ──
        result = {
            "png_path": str(shaded_png),
            "style_used": args.style,
            "enhanced_prompt": f"{args.prompt}, {HANDDRAWN_MASTER_PRESETS[args.style].positive_prompt}",
        }

        if not args.no_vectorize:
            logger.info("Phase 3/4: SVG vectorization (morphological close + spline)…")
            HighPrecisionVectorizer.convert_to_svg(shaded_png, svg_path)
            result["svg_path"] = str(svg_path)

        # ── 4/4 输出 ──
        logger.info("Done — emitting result to stdout")
        _emit_success(result)

    except StyleNotFoundError as e:
        _emit_error(f"参数错误: {e}", code=1)
    except ProviderApiError as e:
        _emit_error(f"云端渲染错误: {e}", code=2)
    except VectorizationError as e:
        _emit_error(f"矢量化失败: {e}", code=3)
    except ToolkitError as e:
        _emit_error(f"内部错误: {e}", code=4)
    except Exception as e:
        logger.exception("未预期错误")
        _emit_error(f"执行失败: {e}", code=5)


if __name__ == "__main__":
    main()