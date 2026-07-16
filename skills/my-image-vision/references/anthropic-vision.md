# Anthropic 原生 Vision 路径

直接 `Read` 图片路径（或预处理后的输出图）。Claude Code 会按当前配置的
`ANTHROPIC_BASE_URL` 自动将图片作为 vision content 发送给对应模型——
不需手动调用 API，不需额外鉴权。此路径对 Anthropic 原生模型和所有支持
vision 的 Anthropic 兼容端点均有效。
