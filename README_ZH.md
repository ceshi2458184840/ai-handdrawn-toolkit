<p align="center">
  <a href="./README.md">🇨🇳 简体中文</a> | <a href="./README_ZH.md">🇨🇳 中文备选</a> | <a href="./README_EN.md">🇬🇧 English</a>
</p>

# 🎨 AI Handdrawn Toolkit — 工程化技能

> 本文件与 [README.md](./README.md) 内容完全等效，仅语言表述略有差异。

## 项目定位

生产级 AI Agent 技能包，专为 Linux / Windows 用户打造，支持命令行管道交互与原生 MCP Agent 技能协议。可联动云端文生图模型，内置手绘 Prompt 增强引擎与矢量化后处理管线，一键将文本描述转化为高精度 PNG 位图及无损 SVG 矢量文件。

## 核心功能

- **三大利手风格**：铅笔素描、建筑钢笔画、极简矢量线稿
- **物理级纹理处理**：石墨质感、纸张凹凸仿真、消除 AI 塑料感
- **高精度矢量化**：Spline 样条曲线拟合，断线自动修复
- **MCP 原生支持**：直接挂载至 Claude Desktop 或 LangChain Agent
- **管道安全设计**：stdout 只输出 JSON，日志走 stderr

## 快速开始

```bash
pip install -e .

# 基础生成（输出 PNG + 无损 SVG 文件）
ai-handdrawn-toolkit --prompt "现代建筑速写" --style architectural_pen_ink

# Linux 管道接入（配合 jq 解析纯净 JSON 输出）
ai-handdrawn-toolkit --prompt "木质椅子" --style pencil_sketch | jq .data.svg_path

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
├── pyproject.toml              # 构建配置与依赖声明
├── src/ai_handdrawn_toolkit/   # Python 包
│   ├── cli.py                  # 命令行入口
│   ├── exceptions.py           # 统一异常层级
│   ├── payload.py              # API Payload 构造器
│   ├── styles.py               # 手绘风格预设引擎
│   ├── shading.py              # 物理纹理着色引擎
│   ├── vectorizer.py           # SVG 矢量化引擎
│   └── mcp_server.py           # MCP 服务器
├── tests/                      # 冒烟测试套件
├── README.md                   # 中文主文档
├── README_ZH.md                # 中文备选文档
├── README_EN.md                # 英文文档
└── SKILL.md                    # 技能文档
```

## 风格预设

| 预设标识 | 风格 | 输出特性 |
|---|---|---|
| `pencil_sketch` | 细腻石墨铅笔素描 | 细腻阴影排线与石墨质感 |
| `architectural_pen_ink` | 大师级建筑钢笔速写 | 高对比度线条，适配建筑设计 |
| `vector_minimalist` | 极简矢量线稿 | 粗笔触大块面，适配 SVG 转换 |

## 参数说明

| 参数 | 默认值 | 描述 |
|---|---|---|
| `--prompt` | *必填* | 手绘内容描述（英文效果更佳） |
| `--style` | `pencil_sketch` | `pencil_sketch` / `architectural_pen_ink` / `vector_minimalist` |
| `--output-dir` | `/tmp` | 输出目录（自动创建） |
| `--no-vectorize` | false | 禁用矢量化 |
| `--no-shading` | false | 跳过纹理着色 |

## 输出契约

```json
{
  "success": true,
  "data": {
    "png_path": "/tmp/sketch_example_pencil_sketch.png",
    "svg_path": "/tmp/sketch_example_pencil_sketch.svg",
    "style_used": "pencil_sketch",
    "enhanced_prompt": "example, detailed graphite pencil sketch..."
  }
}
```

## 许可证

MIT License
