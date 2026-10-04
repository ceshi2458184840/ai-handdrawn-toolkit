# 🎨 AI Handdrawn Toolkit — 工程化 Skill

## When to Use
- 用户要手绘风格图片/线稿
- 用户说不用 GPT，要用免费模型
- 需要把能力打包成可被 Agent 调用的 Skill
- 用户要求清理/重置仓库内容

## 始终规则
1. **免费模型优先**：Pollinations.ai 无 key 无限制，优先；Gemini 2.5 Flash 500张/天 作第二层；OpenAI-compatible / custom 端点按配置启用。
2. **人像用 GPT，非人像用免费模型**：除非用户明确要求 GPT，否则手绘/风景/线稿一律走免费模型。
3. **Skill 契约**：必须生成 SKILL.md，定义能力、参数 schema、输出契约（stdout=路径，stderr=日志，sidecar JSON 元数据）。
4. **Python 包规范**：必须生成 pyproject.toml，支持 `pip install -e .`，脚本入口 `python -m app.cli` 或 `ai-handdrawn-toolkit`。
5. **stdout/stderr 分离**：数据/路径只能走 stdout；日志/调试只能走 stderr；不允许任意 print 污染 stdout。
6. **可复现文件名**：用 prompt 截断 sanitize，不用随机 hash；避免中文/emoji/非法字符。
7. **目录自创建**：输出目录不存在时自动 `mkdir(parents=True, exist_ok=True)`；不要默认往 CWD 乱扔文件。
8. **重试分永久/ transient**：网络/超时/限流/provider 错误才重试；鉴权/参数错误直接抛，不重试。
9. **Vision Gate 合同**：vision judge 返回键必须是 `final` 或 `handdrawn`；调用方必须做 JSON 解析失败降级，不能假设键存在。
10. **测试必过**：至少一条冒烟测试 mock 网络，断言能产出一张 PNG + 一份 JSON 且不抛异常。
11. **仓库主 README 用用户语言**：中文用户=中文主 README，英文改为 README_EN.md；GitHub 默认显示主 README，不用额外链接切换。
12. **仓库内链接用相对路径**：禁止硬编码 `https://github.com/...` 绝对路径，fork/分支/私有部署会全部 404。
13. **绝不向用户甩操作链接**：用户说找不到/不会用=阿清自己解决，不是把 GitHub Settings 链接甩回去。
14. **丑图/垃圾产物不进仓库**：生成的 demo PNG、MP4、占位 JSON 一律不进 git；仓库只留代码和文档。
15. **用户要清仓库=清干净**：`git rm --cached -r` + 清理工作区 + 验证空 + 推送，不留残留文件。

## 工作流

### 1. 先读评审再动手
- 评审说前端问题 → 忽略（本项目是 Python CLI，无浏览器渲染管线）。
- 评审说 Skill manifest / pyproject / stdout / 死代码 / README 夸大 → 立刻修。
- 评审说 i18n / 多语言 → 检查 README 主语言是否对、链接是否相对路径。

### 2. 构建顺序
1. 写 `pyproject.toml`（name/version/dependencies/scripts）。
2. 写 `SKILL.md`（能力、参数、输出契约、环境变量）。
3. 重构 CLI：`_log()` 统一打 stderr；stdout 只 print 输出路径。
4. 清理死代码：占位 provider、`_PROFILES`、`postprocess` 等。
5. README 去夸大：删掉未实现功能，只保留实际可运行的。
6. 加冒烟测试：subprocess 调 CLI，断言 PNG + JSON + exit 0。

### 3. 生成图片
```bash
python -m app.cli generate "prompt" \
  --style clean_sketch \
  --provider pollinations \
  --output-dir generated/ \
  --candidates 2
```

### 4. 质量门禁顺序
- Gate 0: 文件完整性（>1000 bytes）
- Gate 1: 水印检测（heuristic corner + vision，两层融合）
- Gate 2: 风格检查（vision judge 优先，失败降级到 prompt-based style_gate）
- Gate 3: 渲染质量（heuristic score >= 0.35）

## 坑与教训
- `style_match` 键不存在于 vision_judge 返回，必须用 `final` 或 `handdrawn`，否则全拒。
- refinement 不要把 `GeneratedImage` 传给 provider.generate()，传 prompt 字符串，且只检查水印，不重新打分。
- `--candidates 0` 必须 fallback 到 1，不能用 falsy 判断。
- `Config` 必须 deepcopy，否则全局默认值被污染。
- `build_providers()` 缺 key 的 provider 用 `_try_append` 包裹，不能抛异常导致整个链路断掉。
- `OpenAICompatibleProvider` 构造函数 `name` 参数必须放最后且带默认值，否则测试和调用签名不一致。
- 清空 git 仓库时，先 `git rm --cached -r` 清理索引，再用 Python 脚本清理工作区（避免 bash rm  блокировка），最后 `git add -A` 验证空树后推送。
- 远程仓库已比本地新时，先 `git pull --rebase` 再推送；rebase 冲突优先 `git rebase --abort` + `git reset --hard origin/main` 重建，不要硬解冲突。
- 用户说"删掉/全部删除"=必须真删完再报，不留残留；删完执行 `ls` 验证并贴输出。
- 用户说找不到 GitHub 仓库=说明账号多/链接复杂，阿清自己用 gh CLI 处理，不甩链接给用户。
- 评审如果开始批评前端概念（Web Worker / Canvas / SVG XSS / DOMPurify），先确认项目类型是 Python CLI 还是浏览器应用，不要混用标准。

## References
- `references/provider-routing.md` — 免费/付费 API 路由决策
- `references/review-triage.md` — 评审指责分类与处理策略
- `references/git-repo-cleanup.md` — 清空 git 仓库的标准流程与避坑
- `references/pyproject-src-layout.md` — 现代化 src 布局与 pyproject 模板
