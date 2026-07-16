#!/usr/bin/env -S uv run
# /// script
# requires-python = "~=3.12"
# dependencies = ["pillow~=10.4", "httpx~=0.28"]
# ///
"""将图片发送到 DeepSeek V4 Vision API，输出文本描述。

用法：
    ./describe.py <image_path> [--prompt "指令"] [--max-tokens 1024]

从 ~/.claude/settings.json 读取 ANTHROPIC_AUTH_TOKEN（API key）和
ANTHROPIC_BASE_URL。默认走 DeepSeek Vision API，若 Base URL 不含
"deepseek" 则以退出码 23 通知调用方走 Claude Code 原生 Read 路径。

退出码约定（冷门值，避免与系统/API 返回值冲突）：
    0  — 成功，stdout 为识别文本
    23 — 当前配置非 DeepSeek，由调用方改用 Claude Code 原生 vision
    1  — 其它错误（API 故障、文件缺失、JSON 损坏等），不尝试替代路径
"""

import argparse, base64, json, mimetypes, sys
from pathlib import Path

import httpx

# ── 常量 ──────────────────────────────────────────────────────────
SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
DEFAULT_PROMPT = "请详细描述这张图片的内容。"
DEEPSEEK_VISION_URL = "https://api.deepseek.com/v1/chat/completions"
EXIT_NOT_DEEPSEEK = 23  # 冷门值：非 DeepSeek，调用方走原生路径


def _load_settings() -> dict:
    """从 ~/.claude/settings.json 读取配置，损坏时友好报错。"""
    if not SETTINGS_PATH.is_file():
        print("ERROR: ~/.claude/settings.json 不存在", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(SETTINGS_PATH.read_text())
    except json.JSONDecodeError as exc:
        print(
            f"ERROR: ~/.claude/settings.json 不是合法 JSON: {exc}",
            file=sys.stderr
        )
        sys.exit(1)


def _b64_image(path: str) -> tuple[str, str]:
    """返回 (base64_data, media_type)。文件缺失时 exit(1)。"""
    img_path = Path(path)
    if not img_path.is_file():
        print(f"ERROR: 图片不存在: {path}", file=sys.stderr)
        sys.exit(1)
    # 从扩展名推测 MIME 类型，未知时默认 PNG
    mime, _ = mimetypes.guess_type(str(img_path))
    if mime is None:
        mime = "image/png"
    return base64.b64encode(img_path.read_bytes()).decode(), mime


def _call_deepseek_vision(
    image_path: str, prompt: str, token: str, max_tokens: int
) -> str:
    """调 DeepSeek V4 原生 Vision API（OpenAI Chat Completions 格式）。
    返回 choices[0].message.content；失败时 exit(1)。"""
    b64, mime = _b64_image(image_path)
    data_url = f"data:{mime};base64,{b64}"

    # 构造 OpenAI 格式请求体：图片在前、文本在后
    body = {
        "model":
        "deepseek-v4-pro",
        "max_tokens":
        max_tokens,
        "messages": [{
            "role":
            "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                },
            ],
        }],
    }

    resp = httpx.post(
        DEEPSEEK_VISION_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60,
    )

    if resp.status_code != 200:
        print(
            f"ERROR: DeepSeek Vision API 返回 {resp.status_code}\n"
            f"{resp.text[:500]}",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        print(f"ERROR: API 响应格式异常: {exc}", file=sys.stderr)
        print(resp.text[:500], file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="图片文件路径")
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="自定义 vision 指令"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=1024, help="响应最大 token 数（默认 1024）"
    )
    args = parser.parse_args()

    # ── 从 settings.json 读取 API key 与 Base URL ────────────────
    settings = _load_settings()
    token = settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")
    # ANTHROPIC_BASE_URL 可能位于顶层（schema 标准）或 env 内（经
    # settings.json deep-merge 时 includeGitInstructions 等同类配置的
    # 实际路径）。两处都尝试，顶层优先。
    base_url = (
        settings.get("ANTHROPIC_BASE_URL")
        or settings.get("env", {}).get("ANTHROPIC_BASE_URL", "")
    )

    if not token:
        print(
            "ERROR: ~/.claude/settings.json 中未找到 "
            "env.ANTHROPIC_AUTH_TOKEN",
            file=sys.stderr
        )
        sys.exit(1)

    # ── 厂商自动检测 ──────────────────────────────────────────────
    # 默认走 DeepSeek（实际使用中的主要路径）。
    # 若 Base URL 不含 deepseek → exit(23)，让调用方走 Claude Code
    # 原生 vision（Read 图片自动作为 vision content 发送）。
    if "deepseek" not in base_url.lower():
        print(
            "[my-image-vision] 当前配置非 DeepSeek，"
            "请用 Claude Code 原生 vision 路径处理此图。",
            file=sys.stderr
        )
        sys.exit(EXIT_NOT_DEEPSEEK)

    text = _call_deepseek_vision(
        args.image, args.prompt, token, args.max_tokens
    )
    print(text)


if __name__ == "__main__":
    main()
