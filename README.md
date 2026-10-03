# AI 手绘工具箱
> 收集、整理、可直接运行的手绘风格 AI 项目与开源工具。优先免费模型，不依赖 GPT。

## 一、手绘静态图/插画

### 1. Rough.js — 手绘风格渲染库
- **状态**: ✅ 已集成
- **说明**: 9KB JS 库，给几何形状加抖动线条，Excalidraw 底层在用
- **输出**: Canvas / SVG
- **特点**: 7 种填充（排线、实心、之字、交叉、点阵、虚线），roughness/bowing 可调
- **链接**: https://github.com/excalidraw/rough
- **用法**: 
  ```bash
  npm install roughjs
  ```
  ```js
  const rc = rough.canvas(document.getElementById('canvas'));
  rc.rectangle(10, 10, 200, 200, { roughness: 1.5, fill: 'red' });
  ```

### 2. svg2roughjs — SVG 转手绘风
- **状态**: ✅ 可用
- **说明**: 把普通 SVG 自动转成 Rough.js 手绘风格
- **输出**: SVG / Canvas
- **链接**: https://github.com/Slatebox/svg2roughjs
- **用法**:
  ```bash
  npm install svg2roughjs
  ```
  ```js
  const svg2roughjs = new Svg2Roughjs('#output-div');
  svg2roughjs.svg = document.getElementById('input-svg');
  await svg2roughjs.sketch();
  ```

### 3. anidoodle — 代码生成手绘插画
- **状态**: ✅ 可用
- **说明**: 用代码生成手绘插画/动画，9 种风格，每种都是不同画师质感
- **特点**: 无依赖，种子随机可复现
- **输出**: SVG / 动画
- **链接**: https://github.com/alexgreensh/anidoodle

### 4. hand-drawn-styles — 19 种手绘画风提示词
- **状态**: ✅ 已整理
- **说明**: 输出可直接复制给 Midjourney/GPT 画的提示词
- **风格**: 儿童涂色、极简线条、蜡笔、吉卜力、水墨等
- **链接**: https://github.com/threerocks/hand-drawn-styles
- **用法**: 
  ```bash
  git clone https://github.com/threerocks/hand-drawn-styles.git
  python3 scripts/render_prompt.py --style 3.1 --subject "cat" --text "不加文字"
  ```

### 5. handraw-style — 261 种手绘风格编号库
- **状态**: ✅ 已整理
- **说明**: 261 种手绘风格编号，中英双语提示词
- **用法**: 记住编号就能稳定出图
- **链接**: https://github.com/yang0/handraw-style

---

## 二、手绘视频动画

### 6. srt-whiteboard-animation — 线稿转白板手绘视频
- **状态**: ✅ 已安装
- **说明**: 线稿 PNG + annotation.json → stream 渲染器出 MP4
- **特点**: 暖米黄纸张底，逐笔绘制动画
- **链接**: https://github.com/geeklee/srt-whiteboard-animation
- **示例**: 见 `demos/monkey-sitting-banana-whiteboard.mp4`

### 7. whiteboard-animator — 一键生成白板动画
- **状态**: ✅ 可用
- **说明**: 一句命令出 MP4，CPU only，无 GPU/API key
- **特点**: 自动追踪线稿骨架，单词级书写动画
- **链接**: https://github.com/masihsultani/whiteboard-animator
- **用法**:
  ```bash
  whiteboard-animate sketch.png --duration 8 -o out.mp4
  ```

### 8. sketchling — LLM 驱动的手绘动画语言
- **状态**: ⚠️ 需要 Node.js + TypeScript
- **说明**: 专为 LLM 设计，Rough.js 渲染，支持 IK  rigging
- **特点**: Devin 用它冷启动做出完整短片《The Lantern Maker》
- **链接**: https://github.com/anaygarodia/sketchling

---

## 三、Agent/工具技能

### 9. Ian Handdrawn PPT — 文字转手绘技术图解
- **状态**: ✅ 可用
- **说明**: 文字大纲 → 手绘风技术图解 PNG（21:9/16:9）
- **特点**: Codex Skill，优化中文渲染
- **链接**: https://github.com/helloianneo/ian-handdrawn-ppt

### 10. ian-xiaohei-illustrations — 中文文案转手绘插画
- **状态**: ✅ 可用
- **说明**: 中文文案 → 16:9 手绘风插画（小黑怪角色）
- **特点**: 红/橙/蓝三色限定，白底
- **链接**: https://github.com/helloianneo/ian-xiaohei-illustrations

### 11. excalidraw-skill — 文字转架构图
- **状态**: ✅ 可用
- **说明**: 文字描述 → Excalidraw 风格架构图/流程图
- **特点**: 200-400ms 本地渲染，出 SVG+PNG
- **链接**: https://github.com/aref-vc/excalidraw-skill

---

## 四、学术/研究模型

### 12. O3SLM — 手绘草图理解大模型
- **状态**: 🔬 研究
- **说明**: 首个开源手绘草图理解大模型（7B/13B）
- **链接**: https://github.com/... (AAAI 2026)

### 13. SketchAssist — CVPR 2026 草图编辑
- **状态**: 🔬 研究
- **说明**: 草图上色/重绘，统一指令编辑和线条重绘
- **链接**: https://arxiv.org/abs/...

### 14. Anima-2.9B — 免费开源动漫/插画模型
- **状态**: ✅ 可用
- **说明**: 2.9B 参数，3GB 文件，LoRA 微调
- **链接**: https://huggingface.co/...
- **用法**:
  ```bash
  # 下载权重
  wget https://huggingface.co/.../Anima-2.9B-preview-v1.safetensors
  # 用 ComfyUI 加载
  ```

---

## 五、免费 AI 画图 API（手绘风格）

### 15. Pollinations.ai — 免费 AI 画图
- **状态**: ✅ 已测试
- **说明**: 完全免费，无需 API key
- **链接**: https://image.pollinations.ai/
- **用法**:
  ```bash
  curl "https://image.pollinations.ai/prompt/hand-drawn%20monkey%20sketch?width=1200&height=800"
  ```

### 16. Gemini 2.5 Flash Image — 每日 500 张免费
- **状态**: ✅ 已确认
- **说明**: Google AI Studio，500 RPD，无需信用卡
- **链接**: https://aistudio.google.com/

### 17. Agnes / 日日新 — 免费画图模型
- **状态**: ✅ 可用
- **说明**: 国内免费画图 API
- **链接**: 见 art-toolkit.md

---

## 快速开始

### 安装 Rough.js
```bash
npm install roughjs
```

### 生成手绘风格图片
```bash
# 用 Pollinations（免费）
curl "https://image.pollinations.ai/prompt/hand-drawn%20cat?width=800&height=600" -o cat.png

# 用 Gemini 2.5 Flash（每日 500 张）
# 访问 https://aistudio.google.com/ 获取 API key
```

### 生成白板动画视频
```bash
# 安装 whiteboard-animator
pip install whiteboard-animator

# 生成视频
whiteboard-animate sketch.png --duration 8 -o out.mp4
```

---

## 项目结构
```
ai-handdrawn-toolkit/
├── README.md              # 本文件
├── references/            # 参考项目列表
│   └── art-toolkit.md
├── scripts/               # 工具脚本
│   ├── generate_sketch.py # 生成手绘风格草图
│   └── render_whiteboard.py # 渲染白板动画
├── demos/                 # 演示文件
│   ├── monkey-sitting-banana.png
│   └── monkey-sitting-banana-whiteboard.mp4
└── assets/                # 素材资源
```

---

## 贡献
欢迎提交 PR，补充更多手绘风格 AI 项目！

## 许可证
MIT
