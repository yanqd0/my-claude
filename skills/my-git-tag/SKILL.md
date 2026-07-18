---
name: my-git-tag
description: >-
  打语义化版本 tag，自动生成改动摘要并同步 CHANGELOG。
  当用户说"打tag/发布版本/打一个版本/创建tag/发版"时可自主调用；
  也支持用户显式通过 /my-git-tag 触发。
  预发布版本（alpha/beta/rc/dev）跳过 CHANGELOG，从 git log 归类生成 tag message；
  打 tag 前校验项目配置文件（Cargo.toml/package.json/pyproject.toml 等）中的版本号一致性。
allowed-tools: Bash(git:*,test:*) Read Edit Write Grep Skill AskUserQuestion
---

打 `git tag`，支持一个可选参数：`<tag_name>`。

## 执行步骤

### 1. 确定版本号

`Read` `~/.claude/skills/my-changelog/references/next-version.md`，按其流程解析或推算版本号 — 提供 `<tag_name>` 则采用并校验格式，为空则自动推算下一个版本号；对用户非空输入做了调整（如修正格式）时须先用 `AskUserQuestion` 请用户确认。记录输出的 `<version>`、`<last_tag>`、`<is_prerelease>`。

### 2. 识别预发布版本

根据 `<is_prerelease>` 标识：
- **`true`**（版本含 `-alpha`/`-beta`/`-rc`/`-dev` 后缀）→ 跳过步骤 3（不写 CHANGELOG）。
- **`false`**（正式版本）→ 继续步骤 3。

### 3. 同步 CHANGELOG（仅正式版本）

使用 `Skill` 工具调用 `my-changelog`，传入版本号 `<version>` 与区间 `<last_tag>..HEAD`。my-changelog 会归类改动（Features / Bug Fixes / Others）、整合简化后写入 `CHANGELOG.md` 并提交。其归类结果保留在上下文中，供步骤 5 生成 tag message，无需重新分析 commit。

### 4. 项目类型检测与版本一致性检查

#### 4a. 检测项目类型

扫描项目根目录的全部标记文件，收集所有命中的项目类型：

| 项目类型 | 标记文件 | reference |
|----------|----------|-----------|
| Rust/Cargo | `Cargo.toml` | `references/version-check-cargo.md` |
| Python | `pyproject.toml`、`setup.cfg`、`setup.py` | `references/version-check-python.md` |
| npm/Node.js | `package.json` | `references/version-check-npm.md` |
| Java/Maven | `pom.xml` | `references/version-check-java.md` |
| Java/Gradle | `build.gradle`、`build.gradle.kts` | `references/version-check-java.md` |

- 用 `test -f` 检查**所有**标记文件（非命中即停），记录全部命中的类型。
- **全部未命中** → 跳过版本一致性检查，直接到步骤 5。
- **单一命中** → 直接采用该类型。
- **多类型命中**（如 monorepo 同时存在 `Cargo.toml` 和 `package.json`）→ 用 `AskUserQuestion`（单选）让用户选择要检查的类型，选项仅列出命中的类型。

#### 4b. 加载版本检查规则

根据检测到的项目类型，`Read` 对应的 reference 文件（见上表）。

#### 4c. 执行一致性检查

按 reference 指引：
1. **动态版本检测**：先检查项目是否使用基于 git tag 的动态版本方案（如 Python 的 setuptools-scm、Java 的 git-commit-id-plugin）。命中则跳过检查，告知用户"项目使用动态版本方案，跳过配置文件校验"。
2. **读取项目配置版本**：从配置文件中提取当前版本号。
3. **版本号比较**：
   - Python 项目：将 `<version>` 按 reference 中的 PEP 440 映射规则转换为 PEP 440 格式后比较。
   - 其他项目：去掉 `<version>` 的 `v` 前缀后直接比较。
4. 一致 → 跳过步骤 4d。
5. 不一致 → 进入步骤 4d。

#### 4d. 不匹配时处理

用 `AskUserQuestion`（单选）提供以下选项：
- **"更新项目配置文件以匹配 tag `<version>`"**：按 reference 中的修复方法自动更新配置文件。修改后不提交，继续后续步骤。
- **"调整 tag 名称以匹配项目配置的版本"**：将项目配置中的版本号覆盖 `<version>`。若配置版本格式与 tag 格式不一致（如 Python PEP 440 `0.1.0a1`），先按 reference 的映射规则**反向转换**为 semver（`0.1.0a1` → `0.1.0-alpha.1`），再根据 `<last_tag>` 的 `v` 前缀惯例添加或省略前缀。调整后返回步骤 2 重新判断（可能在预发布/正式版本间切换，影响 CHANGELOG 是否写入）。
- **"继续执行，不修复版本差异"**：忽略差异，tag 和配置各自保持当前值。记录此决策到项目记忆。
- **"取消此次操作"**：终止流程，不做任何修改。

### 5. 生成 tag message

**正式版本**：基于步骤 3 my-changelog 的归类结果整形为 tag message 格式（与 CHANGELOG 条目同源，仅改呈现）：
- 自动生成一句概括性的大版本标题（中文，≤50 字符），概括本次版本的主要变化方向。
- 分类标题用 `##`（不含版本号标题行），按「首行标题 → 空行 → Markdown 正文」格式：

```
<概括性标题，≤50字符>

## Features

- 改动描述 1。

## Bug Fixes

- 修复描述 1。

## Others

- 其它改动 1。
```

- 无内容的分类直接省略，不输出空标题。

**预发布版本**：自行分析 commit 记录生成完整格式的 tag message：
- 以 `<version> 预发布` 作为概括性标题。
- 读取 `git log <last_tag>..HEAD`（`<last_tag>` 不存在时取全部历史），分析每条 commit 的标题+正文。
- 按与 my-changelog 相同的归类逻辑分为 Features / Bug Fixes / Others：
  - `Features`：仅新增功能（feat 类 commit）。
  - `Bug Fixes`：仅 bug 修复（fix 类 commit）。
  - 其余（重构、文档、CI、样式等）→ `Others`。
  - 同一版本内新增又删除的功能、引入又修复的 bug，互相抵消不写入。
  - 无内容的分类整体省略。
- 输出格式与正式版本一致：首行标题 + 空行 + `## Features` / `## Bug Fixes` / `## Others`。

### 6. 执行 git tag

```bash
git tag -a <version> -m "<message>"
```

- 正式版本：tag 打在步骤 3 my-changelog 产生的 CHANGELOG 提交上（若无新提交则打在 HEAD）。
- 预发布版本：tag 直接打在 HEAD。

### 7. 保存摘要到项目记忆

将以下内容保存到项目记忆：
- 版本号 `<version>`
- 是否为预发布版本
- 版本类型（Rust/Python/npm/Java/无）
- 版本一致性检查结果（一致/已修复/跳过/忽略差异）
- tag message 摘要（概括性标题）
