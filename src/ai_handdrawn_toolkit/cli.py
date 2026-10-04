import argparse
import json
import logging
import sys
from pathlib import Path
from typing import NoReturn

from .exceptions import ToolkitError, StyleNotFoundError, ProviderApiError, VectorizationError
from .payload import HanddrawnRequestSchema, PayloadBuilder
from .styles import StyleEngine
from .shading import PhysicalTextureShader
from .vectorizer import HighPrecisionVectorizer

# Configure logging to stderr only
logger = logging.getLogger("ai_handdrawn_toolkit")
logger.setLevel(logging.INFO)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(
    logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
)
logger.addHandler(stderr_handler)


def exit_with_json_error(message: str, code: int = 1) -> NoReturn:
    """向 stderr 打日志，向 stdout 吐统一格式的 JSON Error Payload 并退出"""
    logger.error(message)
    error_payload = {"success": False, "error": message, "exit_code": code}
    sys.stdout.write(json.dumps(error_payload, ensure_ascii=False, indent=2) + "\n")
    sys.stdout.flush()
    sys.exit(code)


def sanitize_filename(prompt: str, style: str, max_length: int = 100) -> str:
    """生成可复现的文件名，避免非法字符"""
    # 移除或替换非法字符
    sanitized = ""
    for char in prompt[:max_length]:
        if char.isalnum() or char in (' ', '-', '_', '.', '~'):
            sanitized += char
        else:
            sanitized += '_'
    # 替换空格为下划线
    sanitized = sanitized.replace(' ', '_')
    # 限制长度并添加样式标识
    return f"sketch_{sanitized[:80]}_{style}.png"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Handdrawn Toolkit - Production CLI & Agent Skill",
        epilog="支持三大利手风格：铅笔素描、建筑钢笔画、极简矢量线稿"
    )
    parser.add_argument("--prompt", type=str, required=True, help="手绘内容描述")
    parser.add_argument(
        "--style",
        type=str,
        default="pencil_sketch",
        choices=["pencil_sketch", "architectural_pen_ink", "vector_minimalist"],
        help="风格预设"
    )
    parser.add_argument("--output-dir", type=str, default="/tmp", help="输出目录")
    parser.add_argument("--no-vectorize", action="store_true", help="禁用矢量化处理，直接输出 PNG")

    args = parser.parse_args()

    try:
        logger.info("初始化高质感手绘渲染管线...")

        # 参数验证与请求构建
        req = HanddrawnRequestSchema(prompt=args.prompt, style=args.style)
        payload = PayloadBuilder(req).build_sd_payload()

        logger.info(f"增强 Prompt: {payload['prompt'][:60]}...")

        # 创建输出目录
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 生成可复现文件名
        filename = sanitize_filename(args.prompt, args.style)
        raw_png = out_dir / f"raw_{filename}"
        shaded_png = out_dir / f"shaded_{filename}"
        svg_path = shaded_png.with_suffix(".svg")

        # 模拟调用云端 API 生成原始线稿位图
        raw_png.write_bytes(b"")

        logger.info("应用物理纸张纹理与石墨着色器...")
        PhysicalTextureShader.apply_pencil_graphite_effect(raw_png, shaded_png)

        result_data = {
            "png_path": str(shaded_png),
            "style_used": args.style,
            "enhanced_prompt": payload["prompt"],
        }

        # 矢量化处理
        if not args.no_vectorize:
            logger.info("执行 Spline 矢量化管线 (PNG -> SVG)...")
            HighPrecisionVectorizer.convert_to_svg(shaded_png, svg_path)
            result_data["svg_path"] = str(svg_path)

        # 核心：纯净 JSON 数据写往 sys.stdout，供 pipeline 读取
        output = {"success": True, "data": result_data}
        sys.stdout.write(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
        sys.stdout.flush()
        sys.exit(0)

    except (ToolkitError, StyleNotFoundError) as err:
        exit_with_json_error(f"参数错误: {str(err)}", code=1)
    except ProviderApiError as err:
        exit_with_json_error(f"云端渲染错误: {str(err)}", code=2)
    except VectorizationError as err:
        exit_with_json_error(f"矢量化处理失败: {str(err)}", code=3)
    except Exception as err:
        logger.exception("致命错误")
        exit_with_json_error(f"执行失败: {str(err)}", code=4)


if __name__ == "__main__":
    main()
