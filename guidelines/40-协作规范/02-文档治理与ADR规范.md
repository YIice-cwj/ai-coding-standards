# 文档治理与 ADR 规范 (Documentation Governance & ADR)

**所属域**: 40-协作规范  **域版本**: 2.4.0  **日期**: 2026-11-07  **类型**: 全局通用协作规范（规则 SSOT）

> **SSOT 声明**：README、ADR（架构决策记录）、API 文档、CHANGELOG 与文档新鲜度治理的唯一事实源。
> **关联文档**：[Git 协作](./01-Git协作与版本规范.md) · [API 契约](../10-通用代码规范/05-API与接口契约规范.md) · [代码审查](../50-审查规范/01-代码审查规范.md) · [ADR 模板](../templates/ADR_TEMPLATE.md)。

---

## 1. README 基线

每个可交付仓库的 `README.md` 必须至少包含：

- **是什么 / 为什么**：项目定位、解决的问题与核心能力。
- **快速开始**：环境要求、安装/构建/运行命令，命令必须可直接复制执行。
- **目录结构**：关键目录与职责，链接到详细规范或文档。
- **配置与密钥**：配置来源、必需环境变量、机密管理方式（不写真实值）。
- **验证方式**：测试、Lint、覆盖率与 CI 命令。
- **版本与许可证**：当前版本、版本登记处、License。

**红线**：禁止过期命令、失效链接、与实现不符的截图或描述。

---

## 2. ADR（架构决策记录）

### 2.1 何时必须写 ADR

- L3/L4 架构决策、跨模块契约、数据存储/协议迁移。
- 不可逆或高迁移成本的技术选型。
- 有意接受的技术债与权衡（如“暂不支持多租户”）。

### 2.2 ADR 规则

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-DOC-ADR]** | MUST | 使用 [ADR 模板](../templates/ADR_TEMPLATE.md)；存放于 `docs/adr/NNNN-title.md`；包含 Context/Decision/Alternatives/Consequences | 只在聊天或 PR 评论里做架构决策；无备选方案与后果分析 |
| **[R-DOC-ADR-IMMUT]** | MUST | ADR 一旦 Accepted 不再改写；被替代时新建 ADR 并标注 `Supersedes` | 直接修改已 Accepted 的 ADR 掩盖历史 |
| **[R-DOC-ADR-LINK]** | MUST | PR/L3 计划中链接相关 ADR；决策变更同步更新索引 | ADR 与实现脱节；无索引导致无法检索 |

```markdown
# ADR-0007: 选择游标分页替代 Offset 分页

- **Status**: Accepted
- **Date**: 2026-11-07
- **Deciders**: Backend Team
- **Related**: L3 计划 / PR #123

## Context
订单量超过千万，Offset 分页导致深分页全表扫描与数据漂移。

## Decision
列表接口统一使用基于 `(created_at, id)` 的游标分页。

## Alternatives Considered
| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| Offset 分页 | 实现简单 | 深分页慢、数据漂移 | 否决 |
| 游标分页 | 稳定、可扩展 | 客户端需适配 | 采纳 |

## Consequences
- 正向：深分页性能稳定，数据不漂移。
- 权衡：旧客户端需升级；需维护游标编码。
```

---

## 3. API 与接口文档

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-DOC-API]** | MUST | 以机器可读契约为准（OpenAPI/Protobuf/JSON Schema）；示例请求/响应可执行；错误码与版本策略完整 | 手写文档与实现不一致；缺少错误码/版本说明 |
| **[R-DOC-API-GEN]** | MUST | 能从代码/契约生成的文档优先自动生成；生成物纳入 CI 校验 | 手工复制字段清单；契约变更未同步文档 |
| **[R-DOC-API-EX]** | MUST | 示例覆盖成功、参数错误、权限错误与限流；示例数据脱敏 | 示例含真实 Token/PII；只给成功示例 |

接口设计细则见 [10/05 API 与接口契约规范](../10-通用代码规范/05-API与接口契约规范.md)。

---

## 4. CHANGELOG

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-DOC-CHANGELOG]** | MUST | 遵循 Keep a Changelog + SemVer；分类 Added/Changed/Deprecated/Removed/Fixed/Security；关联 Issue/PR | 直接粘贴 `git log`；无版本号；破坏性变更未标注 |
| **[R-DOC-CHANGELOG-LINK]** | MUST | CHANGELOG 条目链接到 ADR/PR/Issue；发布说明从中提取 | 发布说明与 CHANGELOG 两套口径 |

---

## 5. 文档评审与新鲜度

- **Docs as Code**：文档与代码同 PR 评审；代码行为变更必须同步更新相关文档。
- **单一事实源**：同一规则只在一处定义，其他位置链接引用，禁止复制粘贴形成双源。
- **链接与命令校验**：CI 执行相对链接检查；README/文档中的命令必须可执行。
- **过期清理**：失效文档、截图、配置示例必须删除或标注废弃，禁止长期悬挂。
- **安全与隐私**：文档中禁止真实密钥、Token、PII 与内部敏感地址。
- **Owner**：每个长期文档明确维护者；无主文档在评审中标记并处理。

---

## 6. 自检清单

- [ ] README 包含定位、快速开始、结构、配置、验证、版本与许可证。
- [ ] 架构决策已写 ADR，包含备选方案与后果分析。
- [ ] Accepted ADR 未被改写，被替代时新建并标注 Supersedes。
- [ ] API 文档以机器可读契约为准，示例可执行且脱敏。
- [ ] CHANGELOG 遵循 Keep a Changelog + SemVer，条目关联 Issue/PR。
- [ ] 文档与代码同 PR 更新，无过期命令、失效链接与双源规则。
- [ ] 文档中无真实密钥、Token、PII 或内部敏感地址。
- [ ] 长期文档有明确 Owner，无主文档已处理。
