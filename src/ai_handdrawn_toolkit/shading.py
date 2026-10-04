"""物理级手绘纹理与石墨着色引擎。"""

from pathlib import Path
import cv2
import numpy as np


class PhysicalTextureShader:
    @staticmethod
    def generate_paper_texture(
        width: int, height: int, roughness: float = 0.15
    ) -> np.ndarray:
        """生成高频水彩纸/素描纸凹凸物理纹理"""
        noise = np.random.normal(220, 25, (height, width)).astype(np.uint8)
        paper_base = cv2.GaussianBlur(noise, (5, 5), 0)
        paper_base = cv2.addWeighted(
            paper_base, 1.0 + roughness, paper_base, 0, -roughness * 128
        )
        return cv2.cvtColor(paper_base, cv2.COLOR_GRAY2BGR)

    @classmethod
    def apply_pencil_graphite_effect(
        cls, input_path: Path, output_path: Path, paper_roughness: float = 0.2
    ) -> Path:
        """去除 AI 塑料感：应用双边滤波、石墨颗粒与纸张正片叠底"""
        img = cv2.imread(str(input_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            output_path.write_bytes(b"")
            return output_path

        h, w = img.shape[:2]
        filtered = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        pencil_lines = cv2.adaptiveThreshold(
            filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        graphite_noise = np.random.normal(0, 15, (h, w)).astype(np.float32)
        lines_float = pencil_lines.astype(np.float32) + graphite_noise
        lines_clipped = np.clip(lines_float, 0, 255).astype(np.uint8)

        paper_texture = cls.generate_paper_texture(w, h, roughness=paper_roughness)
        lines_bgr = cv2.cvtColor(lines_clipped, cv2.COLOR_GRAY2BGR)

        blended = (
            lines_bgr.astype(np.float32) * paper_texture.astype(np.float32)
        ) / 255.0
        final_bgr = np.clip(blended, 0, 255).astype(np.uint8)

        cv2.imwrite(str(output_path), final_bgr)
        return output_path
