# Bug 根因诊断与全局修复体系 (Root-Cause Bug Fixing & Global Impact)

**所属域**: 00-行为规范  **域版本**: 2.4.0  **日期**: 2026-10-26  **类型**: 全局行为协议（规则 SSOT）

> **SSOT 声明**：Bug 根因溯源准则、5-Whys 逆推、爆炸半径测距与同类全景排查 (Pattern Sweep) 的唯一权威源（对应铁律 **B7**）。
> **关联文档**：[核心铁律](./01-核心铁律与五阶执行模型.md) · [禁止清单与预检](./03-禁止清单与交付预检.md) · [代码审查规范](../50-审查规范/01-代码审查规范.md)

---

## 一、 核心铁律：B7 根因溯源，全局研判

| 规则 ID | 核心公理 | 强制行为 (DO) | 严禁行为 (DON'T / 一票否决) |
|:---:|---|---|---|
| **B7** | **根因溯源，全局研判** | 逆推源头破坏的不变式；全局评估上下游爆炸半径；全景排查同类实现；产出客观验证闭环 | 报错点机械判空/吞异常掩盖根因（破坏 Fail-Fast）；未评估调用方契约；修局部漏同类 |

---

## 二、 四阶根治协议 (The 4-Phase Protocol)

```
[故障现场] ──► Phase 1: 根因溯源 ──► Phase 2: 全局研判 ──► Phase 3: 最优方案权衡 ──► Phase 4: 闭环验证 ──► [交付方案]
```

### Phase 1: 根因溯源 (Trace Root Cause)
- **区分现场与根因**：崩溃/空指针只是受害现场，严禁在受害点机械添加 `if (!ptr) return;` 或空 `catch`。
- **5-Whys 逆推准则**：顺数据流与调用栈向上逆推，直至锁定最初破坏系统不变式 (Invariant) 的源头位置。
- **准出门禁**：明确定义“何处、因何种时序或逻辑缺失导致非法状态进入系统”。

### Phase 2: 全局研判 (Global Blast Radius)
- **三向测距模型**：
  1. **向上测距 (Callers)**：排查所有调用方，核验改动入参/返回值/异常是否打破上游假设。
  2. **向下测距 (Callees)**：修正状态后，下游依赖模块是否引发级联计算异常。
  3. **旁路测距 (Concurrency & Lifecycle)**：是否波及并发时序、锁竞争或对象生命周期（GC/智能指针）。
- **全景同类排查 (Pattern Sweep)**：检索全库是否存在相同模式逻辑、对称实现（如 Encode/Decode, Read/Write）或同基类派生类，一并纳入修复。
- **定级门禁**：涉及跨模块契约、公共 API 或状态机变更时，必须升级为 **L3 任务**，先出计划文档 (B2)。

### Phase 3: 最优方案权衡 (Clean Fix)
| 方案维度 | 方案 A：地表止痛 (Band-Aid) | 方案 B：源头根治 (Root Cure) [首选] | 方案 C：契约重塑 (Architecture) |
|---|---|---|---|
| **位置与做法** | 报错点就地判空 / 吞异常 | 状态产生源头修正，保证前置条件 | 引入强类型包装 / RAII / 不变量重塑 |
| **根治程度** | ❌ 零（错误继续隐式潜伏） | ✅ 彻底根除非法状态 | ✅ 编译期/架构层彻底杜绝 |
| **决策倾向** | **坚决打回禁止** | **默认首选执行** | 跨模块严重架构缺陷时升级评估 |

### Phase 4: 闭环验证 (Proof of Cure)
- **复现证明 (Red)**：先给出可复现该 Bug 的最小单元测试或严格因果逻辑推导。
- **根除证明 (Green)**：实施修复后，该复现用例稳定通过，自证非法状态无法再次发生。
- **零回归验证 (Regression Guard)**：对 Phase 2 研判的所有调用路径进行回归测试，严禁用 `sleep` 盲等。

---

## 三、 正反模式对比 (Anti-Pattern vs. Best Practice)

```cpp
// 场景：网络延迟下 UI 访问 PlayerState 的 GuildInfo 出现空解引用崩溃

// ❌ 反例：地表止痛（受害点判空，公会名永久空白卡死，下游按钮继续异常）
void UGuildPanel::UpdateGuildName() {
    if (!MyPlayerState || !MyPlayerState->GuildInfo) { return; }
    GuildText->SetText(MyPlayerState->GuildInfo->GuildName);
}

// ✅ 正例：B7 溯源时序竞争，源头确立网络到达契约与委托监听，彻底根治
void AMyPlayerState::OnRep_GuildInfo() {
    OnGuildInfoReady.Broadcast(GuildInfo);
}
void UGuildPanel::NativeConstruct() {
    Super::NativeConstruct();
    GetPlayerState()->OnGuildInfoReady.AddDynamic(this, &UGuildPanel::OnGuildInfoReady);
}
```

---

## 四、 交付核查清单 (B7 Checklist)
- [ ] 已锁定非法状态生成的根因源头，杜绝就地机械判空与吞异常。
- [ ] 已完成三向测距（上游调用方、下游依赖、并发/生命周期）。
- [ ] 已全景排查全库同类与对称实现 (Pattern Sweep)。
- [ ] 具备明确的复现证据 (Red) 与根治验证闭环 (Green)。
