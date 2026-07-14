# Skill 目录结构规范

Skill 以 `skills/<name>/` 目录组织，必须包含 `SKILL.md`（入口），可选包含 `references/`（按需加载的细节文件）。

## SKILL.md 内容原则

- 包含 frontmatter（`name`、`description`、`allowed-tools`），`description` 需写明触发场景引导自主调用。
- 内容为执行流程 + 分支判断，轻量为主。步骤级的细节下沉到 `references/`。
- 涉及多个分支逻辑时，明确"命中即停"的优先级链。

### description 撰写规范

`description` 是 Claude 决定是否调用 skill 时能看到的**唯一信息**——SKILL.md 正文只在调用后才加载。必须包含：

1. **功能概括**：一句话说清 skill 做什么。
2. **触发场景关键词**：密集列出能触发自主调用的具体词和短语。用"当用户说/提到/涉及/出现……时"引导触发判断。
3. **调用方式区分**：写明是"可自主调用"还是"需用户显式触发"，还是两者皆可。

示例对比：
- 弱：`当用户表示想了解项目时，可自主调用。`
- 强：`当用户说"介绍/分析/总结/这个项目是干什么的/这个模块怎么工作"等探索或复盘意图时，可自主调用。`

## references/ 拆分决策

仅在内容满足任一条件时才拆分到 `references/`：

1. **条件触发**：仅在特定分支或特定条件下才需要读取（如 my-mermaid 的 10 个图类型文件，每次只读 1 个；commit-split.md 仅在有 split_plan 时读）。
2. **冷启动**：仅在首次使用、项目无历史状态时才需要（如 commit-prefix.md，仅在仓库无任何提交规范时读一次，之后由记忆 + git log 命中）。
3. **大体积**：内容超过 ~40 行且不总是需要。

不满足以上条件的细节直接 inline 在 SKILL.md 中。

## Skill 间调用

当 skill A 需要调用 skill B 时，必须在 SKILL.md 或 reference 中显式写"使用 `Skill` 工具调用 `<name>`"，而非自然语言"调用 xxx skill"。后者 Claude 会理解为邀请它自己来执行，而不会实际触发目标 skill。

## 用户交互（AskUserQuestion）

需要用户输入或确认的交互点，一律显式调用 `AskUserQuestion`，不用自然语言"提示用户确认/列出候选让用户选"，并在 frontmatter 的 `allowed-tools` 中声明 `AskUserQuestion`。

- **选择题优先**：选项互斥用单选，可并存用多选（`multiSelect: true`）。
- **选答题**：纯确认或开放输入时，把推荐动作写成 label 置首的选项，改动/自定义值走自动提供的 Other 自由文本（如"修改后再写入（在 Other 描述改动）"）。
- **仅限真实决策点**：`git status`、`git log`、`node --version` 等状态自检读作"确认"但不是交互点，保持原样；已明确描述、有默认行为等无歧义、可短路的场景不强行发问。

## 上下文资源利用

CLAUDE.md（项目级/用户级）和记忆文件在 SessionStart 时已加载到上下文，skill 内部无需显式 `Read` 这些文件——直接根据已有上下文判断即可。仅 `git log`、具体代码文件、reference 文件等动态或按需内容才需要显式读取。

## 示例

- `my-mermaid/`：SKILL.md 含类型选择触发表 + 通用格式规范；references/ 下 10 个文件，每种图类型独立，每次只读 1 个。
- `my-git-commit/`：SKILL.md 含完整识别流程链 + 条件分支；commit-message.md（每次必读，15 行）、commit-prefix.md（仅冷启动）、commit-split.md（仅拆分时），各自满足拆分条件。
- `my-code-io/`：SKILL.md 含入口解析 + 7 步流程（30 行）；4 个 references：分析框架（4 种模式 × 29 个维度）、撰写规范（含 13 行图表路由表）、格式规范、输出路径。分析框架使用模式判断表决定读哪些维度。
