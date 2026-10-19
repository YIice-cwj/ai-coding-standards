# UE5 · 网络同步与 Gameplay 生命周期

**所属域**: 30-UE5规范  **域版本**: 3.0.0  **日期**: 2026-10-19

> **上游依赖**：[AI 行为规范](../00-行为规范/01-核心铁律与五阶执行模型.md) · [UE5 · 反射与宏](./05-反射与宏.md)。
> **拆分来源**：由原《代码规范(C++UE5)》§23 拆分而来（域版本 3.0.0）。

---

## 23. 网络同步与 Gameplay 生命周期规范

> **UE5 特化规范**：在多人网络游戏与 GAS（Gameplay Ability System）架构下，对象生命周期与网络同步具有严格的端位与时序约束，必须严格遵循以下原则。

### 23.1 时序归属（生命周期自驱动）

- 复制相关的初始化（开启复制 `SetIsReplicatedByDefault(true)`、注册属性集 `AttributeSet`、`InitAbilityActorInfo` 等）**必须**由宿主 Actor（如 `APlayerState` / `APawn`）根据自身生命周期自驱动触发。
- **严禁**在 `AGameModeBase` / `AGameMode` 的生命周期回调或登录事件（如 `PostLogin`、`RestartPlayer`、`HandleStartingNewPlayer`）中代劳调用 PlayerState 或 Pawn 的网络/复制初始化函数。
- **机理与原因**：
  - GameMode 仅存在于服务器（Server-Only），其回调仅反映服务器端业务步骤"逻辑就绪"，根本无法感知客户端 Actor 是否生成、属性初次复制是否送达（"网络就绪"）。
  - 在 GameMode 回调中强行代劳，会导致客户端缺失关键网络初始化（如客户端未执行 `InitAbilityActorInfo` 导致能力无法预测、动画无法播放、UI 监听断裂），或造成多端严重的时序竞态。
- **驱动时机约定**：
  - **服务器端**：在 `PossessedBy` / `PostInitializeComponents` 等生命周期节点自驱动。
  - **客户端**：在 `OnRep_PlayerState` / `OnRep_Owner` / `ClientInitialize` 等网络通知时机自驱动。

**正例**：
```cpp
// ✅ 正确：PlayerState / Pawn 按自身生命周期自驱动初始化
void AMyPlayerState::PostInitializeComponents() {
    Super::PostInitializeComponents();
    if (HasAuthority()) {
        TryInitAbilitySystem();
    }
}

void AMyPlayerState::OnRep_Owner() {
    Super::OnRep_Owner();
    // 客户端在网络所有者就绪时自驱动
    TryInitAbilitySystem();
}
```

**反例**：
```cpp
// ❌ 错误：在 GameMode 登录回调中越权代劳网络初始化
void AMyGameMode::PostLogin(APlayerController* NewPlayer) {
    Super::PostLogin(NewPlayer);
    if (AMyPlayerState* PS = NewPlayer->GetPlayerState<AMyPlayerState>()) {
        // 错！外部只知道逻辑就绪，客户端此时根本尚未"网络就绪"，会导致客户端初始化丢失
        PS->InitAbilitySystem();
    }
}
```

### 23.2 幂等创建（创建与初始化分离）

- 对象实例一经创建，后续永远复用，**禁止**重复创建覆盖。
- **必须**严格解耦"对象创建"（Creation / Allocation）与"状态初始化"（Initialization / Configuration）：
  - **创建**：仅在对象生命周期伊始执行一次（如在构造函数中使用 `CreateDefaultSubobject`，或惰性加载时通过 `if (!instance)` 保护执行单次 `NewObject`）。
  - **初始化**：支持幂等多次调用。负责配置状态、设置 Owner/AvatarActor、注册属性集、幂等绑定委托等，**绝不能**重新分配（Reallocate）对象实例。
- **机理与原因**：
  - 在网络游戏中，Actor 重生（Respawn）、Possess 重新附身、无缝切图（Seamless Travel）或断线重连时，生命周期函数（如 `PossessedBy`、`OnRep_PlayerState`）会被**多次重复调用**。
  - 若每次初始化都重新创建对象（如重新分配 ASC 或属性集），将导致旧对象被 GC 回收后产生悬垂指针、已绑定的委托与监听失效、网络同步句柄断裂。
- **工程实践提示**：类似项目中的 `TryInitAbilitySystem()` 与 `InitAttributeSet()` 均须按此原则收敛，确保存续实例始终复用。

**正例**：
```cpp
// ✅ 正确：创建与初始化解耦，多次调用安全幂等
void AMyPlayerState::TryInitAbilitySystem() {
    if (!AbilitySystemComponent) {
        // 首次创建（或构造函数已创建）：仅执行一次
        AbilitySystemComponent = NewObject<UAbilitySystemComponent>(this, TEXT("AbilitySystemComponent"));
        AbilitySystemComponent->SetIsReplicated(true);
        AbilitySystemComponent->SetReplicationMode(EGameplayEffectReplicationMode::Mixed);
    }

    if (!AttributeSet) {
        // 属性集实例仅创建一次，后续永远复用
        AttributeSet = NewObject<UMyAttributeSet>(this, TEXT("AttributeSet"));
    }

    // 后续可被多次幂等调用的初始化逻辑（如重新附身时刷新 ActorInfo）
    AActor* AvatarActor = GetPawn();
    AbilitySystemComponent->InitAbilityActorInfo(this, AvatarActor);
}
```

**反例**：
```cpp
// ❌ 错误：每次初始化都重新分配实例，覆盖现有对象
void AMyPlayerState::InitAbilitySystem() {
    // 错！重生或二次调用时重新创建，破坏已有的网络同步状态与委托绑定
    AbilitySystemComponent = NewObject<UAbilitySystemComponent>(this);
    AttributeSet = NewObject<UMyAttributeSet>(this);
    AbilitySystemComponent->InitAbilityActorInfo(this, GetPawn());
}
```

### 23.3 身份分叉（三路职责分离与默认不做原则）

- 任何初始化与 Gameplay 逻辑的第一步，**必须**首先显式检查网络身份与端位角色（`HasAuthority()`、`IsLocallyControlled()` / `IsLocalController()`）。
- **必须**将**服务器（Authority）**、**本地客户端（Autonomous Proxy / Local Client）**、**远端客户端（Simulated Proxy / Remote Client）** 三路职责明确分离。
- **必须遵循防御性设计：默认不做（Default No-Op），按需开启**。未明确需要执行的端位，必须提前返回（Guard Clause），严禁凭直觉无差别全端执行。

**三路职责矩阵**：

| 端位角色 | 判定条件 | 核心职责 | 严禁行为 |
|---|---|---|---|
| **服务器**（Authority） | `HasAuthority()` | 权威属性计算、GAS 授予 Ability / GameplayEffect、核心状态裁决、生成权威 Actor | 严禁创建 Slate/UMG、处理本地输入、播放纯本地音画 |
| **本地客户端**（Autonomous Proxy） | `!HasAuthority() && IsLocallyControlled()` | 本地 HUD / UI 创建与数据绑定、本地输入映射、GAS 能力本地预测、相机震屏与第一人称表现 | 严禁执行权威扣血/修改属性、直接变更不可预测的全局状态 |
| **远端客户端**（Simulated Proxy） | `!HasAuthority() && !IsLocallyControlled()` | 表现层状态被动同步、动画蒙太奇播放、位置插值平滑、受击通用特效与音效 | 严禁创建本地 HUD、绑定输入、执行本地特权逻辑或服务端权威计算 |

**正例**：
```cpp
// ✅ 正确：首要检查端位身份，职责清晰，未匹配端位默认不做
void AMyCharacter::InitPlayerContext() {
    const bool bIsAuthority = HasAuthority();
    const bool bIsLocal = IsLocallyControlled();

    if (bIsAuthority) {
        // 服务器端：仅负责授予初始技能与权威状态配置
        GrantDefaultAbilities();
    }

    if (bIsLocal) {
        // 本地玩家端：仅负责创建本地 HUD 与输入绑定
        SetupLocalHUD();
        BindInputActions();
    }

    // 远端模拟客户端（!bIsAuthority && !bIsLocal）：默认不做，完全依赖属性与状态复制驱动表现
}
```

**反例**：
```cpp
// ❌ 错误：缺少身份分叉，全端无差别执行
void AMyCharacter::InitPlayerContext() {
    // 错！Dedicated Server 会尝试创建 Slate UI 导致崩溃；远端模拟代理也会创建本地 HUD
    CreatePlayerHUD();
    // 错！客户端也尝试调用仅服务器有效的授予技能
    GrantDefaultAbilities();
}
```
