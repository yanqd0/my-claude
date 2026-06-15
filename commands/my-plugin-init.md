---
allowed-tools: Bash(node:*,npm:*,which:*)
description: 初始化开发环境，安装推荐的 Claude Code 插件和工具。
---

检查并安装推荐的插件和工具。可接收一个可选参数 `<plugin_name>`，只安装指定插件；无参数时展示全部推荐项，由用户选择。

## 插件清单

| # | 插件 | 方式 | 用途 | 前提 |
|---|------|------|------|------|
| 1 | `claude-mem-lite` | plugin | 跨会话持久记忆，SQLite FTS5 + TF-IDF 混合检索 | Node.js >= 18 |
| 2 | `claude-mem-lite`（npm 版） | npm | 同上，npm 全局安装，需手动配置 settings.json | Node.js >= 18 |
| 3 | `context7` | plugin | 拉取版本匹配的库文档，消除已废弃 API 的幻觉 | — |

> 同一插件有多行时，优先选 plugin 方式（自动管理 hook 和配置）。仅插件系统不可用时回退到 npm。官方插件（context7、github 等）无需 marketplace add，直接 install。

## 执行步骤

1. **环境检查**：`node --version` 确认 >= 18。
2. **确定安装项**：
   - 有 `<plugin_name>`：只安装指定插件（fuzzy match）。
   - 无参数：展示清单，通过交互确认安装哪些。
3. **逐项安装**：按确认的清单顺序执行。npm 方式直接 `npm install -g`；plugin 方式输出对应的 `/plugin marketplace add` 和 `/plugin install` 命令，提示用户在主交互中执行。
4. **验证**：汇报每项安装结果。plugin 方式安装后，提示退出会话并重启以生效。

## 安装详情

### 1. claude-mem-lite

**plugin 方式（推荐）**

```
/plugin marketplace add sdsrss/claude-mem-lite
/plugin install claude-mem-lite@sdsrss-claude-mem-lite
```

完成后退出当前会话并启动新会话，hook 和 MCP server 才会加载。

**npm 方式**

```bash
npm install -g claude-mem-lite
```

安装后需手动配置 `~/.claude/settings.json` 中的 MCP server 和 hook 脚本路径。不推荐，除非插件系统不可用。

### 3. context7

官方插件，无需 marketplace add。

```
/plugin install context7@claude-plugins-official
```

安装后，Claude 在回答库相关问题时自动拉取对应版本的文档，无需手动触发。

---

> 新增插件：在"插件清单"追加一行，在本节追加 "### N. 插件名" 安装详情。删除时同步移除清单和详情，保持编号连续。
