# 项目级 agent 角色索引

按 `<description>` 匹配候选角色；命中则 `Read` `roles/<role>.md` 按模板填充项目专有知识，
未命中走下方通用骨架。

## 角色索引表

| 角色 | 一句话职责 | 工具集 | 适用项目特征 | 模板 |
|------|-----------|--------|-------------|------|
| `tester` | 跑项目测试并精简报告失败 | 只读 + Bash | 有构建系统/测试套件（同名覆盖全局 tester 的主场景） | `roles/tester.md` |
| `debugger` | 项目取证环境下的根因诊断 | 只读 + Bash + Edit | 有专属取证环境（容器、符号、日志） | `roles/debugger.md` |
| `ci-devops` | CI 红灯诊断与构建矩阵修复建议 | 只读 + Bash | 有 CI 流水线/Docker/交叉编译 | `roles/ci-devops.md` |
| `db-specialist` | schema/迁移/慢查询评审 | 只读（禁写 SQL） | 有数据库与迁移工具 | `roles/db-specialist.md` |
| `performance` | 测量驱动的性能分析 | 只读 + Bash | 有 profiler/基准工具链 | `roles/performance.md` |
| `navigator` | 仓库结构导航与知识积累 | 只读 + `memory: project` | 大型/长期维护仓库 | `roles/navigator.md` |

全局已有薄壳版 code-reviewer / security-auditor，项目级同名覆盖时不入库，走通用骨架并对齐被覆盖者的职责边界。

## 通用骨架（未命中角色时）

frontmatter 按 agent-structure 规范：`name`、`description`（正向触发 + 负向排除 + 触发节奏）、
`tools` 最小权限（只读优先）、`background`、`color`。

正文四段式：

1. **Mission**：一句角色定调（"你是 <项目名> 的 XX 专家……"）。
2. **Workflow**：3-5 步编号流程，首步确认范围（不该接手时立即停止并说明）。
3. **Output Format**：首行一句话结论；发现按 `文件:行号` + 描述 + 修复方向；
   末尾固定「主对话后续动作」一节。
4. **约束**：负面清单（只读不改、不安装依赖等）。

生成时将模板中 `<项目专有知识>` 占位替换为实际值：优先从代码库探测（构建文件、CI 配置、
目录结构），探测不到的向用户确认。

## 社区共识要点

- **单一职责**：一个 agent 只做一件事，拒绝"全栈万能"（prompt 过长则行为退化）。
- **按职责命名**：`tester`/`navigator` 而非 `engineer`，委派路由更准。
- **只读优先**：能只读就不给 Edit/Write——更可信、更便宜、更快。
- **正文 20-60 行**：过长稀释核心指令并浪费每次调用的上下文，过短行为不可控。
- **description 只写路由**：触发条件进 description，行为指令一律进正文。
