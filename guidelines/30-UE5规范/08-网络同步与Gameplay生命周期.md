# UE5 · 网络同步与 Gameplay 生命周期

**所属域**: 30-UE5规范  **域版本**: 3.2.0  **日期**: 2026-10-26  **引擎**: Unreal Engine 5.1+

> **SSOT 依赖**：[00-行为规范](../00-行为规范/01-核心铁律与五阶执行模型.md) · [UE5 · 反射与宏](./05-反射与宏.md)。

---

## 1. 生命周期自驱动与时序安全

- **自驱动原则**：网络组件与 GAS 能力初始化必须由宿主 Actor 自身生命周期驱动：
  - **服务器端**：在 `PossessedBy` 或 `PostInitializeComponents` 中触发初始化。
  - **客户端**：在 `OnRep_PlayerState` 或 `OnRep_Owner` 中触发初始化。
- **严禁越权代劳**：**严禁在 GameMode 登录回调（如 `PostLogin`）中代劳调用客户端组件的网络初始化**（GameMode 仅存在于服务器，无法感知客户端连接与初始复制时序）。

```cpp
// ✅ 正确：宿主自驱动（时序安全）
void AMyPlayerState::PostInitializeComponents() {
    Super::PostInitializeComponents();
    if (HasAuthority()) { TryInitAbilitySystem(); }
}
void AMyPlayerState::OnRep_Owner() {
    Super::OnRep_Owner();
    TryInitAbilitySystem(); // 客户端网络到达后自驱动
}
```

---

## 2. 幂等创建（创建与配置分离）

- **单次创建**：组件或子对象仅在构造函数或通过 `if (!Comp)` 执行单次 `NewObject`，后续永远复用；严禁在生命周期回调中重复分配实例（防止覆盖句柄造成 GC 悬垂）。
- **幂等刷新**：初始化方法（如 `InitAbilityActorInfo`）必须设计为可被多次安全调用，以支持角色重生（Respawn）与切图。

```cpp
// ✅ 正确：组件仅创建一次，配置支持幂等多次调用
void AMyPlayerState::TryInitAbilitySystem() {
    if (!AbilitySystemComponent) {
        AbilitySystemComponent = NewObject<UAbilitySystemComponent>(this, TEXT("ASC"));
        AbilitySystemComponent->SetIsReplicated(true);
    }
    AbilitySystemComponent->InitAbilityActorInfo(this, GetPawn());
}
```

---

## 3. 身份分叉：三路职责分离与默认不做原则

逻辑首行必须判定网络端位角色；未被当前端位认领的职责，通过 Guard Clause 提前返回（默认不做原则）：

| 端位角色 | 判定条件 | 核心专属职责 | 严禁行为 (DON'T / 一票打回) |
|---|---|---|---|
| **服务器 (Authority)** | `HasAuthority()` | 权威数值计算、技能授予、状态裁决、生成权威 Actor | 严禁创建 UMG UI、处理本地输入、播放纯本地音效 |
| **本地客户端 (Autonomous)**| `!HasAuthority() && IsLocallyControlled()` | 创建本地 HUD / UI、输入映射、GAS 能力本地预测 | 严禁执行权威扣血/修改属性、变更不可预测全局状态 |
| **远端代理 (Simulated)** | `!HasAuthority() && !IsLocallyControlled()` | 被动同步属性、播放受击特效/音效、位移平滑插值 | 严禁创建本地 HUD、绑定输入、执行权威计算 |

```cpp
// ✅ 正确：身份三路分叉，未匹配端位默认不做
void AMyCharacter::InitPlayerContext() {
    if (HasAuthority()) { GrantDefaultAbilities(); }       // 仅服务器执行
    if (IsLocallyControlled()) { SetupLocalHUD(); }        // 仅本地玩家执行
    // 模拟代理默认不做任何额外操作
}
```
