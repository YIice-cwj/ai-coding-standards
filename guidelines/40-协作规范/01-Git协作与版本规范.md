# Git 协作与版本规范 (Git Collaboration & Versioning Standards)

**所属域**: 40-协作规范  **域版本**: 2.4.0  **日期**: 2026-11-07  **类型**: 全局通用协作规范（规则 SSOT）

> **SSOT 声明**：**“提交 / 推送 / PR / 发布分别授权” (B-GIT)**、提交信息、分支模型、PR/MR 流程、合并策略、发布与 SemVer 的唯一权威源。
> **关联文档**：[核心铁律](../00-行为规范/01-核心铁律与五阶执行模型.md) · [代码审查](../50-审查规范/01-代码审查规范.md) · [文档治理](./02-文档治理与ADR规范.md)。

---

## 1. 提交与远端操作权限 (B-GIT SSOT)

| 规则 ID | 核心公理 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|:---:|---|---|---|
| **B-GIT** | **提交与远端操作严格受控** | 仅在用户显式发出“提交/commit”指令时执行本地 `git commit`；`git push` 必须另获“推送/push”明确指令；PR 创建/合并、tag、release、force push 同样需明确授权 | 未获指令擅自 commit/push/PR/merge/tag/release；把“提交”推定授权推送或发布 |

- **授权边界（独立不可推定）**：
  - “提交/commit”仅授权本地 `git commit`。
  - “推送/push”是独立授权，不得由提交指令推定。
  - PR 创建/合并、打 tag、发布 release、force push、重写共享历史均为独立远端操作，必须逐项授权。
- **工作区暂存契约**：未获提交指令前，AI 必须将修改保留在工作区，仅汇报改动摘要与验证依据，等待用户审查决定。
- **B-SEC 破坏性操作**：`git reset --hard`、`git clean -f -d`、`git push --force` 必须获得显式确认；公共分支历史回滚优先 `git revert`。

---

## 2. 提交信息结构化契约 (Conventional Commits)

提交信息必须采用 Conventional Commits 格式：

```text
<type>(<scope>): <summary <= 50 字>

<body: 为什么改 + 关键影响>
```

- **类型标签**：`feat`（新功能）、`fix`（Bug 修复）、`docs`（文档）、`style`（纯格式）、`refactor`（重构）、`perf`（性能）、`test`（测试）、`build`（构建/依赖）、`ci`（流水线）、`chore`（杂项）、`revert`（回滚）。
- **scope 可选**：模块、域或目录名，如 `feat(git): ...`、`docs(10): ...`。
- **破坏性变更**：type 后加 `!`（如 `feat(api)!: ...`），并在 footer 写 `BREAKING CHANGE: ...`。
- **原子提交**：一个提交只表达一个逻辑变更；格式化/重命名与业务变更分开提交。
- **正文解释 Why**：正文说明动机、权衡与影响，避免只复述 Diff。

---

## 3. 分支模型与 PR/MR 流程

- **主干可发布**：`main` 随时可构建、可发布；功能分支从最新 `main` 创建，短生命周期。
- **分支命名**：`类型/简述`（如 `feat/user-auth`, `fix/null-pointer`, `docs/adr-0007`）。
- **PR/MR 描述**：必须包含变更目的、实现要点、验证证据、风险与回滚方式；关联 Issue/ADR/L3 计划。
- **合并准入**：CI 全绿、审查通过、无未解决讨论、文档与版本已同步；线性历史优先。
- **小步提交**：单个 PR/MR 建议 ≤400 行有效变更；跨 ≥3 模块或混合功能/重构/格式化时必须拆分（与 [50/01](../50-审查规范/01-代码审查规范.md) 一致）。
- **AI 权限**：未获明确指令，AI 严禁创建 PR/MR、合并、打 tag 或发布 release。

---

## 4. 合并策略与历史管理

- **默认合并**：功能分支使用 Squash Merge 合入 `main`，保持主干线性；发布分支可使用 Merge Commit 保留发布节点。
- **rebase 边界**：仅限个人未共享分支；共享分支禁止 rebase/force push。
- **冲突解决**：合并前同步最新 `main`；解决冲突后必须重新编译并跑相关测试；严禁盲目 `-X ours`/`-X theirs`。
- **公共历史回滚**：使用 `git revert` 生成反向提交；严禁用 `reset --hard` 改写已推送历史。
- **保护分支**：`main` 开启分支保护，要求 CI、审查与必要审批；禁止直接推送（除非用户显式授权）。

---

## 5. 标签、发布与 CHANGELOG

- **标签**：使用 annotated tag `vX.Y.Z`；支持时启用签名；标签只指向通过 CI 的发布提交。
- **版本**：遵循 SemVer。Major 破坏性变更、Minor 向后兼容新增、Patch 修复。
- **CHANGELOG**：遵循 Keep a Changelog；分类至少包含 Added / Changed / Deprecated / Removed / Fixed / Security；禁止直接粘贴提交日志。
- **热修复**：从发布 tag 创建 `hotfix/...`，修复后提升 Patch 版本，并回合 `main`。
- **发布权限**：push tag、创建 release、发布制品均需明确指令；发布说明必须包含验证证据与回滚路径。

---

## 6. Git Hooks 与 CI 门禁

- **pre-commit**：格式化、Lint、机密扫描；**pre-push**：单元测试与静态检查。
- **CI 必跑**：构建、测试、覆盖率、Lint/类型检查、依赖与安全检查；任一门禁失败阻断合并。
- **禁止绕过**：严禁 `--no-verify` 跳过 Hook（除非用户显式授权）；Hook 失败必须修复根因。
- **产物与凭据**：CI 不打印机密；构建产物、缓存与临时文件不得入库。

---

## 7. 仓库过滤与大文件存储 (LFS)

- **`.gitignore` 过滤**：严禁检入编译中间体、系统缓存（`.DS_Store`）与敏感凭据（`.env`）；UE5 必须过滤 `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`。
- **Git LFS**：多媒体资产、模型、纹理及 UE5 二进制文件（`.uasset`, `.umap`）必须配置 LFS，严禁直接检入普通 Git 仓库。
- **子模块**：固定 commit SHA，禁止浮动分支引用；升级子模块需评审并记录变更原因。

---

## 8. 自检清单

- [ ] 未获明确指令，未执行 commit/push/PR/merge/tag/release。
- [ ] 提交信息符合 Conventional Commits，正文说明 Why。
- [ ] 分支从最新 `main` 创建，命名规范，PR 描述完整。
- [ ] CI、审查、文档与版本门禁全部通过。
- [ ] 合并策略符合规范，共享历史未被 force push/rebase 改写。
- [ ] 冲突解决后已重新编译并跑相关测试。
- [ ] tag/release 指向通过 CI 的提交，CHANGELOG 已更新。
- [ ] Hook 未被绕过，CI 无机密泄露与构建产物入库。
- [ ] `.gitignore`/LFS/子模块配置正确。
