"""云端 API Payload 构造器。"""

from typing import Any, Dict
from pydantic import BaseModel, Field
from .styles import HANDDRAWN_MASTER_PRESETS


class HanddrawnRequestSchema(BaseModel):
    prompt: str = Field(..., description="手绘画面描述")
    style: str = Field(
        default="architectural_pen_ink", description="风格预设标识"
    )
    width: int = Field(default=1024, ge=512, le=2048)
    height: int = Field(default=1024, ge=512, le=2048)


class PayloadBuilder:
    def __init__(self, request: HanddrawnRequestSchema) -> None:
        self.req = request
        self.preset = HANDDRAWN_MASTER_PRESETS.get(
            request.style, HANDDRAWN_MASTER_PRESETS["architectural_pen_ink"]
        )

    def build_sd_payload(self) -> Dict[str, Any]:
        return {
            "prompt": f"{self.req.prompt}, {self.preset.positive_prompt}",
            "negative_prompt": self.preset.negative_prompt,
            "steps": self.preset.steps,
            "cfg_scale": self.preset.cfg_scale,
            "width": self.req.width,
            "height": self.req.height,
            "alwayson_scripts": {
                "controlnet": {"args": self.preset.controlnet_stack}
            },
        }
