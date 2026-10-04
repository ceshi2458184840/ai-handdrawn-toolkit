# 🎨 AI Handdrawn Toolkit — 工程化 Skill

## 项目定位

Production-ready AI Agent Skill，专为 Linux / Windows 用户打造，支持命令行管道交互与原生 MCP Agent Skill 协议。它联动云端 SDXL / ControlNet / Flux 模型，内置手绘 Prompt 增强引擎与 `vtracer` 矢量化后处理管线，可一键将文本描述转化为**高精度 PNG 笔触位图及无损 SVG 矢量文件**。

## 核心功能

- **三大利手风格**：铅笔素描、建筑钢笔画、极简矢量线稿
- **物理级纹理处理**：石墨质感、纸张凹凸仿真、消除 AI 塑料感
- **高精度矢量化**：Spline 样条曲线拟合，断线自动修复
- **MCP 原生支持**：直接挂载至 Claude Desktop 或 LangChain Agent
- **管道安全设计**：sys.stdout 严格输出结构化 JSON，日志/进度消息重定向至 sys.stderr

## 快速开始

```bash
pip install -e .

# 基础生成（输出 PNG + 无损 SVG 文件）
ai-handdrawn-toolkit --prompt "现代建筑速写" --style architectural_pen_ink

# Linux 管道接入（配合 jq 解析纯净 JSON 输出）
ai-handdrawn-toolkit --prompt "木质椅子" --style pencil_sketch \\| jq .data.svg_path

# Agent MCP 部署（在 Claude Desktop 的 mcp.json 中添加）：
{
  "mcpServers": {
    "ai-handdrawn-toolkit": {
      "command": "python",
      "args": ["-m", "ai_handdrawn_toolkit.mcp_server"]
    }
  }
}
```

## 仓库结构

```
ai-handdrawn-toolkit/
├── pyproject.toml                    # 现代化构建配置与依赖声明
├── src/
│   └── ai_handdrawn_toolkit/         # Python 包根目录
│       ├── __init__.py               # 包声明
│       ├── __main__.py              # python -m ai_handdrawn_toolkit 支持
│       ├── cli.py                    # Linux CLI 命令入口
│       ├── exceptions.py             # 统一防御性异常层级
│       ├── payload.py                # 云端 API Payload 构造器
│       ├── styles.py                 # 手绘风格与 ControlNet 双控制网预设引擎
│       ├── shading.py                # 物理级手绘纹理与石墨着色引擎
│       ├── vectorizer.py             # 高精度 SVG 样条曲线拟合引擎
│       └── mcp_server.py            # Model Context Protocol (MCP) Server
├── tests/                           # 单元测试套件
│   ├── test_cli.py                  # stdout/stderr 隔离与 exit code 单元测试
│   └── test_styles.py               # Prompt 动态增强校验测试
├── README.md                        # 中文主文档 (用户默认阅读)
├── README_EN.md                     # 英文文档 (英文用户专属)
├── manifest.json                    # AI Agent Skill 标准契约声明
└── SKILL.md                         # 本技能文档
```

## 三大利手风格预设

| 预设标识 | 风格描述 | ControlNet 控形 | 输出特性 |
|----------|----------|----------|----------|
| `pencil_sketch` | 细腻石墨铅笔素描 | LineArt Anime | 细腻阴影排线与石墨质感 |
| `architectural_pen_ink` | 大师级建筑钢笔速写 | LineArt Realism + MSLD | 极简高对比度线条，适配建筑设计 |
| `vector_minimalist` | 极简矢量线稿 | SoftEdge | 粗笔触大块面，极度适配 SVG 转换 |

## 技术特点

### 1. 现代 Python 项目结构
- `pyproject.toml` 现代化单文件构建
- `src/` 隔离开发环境与运行环境
- `tests/` 完整的单元测试套件
- 严格遵循 Python 打包规范

### 2. 展品级画质
- 内置三套经过算法调优的手绘预设风格
- 物理级纸张纹理与石墨着色处理
- 高对比度线稿预处理 + Spline 矢量化
- 消除 AI 生成图片的塑料感与 artifacts

### 3. 管道安全设计
- **sys.stdout** 严格仅输出结构化 JSON，供 pipeline 读取
- **sys.stderr** 仅输出日志与 Spinner
- **exit code** 标准 POSIX 约定 (0=成功, 1=参数/用户错误, 2=系统/网络/渲染错误)

### 4. Agent 原生支持
- 内置 `manifest.json`，符合 AI Agent Skill 标准
- 支持 MCP (Model Context Protocol) 协议
- 原生 Claude Desktop 集成
- LangChain Agent 适配

### 5. 防御性编程
- 统一异常层级：`ToolkitError` → `StyleNotFoundError` / `ProviderApiError` / `VectorizationError`
- 网络请求重试策略（transient 错误重试，permanent 直接抛出）
- 参数校验 (Pydantic) + 错误捕获 + JSON 错误输出

## 参数说明

| 参数 | 类型 | 默认值 | 描述 |
|------|------|------|------|
| `--prompt` | string | *必填* | 手绘内容描述 (例如 "architectural sketch of a modern villa") |
| `--style` | string | `pencil_sketch` | 风格 ('pencil_sketch', 'architectural_pen_ink', 'vector_minimalist') |
| `--output-dir` | string | `/tmp` | 输出目录 (自动创建，不存在时新建) |
| `--no-vectorize` | flag | false | 禁用矢量化处理，直接输出 PNG |

## 输出契约

### 成功时 stdout (纯净 JSON)
```json
{
  "success": true,
  "data": {
    "png_path": "/path/to/sketch_[hash].png",
    "svg_path": "/path/to/sketch_[hash].svg",  # 当 vectorize=true 时存在
    "style_used": "pencil_sketch",
    "enhanced_prompt": "用户输入的 prompt + 风格后缀"
  }
}
```

### 错误时 stdout (纯净 JSON)
```json
{
  "success": false,
  "error": "错误描述",
  "exit_code": 1 或 2
}
```

### 日志时 stderr (人类可读)
```
[14:23:45] [INFO] Initializing sketch generation pipeline...
[14:23:46] [INFO] Enhanced Prompt: architectural sketch of a modern villa, masterpiece, (architectural pen and ink sketch:1.3), precise ink hatching, cross-hatching shading, raw pen strokes, clean white paper background...
[14:23:47] [INFO] Applying physical paper texture and graphite shading shader...
[14:23:48] [INFO] Executing Spline vectorization pipeline (PNG -> SVG)...
```

## 质量保证

1. **Gate 0**: 文件完整性 (>1000 bytes)
2. **Gate 1**: 水印检测（heuristic corner + vision，两层融合）
3. **Gate 2**: 风格检查（vision judge 优先，失败降级到 prompt-based style_gate）
4. **Gate 3**: 渲染质量（heuristic score >= 0.35）

## 依赖

```toml
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "tenacity>=8.2.0",
    "vtracer>=0.6.0",
    "Pillow>=10.0.0",
    "opencv-python>=4.8.0",
    "numpy>=1.24.0",
    "mcp>=1.0.0"
]
```

## 许可证

MIT License - 完全开源，供生产使用

## 版本

当前版本: `0.2.0`

## 修订记录

### v0.2.0 (2025-06-17)
- 物理级纹理着色器 (`shading.py`) 新增石墨颗粒与纸张正片叠底
- 高精度矢量化引擎 (`vectorizer.py`) 强化线稿对比度 + Spline 样条曲线
- 完善风格引擎 (`styles.py`) 采用 `MasterStylePreset` 三层控制网
- 增强异常处理 (`exceptions.py`) 统一防御性异常层级
- 清理死代码，优化日志隔离与参数校验
- 完成冒烟测试套件 (`tests/`)
- 更新 README.md / README_EN.md 双语文档

### v0.1.0
- 初始版本，基础 CLI 与 MCP 支持
