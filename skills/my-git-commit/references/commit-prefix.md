# 提交前缀规范

## 默认前缀（Conventional Commits）

提交标题采用 `<type>: <描述>` 格式。

| type | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能/特性 | `feat: 新增 mermaid 图类型选择指南` |
| `fix` | Bug 修复 | `fix: 修复 settings 数组合并重复` |
| `chore` | 杂务、维护、工具 | `chore: 清理失效软链接` |
| `docs` | 文档 | `docs: 更新 README 安装说明` |
| `refactor` | 重构（非功能非修复） | `refactor: 提取公共 deep merge 逻辑` |
| `style` | 代码格式（不影响逻辑） | `style: 统一缩进` |
| `perf` | 性能优化 | `perf: 减少文件遍历次数` |
| `test` | 测试 | `test: 补充 revert 边界用例` |
| `build` | 构建系统、依赖 | `build: 升级 pyyaml 到 6.x` |
| `ci` | CI/CD 配置 | `ci: 添加 pre-commit 检查` |

> `git revert` 自动生成 `Revert "xxx"` 格式的提交信息，无需修改，因此不提供 `revert` type。

- type 全小写，后跟 `: `（冒号+空格），再接中文描述。
- 标题总长度（含 type 前缀和 `: `）≤ 40 字符。

## 规范识别流程

每次执行时，按以下流程确定本次使用的提交规范：

1. **读 CLAUDE.md**：优先检查 `CLAUDE.md`（项目级）和 `~/.claude/CLAUDE.md`（用户级）中是否有提交规范相关描述（关键词：提交前缀、commit type、commit convention、提交格式、commit message 等）。若有明确规范，直接遵从，跳过后续步骤。
2. **读记忆**：读取记忆中的 `commit-convention` 记录。记忆类型为 `reference`，记录仓库路径、规范名称、type 列表。
3. **记忆命中**：`git log --oneline -10` 检查最近提交是否仍吻合记忆中的规范。吻合则直接使用该规范。
4. **未命中或不吻合**：`git log --oneline -30` 分析标题格式：
   - 若多数提交匹配 `<type>(<scope>): <描述>`（Angular 风格）→ 沿用，识别其 type 集合。
   - 若多数提交匹配 `<type>: <描述>`（Conventional Commits）→ 沿用，识别其 type 集合。
   - 若纯中文描述、无 type 前缀 → 启用默认规范（上表）。
   - 若格式混杂、无法判断多数 → 启用默认规范。
5. **写记忆**：识别完成后，将结果写入记忆文件 `commit-convention.md`。写完后，提示用户可将规范固化到 `CLAUDE.md`。

> 优先级：CLAUDE.md > 记忆 > 历史分析。仓库已有规范 → 遵守已有规范；仓库无规范 → 启用本命令默认规范。
