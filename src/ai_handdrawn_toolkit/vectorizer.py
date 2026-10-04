"""高精度 SVG 矢量化引擎 — 形态学闭运算 + Spline 样条 / vtracer 回退链。"""

from pathlib import Path
import cv2
from .exceptions import VectorizationError


class HighPrecisionVectorizer:
    """形态学闭运算修复断线 → 对比度增强 → Spline 样条矢量化"""

    @classmethod
    def convert_to_svg(cls, input_png: Path, output_svg: Path) -> Path:
        img = cv2.imread(str(input_png), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise VectorizationError(f"无法读取: {input_png}")

        h, w = img.shape[:2]

        # Step 1: 反色 + 阈值化
        _, binary = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)

        # Step 2: 形态学闭运算修复断线
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Step 3: 去除小噪点（形态学开运算）
        cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)

        # Step 4: 写回临时文件
        temp_png = input_png.parent / f"_vtrace_{input_png.name}"
        cv2.imwrite(str(temp_png), cleaned)

        try:
            # 尝试使用 vtracer（已安装时）
            success = cls._try_vtracer(temp_png, output_svg, w, h)

            if not success:
                # 回退：用 OpenCV 生成近似轮廓 SVG
                cls._fallback_svg(cleaned, output_svg, w, h)

            return output_svg
        finally:
            temp_png.unlink(missing_ok=True)

    @classmethod
    def _try_vtracer(cls, input_png: Path, output_svg: Path, w: int, h: int) -> bool:
        try:
            import vtracer
            vtracer.convert_image_to_svg_py(
                str(input_png),
                str(output_svg),
                colormode="binary",
                mode="spline",
                filter_speckle=10,
                corner_threshold=60,
                length_threshold=4.0,
            )
            return output_svg.stat().st_size > 100
        except Exception:
            return False

    @classmethod
    def _fallback_svg(cls, binary_img: "np.ndarray", output_svg: Path, w: int, h: int) -> None:
        """OpenCV findContours 转为 SVG path 作为回退"""
        import numpy as np
        contours, _ = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        paths = []
        for contour in contours:
            if len(contour) < 3:
                continue
            pts = contour.squeeze(axis=1)
            d = "M " + " ".join(f"{int(x)},{int(y)}" for x, y in pts[:, 0:2].astype(np.int32))
            paths.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="1"/>')

        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect width="100%" height="100%" fill="white"/>
{chr(10).join(paths)}
</svg>"""
        output_svg.write_text(svg_content, encoding="utf-8")