"""Model Context Protocol (MCP) Server — 原生 Claude Desktop 集成。"""

from pathlib import Path
import httpx
from urllib.parse import quote
from mcp.server.fastmcp import FastMCP
from ai_handdrawn_toolkit.payload import HanddrawnRequestSchema, PayloadBuilder
from ai_handdrawn_toolkit.styles import HANDDRAWN_MASTER_PRESETS
from ai_handdrawn_toolkit.shading import PhysicalTextureShader
from ai_handdrawn_toolkit.vectorizer import HighPrecisionVectorizer

mcp = FastMCP("AI Handdrawn Toolkit Skill")


@mcp.tool()
async def generate_handdrawn_artwork(
    prompt: str, style: str = "pencil_sketch", output_dir: str = "/tmp"
) -> dict:
    """生成高质感 AI 手绘图像并返回位图与无损 SVG 矢量文件路径。

    Args:
        prompt: 手绘内容描述 (例如 "architectural sketch of a modern villa")
        style: 风格 ('pencil_sketch', 'architectural_pen_ink', 'vector_minimalist')
        output_dir: 输出目录（默认 /tmp）

    Returns:
        dict: 包含状态、PNG/SVG 路径和增强 Prompt 的结果
    """
    req = HanddrawnRequestSchema(prompt=prompt, style=style)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"artwork_{abs(hash(prompt)) % 10_000_000}_{style}"
    raw_png = out_dir / f"raw_{base_name}.png"
    shaded_png = out_dir / f"shaded_{base_name}.png"
    svg_path = out_dir / f"{base_name}.svg"

    # Phase 1: 真实 AI 生成
    style_preset = HANDDRAWN_MASTER_PRESETS.get(
        style, HANDDRAWN_MASTER_PRESETS["pencil_sketch"]
    )
    full_prompt = f"{prompt}, {style_preset.positive_prompt}"
    url = f"https://image.pollinations.ai/prompt/{quote(full_prompt)}"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(url, follow_redirects=True)
        if resp.status_code != 200:
            return {"status": "error", "error": f"API returned HTTP {resp.status_code}"}
        raw_png.write_bytes(resp.content)

    # Phase 2: 物理纹理着色
    PhysicalTextureShader.apply_pencil_graphite_effect(raw_png, shaded_png)

    # Phase 3: 矢量化
    HighPrecisionVectorizer.convert_to_svg(shaded_png, svg_path)

    return {
        "status": "success",
        "png_path": str(shaded_png),
        "svg_path": str(svg_path),
        "enhanced_prompt": full_prompt,
    }


if __name__ == "__main__":
    mcp.run()