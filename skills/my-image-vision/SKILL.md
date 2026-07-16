---
name: my-image-vision
description: >-
  图片识图与预处理：对图片进行压缩/剪裁/灰度/模糊等预处理后，调用 DeepSeek V4 Vision API
  返回文本描述。当用户说"看这张图/分析截图/图片里有什么/识别这张图/OCR/描述图片内容"
  等识图意图时可自主调用；支持多重处理合并为一张图后一次识别。
allowed-tools: Read Write Bash AskUserQuestion
---

对用户指定的图片进行预处理（可选），然后调用 DeepSeek V4 Vision API 返回文本描述。
厂商自动检测：当前配置为 DeepSeek 时走原生 Vision API，否则 fallback 到 Anthropic 原生路径。

## 执行步骤

1. **解析意图**：提取图片路径（相对/绝对路径均可）和预处理需求——用户可能说
   "压一下再识别"、"灰度后看"、"把这张图模糊掉再 OCR"等。图片路径不存在时
   用 `AskUserQuestion`（单选）确认，选项为邻近的候选图片路径。
2. **确认预处理计划**：列出拟执行的操作清单（0~N 个，需复合处理时标明合并为一张图），
   用 `AskUserQuestion`（单选）确认——"按此预处理并识别"（推荐）、
   "调整预处理（在 Other 描述）"、"不做预处理，直接识别"。
3. **执行预处理**（如需）：
   - 单图 1+ 操作：`~/.claude/skills/my-image-vision/scripts/preprocess.py`
     `<input> --op1 ... --opN -o <output>`
   - 单图多处预处理后需合并 → 多次 `preprocess.py` 后
     `~/.claude/skills/my-image-vision/scripts/composite.py`
     `<a> <b> ... --labels "标签1,标签2" -o <output>`
   操作语法详见 `Read` `references/preprocessing.md`（条件触发，仅此步读）。
4. **发送识图**：`~/.claude/skills/my-image-vision/scripts/describe.py`
   `<image> [--prompt "指令"] [--max-tokens N]`。
   脚本自动从 `~/.claude/settings.json` 读取 API key，默认走 DeepSeek Vision API。
   按退出码分支处理：
   - 退出码 **0** → stdout 为识别文本，直接进入步骤 5；
   - 退出码 **23** → 当前配置非 DeepSeek，`Read` `references/anthropic-vision.md`
     按其中规范处理；
   - 退出码 **其他** → 错误，stdout/stderr 为错误信息，不尝试替代路径。
   若需补充前置上下文（之前讨论的结构体定义、变量含义等），经 `--prompt` 传入
   ——脚本为无状态单轮接口，skill 负责从对话中提取上下文组织提示词。
5. **输出结果**：将描述嵌入对话上下文。如涉及预处理操作链，简要标注（如
   "（经灰度+二值化后识别）"）。

## 约束

- API key 从 `~/.claude/settings.json` 的 `env.ANTHROPIC_AUTH_TOKEN` 读取，
  不传参数、不硬编码到脚本或 skill 正文。
- 图片仅送 DeepSeek Vision API（与当前对话模型同一供应商），不送第三方。
- `--prompt` 中不包含敏感信息（凭证、token 等）。
