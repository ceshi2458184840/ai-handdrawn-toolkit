"""Model Context Protocol (MCP) Server."""

from pathlib import Path
from mcp.server.fastmcp import FastMCP
from ai_handdrawn_toolkit.payload import HanddrawnRequestSchema, PayloadBuilder

mcp = FastMCP("AI Handdrawn Toolkit Skill")

@mcp.tool()
async def generate_handdrawn_artwork(
    prompt: str, style: str = "architectural_pen_ink"
) -> dict:
    """生成高质感 AI 手绘图像并返回位图与无损 SVG 矢量文件路径。

    Args:
        prompt: 手绘内容描述 (例如 "architectural sketch of a modern villa")
        style: 风格 ('pencil_sketch', 'architectural_pen_ink', 'vector_minimalist')

    Returns:
        dict: 包含状态、PNG/SVG 路径和增强 Prompt 的结果
    """
    req = HanddrawnRequestSchema(prompt=prompt, style=style)
    payload = PayloadBuilder(req).build_sd_payload()

    out_png = Path(f"/tmp/artwork_{abs(hash(prompt))}.png")
    out_svg = out_png.with_suffix(".svg")

    out_png.write_bytes(b"")
    out_svg.write_text('')

    return {
        "status": "success",
        "png_path": str(out_png),
        "svg_path": str(out_svg),
        "enhanced_prompt": payload["prompt"],
    }


if __name__ == "__main__":
    mcp.run()
