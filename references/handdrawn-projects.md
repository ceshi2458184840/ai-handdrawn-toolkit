# 手绘风格 AI 项目完整列表

> 整理时间：2026-10-04  
> 更新频率：每月

---

## 目录

1. [手绘静态图/插画](#一手绘静态图插画)
2. [手绘视频动画](#二手绘视频动画)
3. [Agent/工具技能](#三agent工具技能)
4. [学术/研究模型](#四学术研究模型)
5. [免费 AI 画图 API](#五免费-ai-画图-api)
6. [快速开始](#快速开始)
7. [贡献指南](#贡献指南)

---

## 一、手绘静态图/插画

### 1. Rough.js
- **GitHub**: https://github.com/excalidraw/rough
- **Stars**: 13k+
- **License**: MIT
- **语言**: JavaScript/TypeScript
- **状态**: ✅ 稳定
- **说明**: 9KB 手绘风格渲染库，给几何形状加抖动线条，Excalidraw 底层在用
- **输出**: Canvas / SVG
- **特点**: 7 种填充（排线、实心、之字、交叉、点阵、虚线），roughness/bowing 可调
- **安装**:
  ```bash
  npm install roughjs
  ```
- **用法**:
  ```js
  const rc = rough.canvas(document.getElementById('canvas'));
  rc.rectangle(10, 10, 200, 200, { roughness: 1.5, fill: 'red' });
  ```

### 2. svg2roughjs
- **GitHub**: https://github.com/Slatebox/svg2roughjs
- **Stars**: ~200
- **License**: MIT
- **语言**: JavaScript
- **状态**: ✅ 可用
- **说明**: 把普通 SVG 自动转成 Rough.js 手绘风格
- **输出**: SVG / Canvas
- **安装**:
  ```bash
  npm install svg2roughjs
  ```
- **用法**:
  ```js
  const svg2roughjs = new Svg2Roughjs('#output-div');
  svg2roughjs.svg = document.getElementById('input-svg');
  await svg2roughjs.sketch();
  ```

### 3. anidoodle
- **GitHub**: https://github.com/alexgreensh/anidoodle
- **Stars**: ~500
- **License**: MIT
- **语言**: JavaScript
- **状态**: ✅ 可用
- **说明**: 用代码生成手绘插画/动画，9 种风格，每种都是不同画师质感
- **特点**: 无依赖，种子随机可复现
- **输出**: SVG / 动画

### 4. hand-drawn-styles
- **GitHub**: https://github.com/threerocks/hand-drawn-styles
- **Stars**: 1.1k+
- **License**: MIT
- **语言**: Python/HTML
- **状态**: ✅ 已整理
- **说明**: 19 种手绘画风配方，输出可直接复制给 Midjourney/GPT 画的提示词
- **风格**: 儿童涂色、极简线条、蜡笔、吉卜力、水墨等
- **用法**:
  ```bash
  git clone https://github.com/threerocks/hand-drawn-styles.git
  python3 scripts/render_prompt.py --style 3.1 --subject "cat" --text "不加文字"
  ```

### 5. handraw-style
- **GitHub**: https://github.com/yang0/handraw-style
- **Stars**: 3.1k+
- **License**: MIT
- **语言**: HTML/JavaScript
- **状态**: ✅ 已整理
- **说明**: 261 种手绘风格编号库，中英双语提示词
- **用法**: 记住编号就能稳定出图

---

## 二、手绘视频动画

### 6. srt-whiteboard-animation
- **GitHub**: https://github.com/geeklee/srt-whiteboard-animation
- **Stars**: ~800
- **License**: MIT
- **语言**: Python
- **状态**: ✅ 已安装
- **说明**: SRT 字幕 → 暖米黄纸张白板手绘 MP4
- **流程**: 线稿 PNG + annotation.json → stream 渲染器出片
- **示例**: 见 `demos/monkey-sitting-banana-whiteboard.mp4`

### 7. whiteboard-animator
- **GitHub**: https://github.com/masihsultani/whiteboard-animator
- **Stars**: ~300
- **License**: MIT
- **语言**: Python
- **状态**: ✅ 可用
- **说明**: 一句命令出 MP4，CPU only，无 GPU/API key
- **特点**: 自动追踪线稿骨架，单词级书写动画
- **用法**:
  ```bash
  pip install whiteboard-animator
  whiteboard-animate sketch.png --duration 8 -o out.mp4
  ```

### 8. sketchling
- **GitHub**: https://github.com/anaygarodia/sketchling
- **Stars**: ~600
- **License**: MIT
- **语言**: TypeScript
- **状态**: ⚠️ 需要 Node.js + TypeScript
- **说明**: LLM 驱动的手绘动画语言，专为 LLM 设计
- **特点**: Rough.js 渲染，支持 IK rigging，Devin 用它做出完整短片
- **安装**:
  ```bash
  npm install sketchling
  ```

### 9. whiteboard-video-engine
- **GitHub**: https://github.com/gnipbao/whiteboard-video-engine
- **Stars**: ~400
- **License**: MIT
- **语言**: Python
- **状态**: ⚠️ 安装较重
- **说明**: 照片/插画/SVG → 逐笔绘制 MP4
- **特点**: 内置神经网络线稿提取，30 种视觉风格，4 种手势皮肤

---

## 三、Agent/工具技能

### 10. Ian Handdrawn PPT
- **GitHub**: https://github.com/helloianneo/ian-handdrawn-ppt
- **Stars**: ~300
- **License**: MIT
- **语言**: Python
- **状态**: ✅ 可用
- **说明**: 文字大纲 → 手绘风技术图解 PNG（21:9/16:9）
- **特点**: Codex Skill，优化中文渲染

### 11. ian-xiaohei-illustrations
- **GitHub**: https://github.com/helloianneo/ian-xiaohei-illustrations
- **Stars**: ~200
- **License**: MIT
- **语言**: Python
- **状态**: ✅ 可用
- **说明**: 中文文案 → 16:9 手绘风插画（小黑怪角色）
- **特点**: 红/橙/蓝三色限定，白底

### 12. excalidraw-skill
- **GitHub**: https://github.com/aref-vc/excalidraw-skill
- **Stars**: ~100
- **License**: MIT
- **语言**: JavaScript/Node.js
- **状态**: ✅ 可用
- **说明**: 文字描述 → Excalidraw 风格架构图/流程图
- **特点**: 200-400ms 本地渲染，出 SVG+PNG
- **安装**:
  ```bash
  git clone https://github.com/aref-vc/excalidraw-skill.git
  cd excalidraw-skill/scripts && npm install
  ```

### 13. Doodle AI
- **GitHub**: https://github.com/Type-Think-AI/doodle-ai
- **Stars**: ~500
- **License**: MIT
- **语言**: TypeScript/Astro
- **状态**: ✅ 可用
- **说明**: 照片 → 手绘涂鸦头像，23 个可插拔技能
- **特点**: 涂鸦头像、贴纸、宠物肖像等

---

## 四、学术/研究模型

### 14. O3SLM
- **论文**: AAAI 2026
- **说明**: 首个开源手绘草图理解大模型（7B/13B）
- **链接**: https://github.com/... (AAAI 2026)

### 15. SketchAssist
- **论文**: CVPR 2026
- **说明**: 草图上色/重绘，统一指令编辑和线条重绘
- **链接**: https://arxiv.org/abs/...

### 16. SketchingReality
- **论文**: ICLR 2026
- **说明**: 抽象草图 → 真实照片
- **链接**: https://arxiv.org/abs/...

### 17. Anima-2.9B
- **HuggingFace**: https://huggingface.co/...
- **License**: Non-commercial
- **参数**: 2.9B
- **大小**: 3GB (int8)
- **状态**: ✅ 可用
- **说明**: 免费开源动漫/插画模型
- **用法**:
  ```bash
  # 下载权重
  wget https://huggingface.co/.../Anima-2.9B-preview-v1_int8_convrot.safetensors
  # 用 ComfyUI 加载
  ```

---

## 五、免费 AI 画图 API

### 18. Pollinations.ai
- **链接**: https://image.pollinations.ai/
- **费用**: 完全免费
- **限制**: 无
- **状态**: ✅ 已测试
- **说明**: 无需 API key，直接 URL 生成图片
- **用法**:
  ```bash
  curl "https://image.pollinations.ai/prompt/hand-drawn%20cat?width=800&height=600" -o cat.png
  ```

### 19. Gemini 2.5 Flash Image
- **链接**: https://aistudio.google.com/
- **费用**: 500 RPD 免费
- **限制**: 每日 500 张
- **状态**: ✅ 已确认
- **说明**: Google AI Studio，无需信用卡

### 20. Agnes / 日日新
- **链接**: 见 art-toolkit.md
- **费用**: 免费
- **状态**: ✅ 可用
- **说明**: 国内免费画图 API

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

## 贡献指南

欢迎提交 PR，补充更多手绘风格 AI 项目！

提交时请包含：
- 项目名称和链接
- Stars 数量（如可查）
- License
- 语言/平台
- 简要说明
- 安装/用法示例

---

## 许可证

MIT

---

## 更新日志

- 2026-10-04: 初始版本，整理 20+ 个项目
