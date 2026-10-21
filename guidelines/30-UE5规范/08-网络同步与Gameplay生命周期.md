# UE5 · 网络同步与 Gameplay 生命周期

**所属域**: 30-UE5规范  **域版本**: 3.1.0  **日期**: 2026-10-21

> **上游依赖**：[00-行为规范](../00-行为规范/01-核心铁律与五阶执行模型.md) · [UE5 · 反射与宏](./05-反射与宏.md)。

---

## 23. 网络同步与 Gameplay 生命周期规范

### 23.1 生命周期自驱动（生命周期归属）
- 复制与能力初始化（`SetIsReplicatedByDefault(true)`、`InitAbilityActorInfo` 等）**必须由宿主 Actor 自身生命周期驱动**：
  - **服务器端**：在 `PossessedBy` / `PostInitializeComponents` 自驱动。
  - **客户端**：在 `OnRep_PlayerState` / `OnRep_Owner` 自驱动。
- **严禁在 GameMode 登录回调（如 `PostLogin`）中代劳调用客户端组件的网络初始化**（GameMode 仅存在于服务器，无法感知客户端网络状态与初始复制到达）。

```cpp
// ✅ 正确：宿主自驱动
void AMyPlayerState::PostInitializeComponents() {
    Super::PostInitializeComponents();
    if (HasAuthority()) { TryInitAbilitySystem(); }
}
void AMyPlayerState::OnRep_Owner() {
    Super::OnRep_Owner();
    TryInitAbilitySystem(); // 客户端网络到达后自驱动
}

// ❌ 错误：在 GameMode 回调中越权代劳（导致客户端初始化丢失或时序竞态）
void AMyGameMode::PostLogin(APlayerController* NewPlayer) {
    Super::PostLogin(NewPlayer);
    if (AMyPlayerState* PS = NewPlayer->GetPlayerState<AMyPlayerState>()) {
        PS->InitAbilitySystem(); // 错！客户端尚未网络就绪
    }
}
```

---

### 23.2 幂等创建（创建与初始化分离）
- **对象仅创建一次，后续永远复用**；严禁在生命周期回调中重复分配实例。
- **解耦创建与配置**：
  - **创建 (Creation)**：仅在构造函数或通过 `if (!Component)` 执行单次 `NewObject`。
  - **初始化 (Initialization)**：支持因角色重生（Respawn）或重新附身而被幂等多次调用（如刷新 ActorInfo、重新绑定委托）。

```cpp
// ✅ 正确：创建单次，配置支持安全幂等调用
void AMyPlayerState::TryInitAbilitySystem() {
    if (!AbilitySystemComponent) {
        AbilitySystemComponent = NewObject<UAbilitySystemComponent>(this, TEXT("ASC"));
        AbilitySystemComponent->SetIsReplicated(true);
    }
    // 幂等刷新 ActorInfo，支持重生与切图
    AbilitySystemComponent->InitAbilityActorInfo(this, GetPawn());
}

// ❌ 错误：每次调用重新分配，覆盖旧实例破坏网络句柄
void AMyPlayerState::InitAbilitySystem() {
    AbilitySystemComponent = NewObject<UAbilitySystemComponent>(this); // 错！旧对象被 GC 导致悬垂与断裂
}
```

---

### 23.3 身份分叉（三路职责分离与默认不做原则）
- 初始化第一步必须检查网络身份（`HasAuthority()`、`IsLocallyControlled()`）。
- **默认不做（Default No-Op）**：未明确需要执行的端位使用 Guard Clause 提前返回，严禁全端无差别执行。

| 端位角色 | 判定条件 | 核心职责 | 严禁行为 |
|---|---|---|---|
| **服务器 (Authority)** | `HasAuthority()` | 权威属性计算、授予技能、状态裁决、生成权威 Actor | 严禁创建 UMG UI、处理本地输入、播放纯本地音效 |
| **本地客户端 (Autonomous)** | `!HasAuthority() && IsLocallyControlled()` | 创建本地 HUD / UI、输入映射、GAS 能力本地预测 | 严禁执行权威扣血/修改属性、直接变更不可预测全局状态 |
| **远端客户端 (Simulated)** | `!HasAuthority() && !IsLocallyControlled()` | 被动同步属性、播放受击特效/音效、位移平滑插值 | 严禁创建本地 HUD、绑定输入、执行服务端权威计算 |

```cpp
// ✅ 正确：身份分叉，按端位执行，未匹配默认不做
void AMyCharacter::InitPlayerContext() {
    if (HasAuthority()) {
        GrantDefaultAbilities(); // 仅服务器权威授予
    }
    if (IsLocallyControlled()) {
        SetupLocalHUD();         // 仅本地玩家创建 UI
    }
    // 远端模拟代理默认不做
}
```
