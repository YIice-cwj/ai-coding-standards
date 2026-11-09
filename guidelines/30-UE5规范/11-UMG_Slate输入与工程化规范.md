# UE5 · UMG、Slate、输入与工程化

**所属域**: 30-UE5规范  **域版本**: 3.6.0  **日期**: 2026-11-09  **引擎**: Unreal Engine 5.1+

> **SSOT 声明**：UMG/Slate UI、Enhanced Input、模块与插件、本地化与自动化测试的唯一事实源。
> **关联文档**：[类结构与接口](./02-类结构接口与头文件.md) · [错误、日志与测试](./07-错误日志测试与构建.md) · [网络与 Gameplay 生命周期](./08-网络同步与Gameplay生命周期.md) · [通用职责边界](../10-通用代码规范/02-架构健壮性与工程安全.md)

---

## 1. UMG 与 Slate

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-UE-UI-BIND]** | MUST | 必需控件使用 `meta = (BindWidget)`，可选控件用 `BindWidgetOptional`；在 `NativeConstruct` 中校验绑定 | 运行时空绑定崩溃；用 `FindWidget` 到处查找；UI 直接修改业务数据或持久化 |
| **[R-UE-UI-LIFE]** | MUST | 在 `NativeConstruct` 绑定委托/定时器，在 `NativeDestruct` 解绑/清理 | 只绑定不清理，导致控件销毁后回调野指针 |
| **[R-UE-UI-TICK]** | MUST | UI 默认不依赖 Tick；必须 Tick 时仅做轻量插值与视觉反馈 | 在 UI Tick 中做网络请求、业务计算、频繁字符串拼接 |
| **[R-UE-UI-TEXT]** | MUST | 所有玩家可见文本使用 `FText` + 本地化 Key（`LOCTEXT`/`NSLOCTEXT`） | `FString` 直接显示；硬编码文案；拼接整句导致无法本地化 |
| **[R-UE-SLATE]** | MUST | Slate 在 `Construct` 构建控件树；`OnPaint` 仅绘制；重逻辑放事件/命令 | `OnPaint` 中做业务计算、加载资源或频繁分配；无失效控制的重绘 |

```cpp
UCLASS()
class UMyHudWidget : public UUserWidget {
    GENERATED_BODY()

protected:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;

    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UTextBlock> TitleText;
};
```

```cpp
void SMyPanel::Construct(const FArguments& InArgs) {
    ChildSlot[
        SNew(STextBlock).Text(NSLOCTEXT("MyPanel", "Title", "Inventory"))
    ];
}
```

---

## 2. Enhanced Input

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-UE-INPUT-ENHANCED]** | MUST | 统一使用 `UEnhancedInputComponent` + `UInputAction` + `UInputMappingContext` | 混用旧版 `BindAction`/Axis Mapping；在代码中散落硬编码按键 |
| **[R-UE-INPUT-CONTEXT]** | MUST | 在 Possess/BeginPlay 添加 Mapping Context，在 UnPossess/EndPlay 移除；明确优先级 | 重复添加 Context；角色切换后旧 Context 残留 |
| **[R-UE-INPUT-MODE]** | MUST | UI 模态/菜单打开时切换输入模式并消费输入；关闭后恢复游戏输入 | UI 打开时角色仍响应移动/攻击；输入模式与 UI 状态不同步 |
| **[R-UE-INPUT-CONSUME]** | MUST | 关键动作显式 `ConsumeInput`，避免同一输入触发多个系统 | 一个按键同时触发 UI 与 Gameplay；重复绑定同一 Action |

```cpp
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) {
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    if (auto* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent)) {
        EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::HandleMove);
    }
}
```

---

## 3. 模块、插件与工程化

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-UE-MODULE]** | MUST | `Build.cs` 严格区分 `PublicDependencyModuleNames` 与 `PrivateDependencyModuleNames`；显式 `CppStandard`；禁止模块循环依赖 | 运行时模块依赖 Editor 模块；把所有依赖塞进 Public；循环依赖 |
| **[R-UE-PLUGIN]** | MUST | 插件使用 `.uplugin` 描述符；模块 Type 明确（Runtime/Editor/Developer）；内容与代码职责分离 | 运行时插件依赖 Editor 模块；插件内容硬编码绝对路径 |
| **[R-UE-TEST]** | MUST | 核心 Gameplay 逻辑使用 Automation Test；异步测试用 Latent/事件同步；禁 `FPlatformProcess::Sleep` 盲等 | 只靠手测；测试依赖关卡/顺序；sleep 盲等 |
| **[R-UE-L10N]** | MUST | 本地化文本使用 `FText` 与命名空间 Key；数字/日期/货币使用文化感知格式化 | 硬编码英文/中文文案；用 `FString` 拼接本地化句子 |

---

## 4. 自检清单

- [ ] 必需控件 `BindWidget` 已校验，可选控件使用 `BindWidgetOptional`。
- [ ] 委托/定时器在 `NativeDestruct` 解绑清理，无野指针回调。
- [ ] UI 无业务 Tick；玩家可见文本全部 `FText` 且可本地化。
- [ ] Slate `OnPaint` 仅绘制，重逻辑在事件/命令层。
- [ ] 输入统一 Enhanced Input，无旧版输入混用。
- [ ] Mapping Context 随 Possess/UnPossess 正确添加与移除。
- [ ] UI 模态时输入模式切换并消费输入，关闭后恢复。
- [ ] Build.cs 依赖 public/private 正确，无 Editor 依赖泄漏到 Runtime。
- [ ] 插件模块类型与内容职责清晰，无绝对路径硬编码。
- [ ] 核心 Gameplay 逻辑有 Automation Test，异步测试无 sleep 盲等。
