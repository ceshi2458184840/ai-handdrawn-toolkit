"""手绘风格与 ControlNet 双控制网预设引擎。"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class MasterStylePreset:
    name: str
    display_name: str
    positive_prompt: str
    negative_prompt: str
    controlnet_stack: List[Dict[str, Any]]
    cfg_scale: float
    steps: int


HANDDRAWN_MASTER_PRESETS: Dict[str, MasterStylePreset] = {
    "architectural_pen_ink": MasterStylePreset(
        name="architectural_pen_ink",
        display_name="大师级建筑钢笔速写",
        positive_prompt=(
            "masterpiece, (architectural pen and ink sketch:1.3), "
            "precise ink hatching, cross-hatching shading, raw pen strokes, "
            "clean white paper background"
        ),
        negative_prompt=(
            "bad anatomy, smooth shading, 3d render, watercolor, blurry, color, "
            "digital painting, photography"
        ),
        controlnet_stack=[
            {
                "module": "lineart_realisticness",
                "model": "control_v11p_sd15_lineart",
                "weight": 1.0,
            },
            {"module": "mlsd", "model": "control_v11p_sd15_mlsd", "weight": 0.6},
        ],
        cfg_scale=8.0,
        steps=35,
    ),
    "pencil_sketch": MasterStylePreset(
        name="pencil_sketch",
        display_name="细腻石墨铅笔素描",
        positive_prompt=(
            "masterpiece, detailed graphite pencil sketch, fine line art, "
            "hatching shading, graphite texture, clean paper background"
        ),
        negative_prompt=(
            "photorealistic, 3d render, glossy texture, smooth gradient, "
            "color background, blurry"
        ),
        controlnet_stack=[
            {
                "module": "lineart_anime",
                "model": "control_v11p_sd15_lineart",
                "weight": 0.9,
            }
        ],
        cfg_scale=7.5,
        steps=30,
    ),
    "vector_minimalist": MasterStylePreset(
        name="vector_minimalist",
        display_name="极简矢量线稿",
        positive_prompt=(
            "clean vector lineart, stroke illustration, storybook handdrawn style, "
            "flat monochrome graphic, bold outlines"
        ),
        negative_prompt=(
            "shadow, gradient, photorealism, noise, watercolor, realistic lighting"
        ),
        controlnet_stack=[
            {
                "module": "softedge",
                "model": "control_v11p_sd15_softedge",
                "weight": 0.8,
            }
        ],
        cfg_scale=7.0,
        steps=25,
    ),
}
