---
allowed-tools: Bash(node:*,npm:*,which:*,cat:*)
description: 初始化开发环境，安装推荐的 Claude Code 插件和工具。
---

检查并安装推荐的插件和工具。支持增量安装——已安装的插件自动跳过，不重复提示。可接收一个可选参数 `<plugin_name>`，只安装指定插件；无参数时展示全部推荐项，由用户选择。

## 插件清单

| # | 插件 | 方式 | 检测标识 | 用途 | 前提 |
|---|------|------|---------|------|------|
| 1 | `claude-mem-lite` | npm | `which claude-mem-lite` | 跨会话持久记忆，SQLite FTS5 + TF-IDF 混合检索 | Node.js >= 18 |
| 2 | `context7` | plugin | `context7@claude-plugins-official` | 拉取版本匹配的库文档，消除已废弃 API 的幻觉 | — |
| 3 | `explanatory-output-style` | plugin | `explanatory-output-style@claude-plugins-official` | 教育式解释实现选择，输出附带设计决策说明 | — |
| 4 | `agent-bell` | npm | `which agent-bell` | 多平台桌面通知与音效：Stop/Notification 事件触发，冷却防轰炸，tmux 兼容 | Node.js >= 18 |

> 官方插件（context7、explanatory-output-style 等）无需 marketplace add，直接 `install`。

## 执行步骤

1. **环境检查**：`node --version` 确认 >= 18。
2. **检测已安装**：
   - plugin 方式：读取 `~/.claude/plugins/installed_plugins.json`，检查 `plugins` 字段的 key 中是否包含"检测标识"。
   - npm 方式：执行"检测标识"中的命令，按退出码判断是否已安装（0=已安装）。
   - 已安装的插件标记为"跳过"，不参与后续交互和安装。
3. **确定安装项**：
   - 有 `<plugin_name>`：在清单中 fuzzy match，仅限未安装的。
   - 无参数：展示清单（标注哪些已安装、哪些待安装），通过交互确认要安装哪些。
   - 若全部已安装：汇报"所有推荐插件均已安装"，结束。
4. **逐项安装**：按确认的清单顺序执行。npm 方式直接执行对应安装命令；plugin 方式输出 `/plugin install` 命令，提示用户在主交互中执行。
5. **验证**：汇报每项安装结果。plugin 方式安装后，提示 `/reload-plugins` 以加载，必要时重启会话。

## 安装详情

### 1. claude-mem-lite

```bash
npm install -g claude-mem-lite && claude-mem-lite install
```

`claude-mem-lite install` 自动完成 MCP server 注册、hook 配置和数据库初始化，无需手动编辑 settings.json。

### 2. context7

官方插件。

```
/plugin install context7@claude-plugins-official
```

安装后执行 `/reload-plugins`。Claude 在回答库相关问题时自动拉取对应版本的文档。

### 3. explanatory-output-style

官方插件。

```
/plugin install explanatory-output-style@claude-plugins-official
```

安装后执行 `/reload-plugins`。Claude 在实现代码时会附带设计决策说明。

### 4. agent-bell

```bash
npm install -g agent-bell && npx agent-bell init
```

`init` 向导自动检测 Claude Code 并配置 Stop + Notification hook，支持多套音效主题、可配置冷却和升级提示。配置文件在 `~/.agent-bell/config.json`。

---

> 新增插件：在"插件清单"追加一行（含检测标识），在本节追加 "### N. 插件名" 安装详情。删除时同步移除清单和详情，保持编号连续。
