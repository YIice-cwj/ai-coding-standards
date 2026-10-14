# UE5 C++ 代码规范 (UE5 C++ Coding Standards)

**版本**: 2.1.0  **日期**: 2026-10-14

> **行为规范继承**：AI 编码助手在执行本规范代码任务时，**必须严格遵循 [AI行为规范.md](./AI行为规范.md)**（含 5 阶执行模型、最小变更、计划先行与高强度验证）。
> **基准代码规范**：本规范派生自《[代码规范(C:C++)](./代码规范(C:C++).md) v6.1.0》，在 UE5 引擎约束下做适配与仲裁；两者冲突时以本规范为准（详见附录 F 仲裁表）。
> **适用范围**：所有 UE5 项目 C++ 新代码；修改老代码时遵循最小变更原则，不强制重构未触及的代码。
> **优先级（高→低）**：[AI行为规范](./AI行为规范.md) > 安全规范（19）> UE5 引擎约束 > 正确性（14） > 性能（13） > 风格（1-2）。
> **版本规则**：遵循语义化版本（SemVer）。

---

## 目录

1. [代码格式](#1-代码格式)
2. [命名规范](#2-命名规范)
3. [注释规范](#3-注释规范)
4. [类结构规范](#4-类结构规范)
5. [头文件规范](#5-头文件规范)
6. [接口设计规范](#6-接口设计规范)
7. [函数规范](#7-函数规范)
8. [移动语义](#8-移动语义)
9. [命名空间](#9-命名空间)
10. [类型推导与现代特性](#10-类型推导与现代特性)
11. [模板规范](#11-模板规范)
12. [函数修饰符](#12-函数修饰符)
13. [性能与最佳实践](#13-性能与最佳实践)
14. [错误处理](#14-错误处理)
15. [日志规范](#15-日志规范)
16. [并发规范](#16-并发规范)
17. [内存管理](#17-内存管理)
18. [宏与反射规范](#18-宏与反射规范)
19. [安全规范](#19-安全规范)
20. [测试规范](#20-测试规范)
21. [编译构建](#21-编译构建)
22. [设计模式](#22-设计模式)
23. [网络同步与 Gameplay 生命周期规范](#23-网络同步与-gameplay-生命周期规范)
24. [Git 规范](#24-git-规范)
25. [开发七大守则](#25-开发七大守则)
- [附录 A：UE5 反射宏家族速查](#附录-aue5-反射宏家族速查)
- [附录 B：UPROPERTY Specifier 速查](#附录-buproperty-specifier-速查)
- [附录 C：UFUNCTION Specifier 速查](#附录-cufunction-specifier-速查)
- [附录 D：委托类型选择决策树](#附录-d委托类型选择决策树)
- [附录 E：UE5 容器选择决策树](#附录-eue5-容器选择决策树)
- [附录 F：C++ 规范与 UE5 冲突仲裁表](#附录-fc-规范与-ue5-冲突仲裁表)
- [附录 G：版本履历](#附录-g版本履历)

---

## 1. 代码格式

### 1.1 缩进
使用 4 空格缩进，**严禁**使用 Tab。

### 1.2 大括号与代码块格式
- 类、函数、控制语句、命名空间：大括号与关键字**必须**在同一行
- **禁止**大括号单独占一行

### 1.3 头文件引用顺序

UE5 强制要求 `CoreMinimal.h` 必须在**所有头文件最前**（否则 IWYU / PCH 报错）。本规范覆盖 C++ 通用规范的 1.3，统一采用：

```cpp
#pragma once

#include "CoreMinimal.h"              // 1. 必须第一
#include "GameplayTagContainer.h"    // 2. UE5 引擎头文件
#include "Components/ActorComponent.h"
#include "FlexiItemSlot.h"           // 3. 项目内部头文件
#include "FlexiBagComponent.generated.h"  // 4. UHT 生成文件必须最后

class UFlexiItemObject;              // 前向声明放在所有 #include 之后
```

组间**必须**用空行分隔。

### 1.4 文件编码与换行
- **必须**使用 UTF-8 无 BOM 编码
- **必须**使用 LF（`\n`）换行符，**严禁**使用 CRLF

---

## 2. 命名规范

> **项目优先原则**：进入已有项目时，AI **必须**先查看现有代码的类、函数、变量命名，推断并遵循项目既有命名规范（UHT 强制前缀 U/A/F/E/I/S 不受项目风格覆盖，见 2.1）；新项目无可推断的既有命名时，**必须**询问用户采用哪种命名规范，**严禁**自行假定。

### 2.1 类型命名（UE5 强制前缀）

UE5 的 UHT（UnrealHeaderTool）**强制检查**类名前缀，错误命名会编译失败：

| 类型 | 前缀 | 后缀 | 示例 |
|------|------|------|------|
| 继承自 `UObject` 的类 | `U` | 无 | `UFlexiBagComponent` |
| 继承自 `AActor` 的类 | `A` | 无 | `AFlexiItemPickupActor` |
| USTRUCT 结构体 | `F` | 无 | `FFlexiItemSlot` |
| UENUM 枚举 | `E` | 无 | `EFlexiSortDirection` |
| 接口（UObject 版） | `I`（接口本体）+ `U`（UInterface 包装） | 无 | `IFlexiBagFeatureInterface` / `UFlexiBagFeatureInterface` |
| Slate 控件 | `S` | 无 | `SFlexiBagSlot` |
| 模板参数 | `T` 前缀或大写首字母 | 无 | `typename TContainer` |

> **覆盖 C++ 规范 2.1**：UE5 项目中**禁止**使用 `_t` 后缀（如 `manager_t`）。`_t` 后缀与蓝图 API、与 UE5 官方惯例、与大量第三方插件冲突。

### 2.2 枚举类型
- **必须**使用 `enum class`（scoped enum），**禁止**裸 `enum`
- 枚举值命名格式为 `类型::值`，**禁止**大写命名
- 示例：`EFlexiSortDirection::ascending`、`EItemQuality::dark_red`

### 2.3 变量命名
- **必须**使用下划线分隔的小写字母：`user_name`, `is_valid`
- **禁止**驼峰命名：`userName`, `bValid`

### 2.4 私有成员变量

> **覆盖 C++ 规范 2.4**：UE5 项目中**禁止**使用下划线后缀 `_`。

原因：
- `UPROPERTY` 成员名字会**直接暴露给蓝图与反射系统**，后缀会污染蓝图 API
- UE5 官方代码与所有第三方插件均不带后缀，遵循生态一致性

```cpp
// ✅ UE5 风格
class UFlexiBagComponent : public UActorComponent {
private:
    UPROPERTY(Transient)
    TArray<FFlexiItemSlot> slot_array;  // 无后缀

    UPROPERTY(Transient)
    TObjectPtr<UFlexiItemObjectFactory> cached_factory;  // 无后缀
};

// ❌ 禁止：C++ 通用规范的下划线后缀
class UFlexiBagComponent : public UActorComponent {
    UPROPERTY(Transient)
    TArray<FFlexiItemSlot> slot_array_;  // 错！蓝图会看到 slot_array_
};
```

### 2.5 私有成员函数

> **覆盖 C++ 规范 2.5**：UE5 项目中**禁止**使用单下划线后缀 `_`、双下划线前缀 `__`、单下划线前缀 `_`。

```cpp
class UFlexiBagComponent : public UActorComponent {
private:
    void init_slots();           // ✅ 无后缀
    bool validate_index(int32 index) const;  // ✅
    int32 find_first_empty_slot() const;    // ✅

    // ❌ 禁止
    void init_slots_();          // 错！下划线后缀与 UFUNCTION 命名不一致
    void __init_slots();        // 错！C++ 保留标识符
    void _init_slots();         // 错！与保留标识符边界混淆
};
```

### 2.6 常量命名
- **必须**使用全大写 + 下划线：`MAX_BUFFER_SIZE`
- **禁止**小写、k 前缀
- `constexpr` 常量同样遵循此规则

### 2.7 全局变量
- **必须**添加 `global_` 前缀
- **禁止** `g_` 前缀或其他形式
- UE5 项目中应尽量避免全局变量，优先使用 `UDeveloperSettings` 或 `UGameInstanceSubsystem`

### 2.8 命名空间
- **必须**使用小写字母
- **禁止**嵌套过深（建议最多 2-3 层）

### 2.9 函数命名
- **必须**使用下划线分隔的小写字母
- 可保留 get/set 前缀
- 蓝图可调用函数**建议**加 `bp_` 前缀以区分（可选）

---

## 3. 注释规范

### 3.1 文件头注释
所有头文件**必须**包含文件头注释。

### 3.2 函数注释
- **必须**使用 `/** */` 文档注释格式，**禁止**使用 `//` 行注释替代
- 内容**必须**包含：功能、参数、返回值；重要函数**必须**补充实现思路或使用示例

### 3.3 类注释
- 重要类**必须**包含注释，说明功能、设计思路、使用场景
- UCLASS 注释会出现在编辑器 Details Panel 的 tooltip 中

### 3.4 函数内部注释

> **继承 C++ 规范 3.2**：
- **禁止**在函数体内添加任何行内注释（`// xxx`）或块注释
- 如需说明函数实现思路、关键步骤、注意事项，**必须**写在函数定义上方的文档注释 `/** */` 中
- 若函数内部确需注释才能理解，说明函数过于复杂，**必须**考虑拆分（见第 25 条单一职责）

**正例**：
```cpp
/**
 * @brief 计算用户得分
 * @param user 用户信息
 * @return 加权后的得分
 *
 * 实现思路：基础分 + 活跃度加成 - 违规惩罚
 */
int32 calc_score(const FUserData& user) const {
    int32 base = user.base_score;
    int32 bonus = user.active_days * BONUS_PER_DAY;
    int32 penalty = user.violations * PENALTY;
    return base + bonus - penalty;
}
```

**反例**：
```cpp
int32 calc_score(const FUserData& user) const {
    int32 base = user.base_score;
    int32 bonus = user.active_days * BONUS_PER_DAY;  // 计算活跃度加成
    int32 penalty = user.violations * PENALTY;       // 扣除违规惩罚
    return base + bonus - penalty;                  // 返回总分
}
```

---

## 4. 类结构规范

> **继承 C++ 规范 4**。UE5 项目中由于 UCLASS 的反射要求，需补充以下约定。

**必须**按以下顺序组织：

1. `public` 类型定义（含 USTRUCT 嵌套、using 别名）
2. `protected` 类型定义
3. `private` 类型定义
4. `private` 常量
5. `protected` 常量
6. `public` 常量
7. `private` 成员变量（含 UPROPERTY）与静态变量
8. `protected` 成员变量与静态变量
9. `public` 成员变量（谨慎使用）与静态变量
10. `private` 成员函数
11. `protected` 成员函数
12. `public` 成员函数（含 UFUNCTION）
13. `private` 静态函数
14. `protected` 静态函数
15. `public` 静态函数
16. UE5 反射相关重写（如 `GetLifetimeReplicatedProps`、`ReplicateSubobjects`）

**函数实现顺序必须与类中声明顺序一致**：`.cpp` 中的函数实现**必须**按照头文件中声明的先后顺序排列。

**内联函数放置**：UE5 项目中，UCLASS 的内联实现通常放在类声明内（UE5 不强制 `.inl`）；非反射类的内联实现仍按 C++ 规范 5 放在访问权限区域尾部。

---

## 5. 头文件规范

### 5.1 文件后缀

| 文件类型 | 后缀 | 用途 |
|----------|------|------|
| 头文件 | `.h` | 声明 |
| 源文件 | `.cpp` | 实现（UE5 推荐 `.cpp`，旧代码可能用 `.cc`） |
| 头源合一 | `.hpp` | 声明+实现（UE5 项目**禁止**使用） |
| 模板实现 | `.inl` | 模板实现（非反射类可用） |

### 5.2 UE5 头文件特殊要求

- **必须**使用 `#pragma once`
- **必须**在头文件最后 `#include "XXX.generated.h"`（UHT 强制）
- **必须**使用前向声明减少依赖
- **严禁**在头文件中 `using namespace`（见第 9 条）

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "FlexiBagComponent.generated.h"   // 必须最后

class UFlexiItemDataAsset;   // 前向声明
class UFlexiItemObject;
```

---

## 6. 接口设计规范

UE5 接口**必须**使用 `UINTERFACE` + `I` 前缀类双结构：

```cpp
// .h
UINTERFACE(MinimalAPI, Blueprintable)
class UFlexiBagFeatureInterface : public UInterface {
    GENERATED_BODY()
};

/**
 * @brief UI 功能子模块通信接口
 */
class FLEXIINVENTORY_API IFlexiBagFeatureInterface {
    GENERATED_BODY()

public:
    virtual ~IFlexiBagFeatureInterface() = default;  // 虚析构

    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    void initialize_feature(UFlexiBagMainWidget* main_bag_widget);
};
```

规则：
- `U` 前缀类**必须**继承 `UInterface`，**只**包含 `GENERATED_BODY()`
- `I` 前缀类**必须**包含虚析构函数与所有接口方法
- 实现：`class UMyClass : public UObject, public IFlexiBagFeatureInterface`
- C++ 侧用 `Cast<IFlexiBagFeatureInterface>(obj)` 判断是否实现

---

## 7. 函数规范

### 7.1 关键规则

> **覆盖 C++ 规范 6.1 中与 UE5 冲突的部分**：

- 单参数构造函数**必须**使用 `explicit`
- 不抛异常的函数**必须**标记 `noexcept`（UE5 项目中几乎所有函数都应 noexcept，因 UE5 默认禁用异常）
- 赋值运算符**必须**返回自身引用
- **必须**使用 `nullptr`，**严禁**使用 `NULL` 或 `0`
- **必须**使用 `TObjectPtr<T>` 替代裸 `T*`（UE5.1+，发布构建中等价于 `T*`）
- **必须**使用 `using`，**禁止** `typedef`
- **必须**在成员变量声明处直接初始化（默认成员初始化）
- **必须**遵循 Rule of 0/3/5

### 7.2 列表初始化

- **优先**使用列表初始化 `{}`；当 `{}` 会改变语义时（如 `std::vector<int> v(10, 0)` 计数构造）**必须**使用 `()`

### 7.3 lambda 表达式
- **必须**显式捕获需要的变量
- **禁止**捕获过多变量
- UE5 项目中 lambda 优先用 `TFunction` 而非 `std::function`

### 7.4 函数设计规则
- 函数长度**建议**不超过 50 行；超过**必须**考虑拆分（单一职责，见第 25 条）
- 函数参数**建议**不超过 4 个；超过**必须**考虑封装为结构体
- **必须**使用提前返回（guard clause）简化嵌套
- **必要防御原则与严禁过度防御（Like Human Engineers）**：
  - **核心铁律：非确定不判断就会出错，绝不添加判断**。像资深人类工程师一样思考，只在真正的关键边界（玩家网络输入、RPC 参数、未初始化的弱指针等）做必要校验。
  - **严禁过度防御**：绝不能因为某个地方出错的几率只有 0.1% 甚至 0% 就去写一个防御分支；**严禁**为不存在或概率极低的臆想场景层层设卡。
  - **信任 UE5 引擎上下文与架构契约**：在生命周期明确的回调中（如组件的 `BeginPlay`、`Tick` 中 `GetOwner()`、已注册的 Subsystem 等），上游或引擎架构已保证其有效性，**严禁在每个子方法内部重复调用 `IsValid()` / `!= nullptr` 层层设卡**。
- 主逻辑**必须**保持线性一路向下：**严禁**深嵌套、逻辑分叉散落与控制流来回横跳；提前返回（guard clause）是线性化手段，不属于"乱跳"
- **必须**优先使用纯函数（无副作用）；成员函数 `const` 修饰见第 12 条
- **禁止**输出参数（非 const 引用作为返回值），**必须**使用返回值或 `TOptional`

### 7.5 UE5 反射函数特殊要求

```cpp
UCLASS()
class UFlexiBagComponent : public UActorComponent {
    GENERATED_BODY()

public:
    // BlueprintCallable：蓝图可调用
    UFUNCTION(BlueprintCallable, Category = "FlexiInventory|Logic")
    bool move_item(int32 source_index, int32 target_index);

    // BlueprintPure：蓝图可调用且无副作用（隐式 const）
    UFUNCTION(BlueprintPure, Category = "FlexiInventory|Query")
    int32 get_slot_count() const;

    // BlueprintNativeEvent：C++ 提供默认实现，蓝图可覆盖
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    void on_item_added(int32 slot_index);

    // BlueprintImplementableEvent：纯蓝图实现
    UFUNCTION(BlueprintImplementableEvent, BlueprintCallable)
    void play_pickup_anim();
};
```

- `BlueprintNativeEvent` 在 `.cpp` 中实现时**必须**加 `_Implementation` 后缀
- `BlueprintPure` 函数**必须**标记 `const`
- 蓝图可调用函数**必须**指定 `Category`，用 `|` 分层（如 `FlexiInventory|Logic`）

---

## 8. 移动语义

### 8.1 Rule of 0/3/5
- **必须**遵循 Rule of 0/3/5
- UCLASS 类**通常**遵循 Rule of 0（让编译器生成默认实现），因为 `UObject` 派生类禁止深拷贝

### 8.2 noexcept
- 移动构造函数和赋值运算符**必须**标记 `noexcept`
- UE5 中 `TArray`、`TMap` 等容器在 realloc 时会检查元素类型的 `noexcept` 移动构造

### 8.3 参数传递规则

> **覆盖 C++ 规范 6.2 中参数传递部分**：

| 场景 | 规则 |
|------|------|
| 内置类型/小型结构 | 按值传递 |
| 大型对象（如 `TArray`、`FString`） | const 引用 |
| 需要修改 | 非 const 引用 |
| 需要转移所有权 | 右值引用 |
| UObject 参数 | `UObject*` 或 `TObjectPtr<UObject>`（不要传值） |
| 需要传递 UObject 所有权 | `TObjectPtr<UObject>`（GC 自动管理，无需 `std::move`） |

---

## 9. 命名空间

- **禁止**嵌套过深（建议最多 2-3 层）
- **严禁**在头文件中使用 `using namespace`
- **禁止**在源文件中使用 `using namespace std`（UE5 项目**禁止**使用 std 容器，用 UE5 对应物）
- 文件内部符号**必须**放在匿名命名空间

UE5 项目中**禁止**使用以下 std 类型，必须用 UE5 对应物：

| std 类型 | UE5 替代 |
|---------|---------|
| `std::string` | `FString` |
| `std::string_view` | `FStringView` |
| `std::vector<T>` | `TArray<T>` |
| `std::array<T, N>` | `TFixedArray<T, N>` 或 `std::array`（非反射代码可用） |
| `std::map<K, V>` | `TMap<K, V>` |
| `std::unordered_map<K, V>` | `TMap<K, V>`（默认哈希） |
| `std::set<T>` | `TSet<T>` |
| `std::shared_ptr<T>` | `TSharedPtr<T>`（非 UObject）/ GC（UObject） |
| `std::unique_ptr<T>` | `TUniquePtr<T>`（非 UObject）/ `NewObject<T>`（UObject） |
| `std::function<...>` | `TFunction<...>` |
| `std::thread` | `FAsyncTask` / `TFuture` |
| `std::mutex` | `FCriticalSection` |
| `std::optional<T>` | `TOptional<T>` |

---

## 10. 类型推导与现代特性

### 10.1 类型推导
- **必须**明确使用 `auto`，避免隐式类型推导
- `decltype` **必须**用于需要类型信息时
- `auto` 变量**必须**在声明时初始化
- **禁止** `auto` 的以下反模式：

```cpp
auto x = {1, 2, 3};           // 错！推导为 std::initializer_list<int>
auto p = new widget();         // 错！推导为 widget*，应避免裸 new
```

### 10.2 结构化绑定与 if constexpr
- **必须**使用结构化绑定解构多返回值（替代 `std::tie`）
- **必须**使用 `if constexpr` 替代 SFINAE 实现编译期分支

### 10.3 concept 与约束（C++20）
- UE5 项目**建议**使用 C++20，但需在 `Build.cs` 中显式启用
- 自定义 concept **禁止**加 `_t` 后缀

### 10.4 属性（Attributes）
- 返回值不应被忽略的函数**必须**标记 `[[nodiscard]]`
- 暂未使用的变量/参数**必须**标记 `[[maybe_unused]]`，**禁止**用 `(void)` 强转
- **禁止**使用 `[[deprecated]]` 之外的编译器扩展属性

---

## 11. 模板规范

### 11.1 模板实现位置
- 模板参数**必须**使用有意义的名称：`template<typename T>`
- 类模板**必须**通过 `using` 为模板参数及相关类型定义语义化别名（`value_type` / `size_type` 等，放 public 类型定义区），类内及成员函数签名**禁止**直接使用 `T`
- 模板实现**必须**放在 `.inl` 文件，由对应 `.h` 在末尾 `#include`
- 模板特化**必须**明确标注
- **禁止**将模板实现放入 `.cpp`（除非使用显式实例化）

### 11.2 UE5 反射类与模板

> **UE5 特化规则**：UCLASS / USTRUCT / UENUM **禁止**是模板类，因 UHT 不支持模板反射。

如果需要泛型容器，用 USTRUCT 包装 + `TArray<TObjectPtr<UObject>>` + 类型检查：

```cpp
// ✅ 正确：用 UObject 多态 + 运行期类型检查替代模板
USTRUCT(BlueprintType)
struct FLEXIINVENTORY_API FFlexiItemSlot {
    GENERATED_BODY()

    UPROPERTY()
    TObjectPtr<UFlexiItemObject> item_object;  // 多态对象，运行期判定类型
};

// ❌ 错误：UHT 不支持模板 USTRUCT
template<typename T>
USTRUCT()
struct FFlexiContainer {
    GENERATED_BODY()
    T item;
};
```

### 11.3 非反射类的模板

非反射的纯 C++ 工具类**可以**使用模板，核心规则（同 C++ 规范 9）：
- 模板参数**必须**使用有意义的名称：`template<typename T>`
- **必须**将模板实现放在 `.inl` 文件，由对应 `.h` 在末尾 `#include`
- 模板特化**必须**明确标注；**禁止**模板实现放入 `.cpp`（除非显式实例化）或在头文件中直接定义

---

## 12. 函数修饰符

- 重写虚函数**必须**使用 `override`
- `const` 不需要修改成员函数**必须**标记 `const`
- `constexpr` 函数**必须**正确使用
- `BlueprintPure` UFUNCTION **必须**同时标记 `const`

---

## 13. 性能与最佳实践

### 13.1 通用规则
- **禁止**不必要拷贝，优先移动
- **禁止**在构造函数中做复杂操作
- **必须**使用 `TOptional` 表示可选值（替代 `std::optional`）

### 13.2 返回值优化（RVO/NRVO）
- **必须**按值返回局部对象，依赖 RVO/NRVO，**禁止**返回 `std::move` 局部对象（会禁用 NRVO）

### 13.3 UE5 容器使用

> **覆盖 C++ 规范 10.3**：

- **必须**在已知元素数量时调用 `Reserve()` 预分配
- **必须**优先使用 `EmplaceBack` / `Emplace` 替代 `Add` / `Add`，避免临时对象
- **禁止**使用 `std::list`（缓存不友好），**必须**优先 `TArray` / `TDeque`
- 容器选择详见**附录 E：UE5 容器选择决策树**

```cpp
TArray<int32> v;
v.Reserve(n);            // 预分配
for (int32 i = 0; i < n; ++i) {
    v.EmplaceBack(i);    // 直接构造，避免临时对象
}
```

### 13.4 字符串使用

UE5 三种字符串：

| 类型 | 用途 | 选择原则 |
|------|------|---------|
| `FString` | 可变字符串，运行期操作 | 临时拼接、格式化 |
| `FName` | 不可变名，哈希存储 | 字典 key、Tag 名、资源路径 |
| `FText` | 本地化文本 | UI 显示、玩家可见文本 |

**规则**：
- UI 显示文本**必须**用 `FText`（支持本地化）
- 字典 key / Tag 名**必须**用 `FName`（哈希快）
- 临时字符串操作用 `FString`
- **禁止**用 `const TCHAR*` 作为成员变量（GC 不跟踪）
- **禁止**用 `std::string`

### 13.5 软引用与弱引用

| 类型 | 用途 |
|------|------|
| `TObjectPtr<T>` + UPROPERTY | 强引用（GC 跟踪） |
| `TWeakObjectPtr<T>` | 弱引用（防循环引用，访问前 `IsValid()`） |
| `TSoftObjectPtr<T>` | 软引用（仅存路径，按需加载） |
| `TSoftClassPtr<T>` | 软类引用（按需加载类） |
| `FSoftObjectPath` | 纯路径（无类型信息） |

---

## 14. 错误处理

> **继承 C++ 规范 11**，UE5 默认禁用 C++ 异常，与本规范天然契合：

- **必须**默认使用错误码 / `TOptional` / `TExpected`（UE5.3+）方案
- **禁止**使用 C++ 异常（`throw` / `try-catch`），UE5 项目默认 `-fno-exceptions`
- **必须**在构造函数中避免失败（使用工厂模式 + `TOptional` 返回结果）
- **必须**在析构函数中处理清理工作，**禁止**抛出异常
- 日志记录**必须**包含错误上下文信息

**正例**：
```cpp
[[nodiscard]] TOptional<UFlexiItemObject*> find_item(int32 slot_index) const {
    if (!validate_index(slot_index)) {
        UE_LOG(LogFlexiInventory, Warning, TEXT("Invalid slot index: %d"), slot_index);
        return {};
    }
    return slots[slot_index].item_object;
}
```

**反例**：
```cpp
UFlexiItemObject* find_item(int32 slot_index) const {
    if (slot_index < 0) throw std::out_of_range("...");  // 错！UE5 禁用异常
    return slots[slot_index].item_object;
}
```

### 14.1 UE5 断言宏

| 宏 | 用途 | 发布构建行为 |
|---|---|---|
| `check(expr)` | 不变式断言 | 自动移除 |
| `checkf(expr, fmt, ...)` | 带格式化信息的不变式断言 | 自动移除 |
| `ensure(expr)` | 警告级断言 | 保留，仅报错一次不崩 |
| `ensureMsgf(expr, fmt, ...)` | 带格式化的警告级断言 | 保留 |
| `verify(expr)` | 必须执行副作用的断言 | 保留表达式执行 |

**使用原则**：
- `check`：用于内部不变式（如 `check(slots.Num() > 0)`）
- `ensure`：用于可能出错的边界情况（如参数校验失败）
- `verify`：表达式有副作用时使用

---

## 15. 日志规范

### 15.1 UE5 日志宏

> **覆盖 C++ 规范 12**：UE5 项目**禁止**使用 `cout` / `printf` / `std::format`，**必须**使用 `UE_LOG`。

```cpp
// 声明日志分类（.cpp 中）
DEFINE_LOG_CATEGORY_STATIC(LogFlexiInventory, Log, All);
// 或全局声明
DECLARE_LOG_CATEGORY_EXTERN(LogFlexiInventory, Log, All);
DEFINE_LOG_CATEGORY(LogFlexiInventory);

// 使用
UE_LOG(LogFlexiInventory, Log, TEXT("Item added to slot %d"), slot_index);
UE_LOG(LogFlexiInventory, Warning, TEXT("Slot %d is locked"), slot_index);
UE_LOG(LogFlexiInventory, Error, TEXT("Failed to save bag: %s"), *error_msg);
```

### 15.2 日志级别

| 级别 | 用途 |
|------|------|
| `Fatal` | 致命错误，立即崩溃（仅用于不可恢复状态） |
| `Error` | 错误，记录但不崩溃 |
| `Warning` | 警告，非预期但可继续 |
| `Display` | 重要信息，默认显示 |
| `Log` | 普通信息，默认显示 |
| `Verbose` | 详细信息，默认隐藏 |
| `VeryVerbose` | 极详细，调试用 |

### 15.3 规则
- **禁止**在日志中输出敏感信息（密码、密钥等）
- **禁止**在高频循环中输出日志（每帧/每 Tick）
- 日志格式**必须**包含：日志分类、级别、消息（UE5 自动附加文件名、行号、时间戳、线程ID）
- **必须**使用 `TEXT()` 宏包裹字符串字面量

---

## 16. 并发规范

### 16.1 锁与同步原语

> **覆盖 C++ 规范 13.1**：UE5 项目优先使用 UE5 同步原语。

| C++17 | UE5 | 用途 |
|-------|-----|------|
| `std::mutex` | `FCriticalSection` | 互斥锁 |
| `std::lock_guard` | `FScopeLock` | RAII 锁 |
| `std::shared_mutex` | `FRWLock` | 读写锁 |
| `std::atomic<T>` | `FThreadSafeCounter` / `std::atomic`（也可） | 原子计数 |
| `std::condition_variable` | `FEvent` | 事件 |

规则：
- **必须**使用 RAII 管理锁（`FScopeLock`）
- **禁止**在持锁期间执行耗时操作
- **必须**避免死锁：**禁止**嵌套锁，**必须**按固定顺序获取锁
- 需要同时获取多把锁时，**必须**使用 `FScopedResolution`（自动死锁避免）
- 读多写少场景**必须**使用 `FRWLock`：
  ```cpp
  mutable FRWLock mutex;
  // 读端
  FReadScopeLock lk(mutex);
  // 写端
  FWriteScopeLock lk(mutex);
  ```
- **禁止**使用 `std::recursive_mutex`（设计气味）

### 16.2 线程管理

> **覆盖 C++ 规范 13.2**：UE5 项目**禁止**使用 `std::thread` / `std::jthread`，**必须**使用 UE5 任务系统。

| 场景 | UE5 方案 |
|------|---------|
| 简单异步任务 | `FAsyncTask<T>` |
| Future/Promise | `TFuture<T>` / `TPromise<T>` |
| 并行 for | `ParallelFor(n, [](int32 i) { ... })` |
| 长期运行任务 | `FQueuedThreadPool` |
| 延迟执行 | `FTimerHandle` + `SetTimerByEvent` |

```cpp
// 异步任务：TUniquePtr 管理（禁止裸 new/delete，见 17.1）
TUniquePtr<FAsyncTask<FMyTask>> task = MakeUnique<FAsyncTask<FMyTask>>(args...);
task->StartBackgroundTask();
// 主线程轮询
if (task->IsDone()) {
    auto result = task->GetTask().result;
    task.Reset();
}

// TFuture
auto future = Async(EAsyncExecution::ThreadPool, []() {
    return expensive_computation();
});
// 主线程
int32 result = future.Get();  // 阻塞直到完成
```

**关键约束**：
- **禁止**在非游戏线程访问 `UObject`（GC 不安全），必须通过 `FTaskGraphInterface` 调度回游戏线程
- **必须**使用 `thread_local` 管理线程私有状态

### 16.3 原子操作与内存序
- 共享数据**必须**使用原子操作或锁保护
- **必须**使用 `std::atomic` 或 `FThreadSafeCounter` 替代 volatile 标志位
- **必须**正确选择内存序：
  - 默认 `memory_order_seq_cst`（顺序一致，最安全）
  - 仅在性能剖析确认需要时使用 `memory_order_acquire` / `memory_order_release`
  - **禁止**无依据地使用 `memory_order_relaxed`

### 16.4 线程局部存储与通信
- 线程私有状态**必须**使用 `thread_local`
- 线程间通信**必须**使用 `TFuture` / `TPromise` 或 `TQueue<T>`
- **禁止**使用条件变量的虚假唤醒：**必须**用谓词形式

---

## 17. 内存管理

### 17.1 RAII 与智能指针

> **覆盖 C++ 规范 14**：

- **必须**遵循 RAII 原则
- `UObject` 派生类**禁止**使用 `new` / `delete`，**必须**用 `NewObject<T>(outer)` 创建，由 GC 管理
- 非 UObject 类型**必须**用 `TUniquePtr<T>` / `TSharedPtr<T>`，**禁止**裸 `new` / `delete`

### 17.2 UObject 创建规则

```cpp
// ✅ 正确：UObject 用 NewObject
UFlexiItemObject* item = NewObject<UFlexiItemObject>(this);
// GC 自动跟踪，前提是 this 持有 UPROPERTY 引用 item

// ✅ 正确：非 UObject 用 MakeUnique/MakeShared
auto factory = MakeUnique<FFlexiDataParser>();
auto shared_data = MakeShared<FSharedContext>();

// ❌ 错误：UObject 不能用 std::make_unique
auto item = std::make_unique<UFlexiItemObject>();  // 错！

// ❌ 错误：UObject 不能用裸 new
UFlexiItemObject* item = new UFlexiItemObject();  // 错！

// ❌ 错误：UObject 不能用 delete
delete item;  // 错！
```

### 17.3 UPROPERTY 保留机制（重要陷阱）

> **UE5 特化规则**：任何 `UObject*` / `TObjectPtr<UObject>` 成员变量**必须**用 `UPROPERTY()` 标记（哪怕没有 specifier），否则 GC 不知道你持有它，会被回收。

```cpp
class UFlexiBagComponent : public UActorComponent {
    GENERATED_BODY()

    // ✅ 正确：UPROPERTY 持有，GC 强引用
    UPROPERTY(Transient)
    TObjectPtr<UFlexiItemObjectFactory> cached_factory;

    // ❌ 错误！无 UPROPERTY，GC 随时可能回收 cached_factory
    TObjectPtr<UFlexiItemObjectFactory> cached_factory_no_prop;
};
```

### 17.4 智能指针选择决策

```
需要管理 UObject？
├─ 是 → 用 TObjectPtr + UPROPERTY（GC 管理）
└─ 否 → 需要共享所有权？
        ├─ 是 → TSharedPtr<T>（用 MakeShared 创建）
        └─ 否 → 需要独占所有权？
                ├─ 是 → TUniquePtr<T>（用 MakeUnique 创建）
                └─ 否 → 用栈对象或值语义
```

### 17.5 内存分配检查
- 内存分配**必须**检查是否成功（UE5 的 `FMemory::Malloc` 返回 nullptr 时由 OOM handler 处理）
- **必须**使用内存池处理高频分配场景（如 `FMemoryPool` 或自定义 `FMalloc`）

---

## 18. 宏与反射规范

### 18.1 C++ 宏

> **继承 C++ 规范 15**：
- **优先**使用 `const` / `constexpr` / `enum` 替代宏定义常量
- **优先**使用 `inline` / `constexpr` 函数替代宏定义函数
- **必须**使用全大写 + 下划线命名宏：`MAX_ITERATIONS`
- **必须**使用 `do { ... } while(0)` 包裹多语句宏
- **禁止**使用宏实现模板或泛型逻辑

### 18.2 UE5 反射宏

> **UE5 特化规则**：UE5 的反射宏（`UCLASS` / `USTRUCT` / `UENUM` / `UPROPERTY` / `UFUNCTION` / `GENERATED_BODY`）**必须**严格遵守使用规则：

| 宏 | 使用规则 |
|---|---|
| `UCLASS(...)` | 类**必须**继承自 `UObject` 或其派生类；**必须**在类体内第一行写 `GENERATED_BODY()` |
| `USTRUCT(...)` | 结构体**必须**在体内第一行写 `GENERATED_BODY()`；**禁止**继承自 UObject（USTRUCT 不能是 UObject） |
| `UENUM(...)` | **必须**用于 `enum class`；**禁止**用于裸 enum |
| `UPROPERTY(...)` | **必须**用于 `UObject*` / `TObjectPtr<T>` 成员（否则 GC 不跟踪）；**建议**用于需要序列化/编辑器可见的成员 |
| `UFUNCTION(...)` | **必须**用于蓝图可调用函数；**必须**指定 `Category` |
| `GENERATED_BODY()` | **必须**在 UCLASS / USTRUCT / UENUM 体内第一行；**禁止**手动写 `GENERATED_BODY_LEGACY` |
| `GENERATED_UCLASS_BODY()` | **禁止**使用（旧 API，已废弃） |

### 18.3 .generated.h 强制要求

参与反射的头文件**必须**在最后 `#include "XXX.generated.h"`：

```cpp
// MyComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyComponent.generated.h"   // 必须最后

UCLASS()
class UMyComponent : public UActorComponent {
    GENERATED_BODY()
};
```

**遗漏 `.generated.h` 会导致链接错误** `unresolved external symbol Z_Construct...`。

### 18.4 反射宏 specifier 选择

详见附录 B（UPROPERTY Specifier）与附录 C（UFUNCTION Specifier）。

---

## 19. 安全规范

> **继承 C++ 规范 16**，UE5 特化补充：

### 19.1 字符串安全

- **禁止**使用 `strcpy` / `sprintf` / `strncpy`（`strncpy` 不保证 null 终止且有截断问题）
- **优先**使用 `FString` / `FStringView` / `FName` / `FText`
- C 接口处**必须**使用 `FCString::Snprintf` 或 `FString::Printf`
- **必须**使用 `sizeof(buffer)` 或 `ARRAY_COUNT(buffer)` 而非硬编码大小

### 19.2 随机数

- **禁止**使用 `rand()` 生成安全随机数
- **必须**使用 `FMath::Rand()`（简单场景）或 `FRandomStream`（可复现场景）

### 19.3 输入校验
- 外部输入数据**必须**进行有效性校验（内部调用链已保证的数据不重复校验，见 7.4）
- **禁止**在代码中硬编码密钥、密码

### 19.4 `FStringView` 生命周期安全

> **覆盖 C++ 规范 16.1 中的 `std::string_view`**：

- `FStringView` **必须**视为非所有权视图，**禁止**持有超出源字符串生命周期的 view
- 类成员**禁止**使用 `FStringView` 存储字符串，**必须**使用 `FString`
- **必须**使用 `TArrayView<T>` 替代 `const T*` + `int32` 的连续内存参数组合

**正例**：
```cpp
void process(FStringView sv);             // 函数参数：安全
FString s = make_string();
FStringView sv = s;                       // 同作用域：安全
```

**反例**：
```cpp
FStringView get_view() {
    FString s = make_temp();               // 临时对象
    return s;                              // 错！返回指向已销毁对象的 view
}
FStringView sv = TEXT("hello");            // 危险！字面量生命周期模糊
```

---

## 20. 测试规范

> **覆盖 C++ 规范 17**：UE5 项目使用 Automation 测试框架。

### 20.1 测试类型

| 类型 | 宏 | 用途 |
|------|---|------|
| 简单测试 | `IMPLEMENT_SIMPLE_AUTOMATION_TEST` | 纯逻辑单元测试 |
| 复杂测试 | `IMPLEMENT_COMPLEX_AUTOMATION_TEST` | 需要加载场景/资源 |
| 命令测试 | `IMPLEMENT_LATENT_AUTOMATION_TEST` | 多帧异步测试 |

```cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FFlexiBagComponentTest,
    "FlexiInventory.BagComponent.AddRemove",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FFlexiBagComponentTest::RunTest(const FString& Parameters) {
    UFlexiBagComponent* bag = NewObject<UFlexiBagComponent>();
    bool result = bag->try_add_item(testItem, 5);
    TestTrue(TEXT("Add item should succeed"), result);
    TestEqual(TEXT("Slot count should be 1"), bag->count_item(TestItem), 5);
    return true;
}
```

### 20.2 规则
- **必须**为新功能编写单元测试
- **必须**保证测试可重复执行
- **必须**使用 mock 对象隔离依赖
- 测试用例**必须**覆盖正常和异常路径
- **禁止**在测试中使用 `FPlatformProcess::Sleep` 等待异步完成，应使用 `TFuture` / `FEvent` 等同步机制

---

## 21. 编译构建

### 21.1 C++ 标准
- **必须**明确指定 C++ 标准（建议 C++20 起步，最低 C++17）
- 在 `Build.cs` 中通过 `CppStandard` 设置：
  ```csharp
  public FlexiInventory(ReadOnlyTargetRules Target) : base(Target) {
      PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
      CppStandard = CppStandardVersion.Cpp20;
      // ...
  }
  ```

### 21.2 Build.cs 配置规则
- **必须**显式声明模块依赖（`PublicDependencyModuleNames` / `PrivateDependencyModuleNames`）
- **必须**设置 `PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs`
- **禁止**把私有依赖放在 `PublicDependencyModuleNames`（会污染下游模块）
- **必须**设置编译选项：`-Wall` / `-Wextra` / `-Wpedantic`（通过 `Target.ExtraModuleArguments` 或全局 `Target.cs`）

### 21.3 编译配置
- **必须**设置调试（Debug）和发布（Shipping）两种构建配置
- **禁止**修改第三方库源码，**必须**使用补丁或封装
- **必须**在提交前执行完整构建和测试

### 21.4 Target.cs 配置
- **必须**在 `Target.cs` 中启用所需功能（如 `bUseNavigationSystem`、`bUseGameplayTags`）
- **建议**启用 `bForceIEAutomation` 用于测试

---

## 22. 设计模式

> **继承 C++ 规范 19**，UE5 特化补充：

- **必须**根据场景选择合适模式，**禁止**过度设计
- 单例模式**必须**使用 `USubsystem`（如 `UGameInstanceSubsystem`、`UWorldSubsystem`）替代手写单例
- 工厂模式**必须**封装对象创建逻辑，隐藏具体类型
- **必须**优先使用组合而非继承
- **禁止**在模板中过度使用类型擦除

### 22.1 UE5 常用模式

| 模式 | UE5 实现方式 |
|------|------|
| 单例 | `UGameInstanceSubsystem` / `UWorldSubsystem` / `ULocalPlayerSubsystem` |
| 工厂 | `NewObject<T>` + 工厂类（参考 FlexiItemObjectFactory） |
| 观察者 | UE5 委托（`DECLARE_DYNAMIC_MULTICAST_DELEGATE`） |
| 策略 | DataAsset 子类化（如 `UFlexiBagSortRuleDataAsset`） |
| 状态 | `FGameplayTag` 标签组合（替代 enum 状态机） |
| 组件 | `UActorComponent`（UE5 原生支持） |

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
        try_init_ability_system();
    }
}

void AMyPlayerState::OnRep_Owner() {
    Super::OnRep_Owner();
    // 客户端在网络所有者就绪时自驱动
    try_init_ability_system();
}
```

**反例**：
```cpp
// ❌ 错误：在 GameMode 登录回调中越权代劳网络初始化
void AMyGameMode::PostLogin(APlayerController* new_player) {
    Super::PostLogin(new_player);
    if (AMyPlayerState* ps = new_player->GetPlayerState<AMyPlayerState>()) {
        // 错！外部只知道逻辑就绪，客户端此时根本尚未"网络就绪"，会导致客户端初始化丢失
        ps->init_ability_system();
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
- **工程实践提示**：类似项目中的 `try_init_ability_system()` 与 `init_attribute_set()` 均须按此原则收敛，确保存续实例始终复用。

**正例**：
```cpp
// ✅ 正确：创建与初始化解耦，多次调用安全幂等
void AMyPlayerState::try_init_ability_system() {
    if (!ability_system_component) {
        // 首次创建（或构造函数已创建）：仅执行一次
        ability_system_component = NewObject<UAbilitySystemComponent>(this, TEXT("AbilitySystemComponent"));
        ability_system_component->SetIsReplicated(true);
        ability_system_component->SetReplicationMode(EGameplayEffectReplicationMode::Mixed);
    }

    if (!attribute_set) {
        // 属性集实例仅创建一次，后续永远复用
        attribute_set = NewObject<UMyAttributeSet>(this, TEXT("AttributeSet"));
    }

    // 后续可被多次幂等调用的初始化逻辑（如重新附身时刷新 ActorInfo）
    AActor* avatar_actor = GetPawn();
    ability_system_component->InitAbilityActorInfo(this, avatar_actor);
}
```

**反例**：
```cpp
// ❌ 错误：每次初始化都重新分配实例，覆盖现有对象
void AMyPlayerState::init_ability_system() {
    // 错！重生或二次调用时重新创建，破坏已有的网络同步状态与委托绑定
    ability_system_component = NewObject<UAbilitySystemComponent>(this);
    attribute_set = NewObject<UMyAttributeSet>(this);
    ability_system_component->InitAbilityActorInfo(this, GetPawn());
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
void AMyCharacter::init_player_context() {
    const bool is_authority = HasAuthority();
    const bool is_local = IsLocallyControlled();

    if (is_authority) {
        // 服务器端：仅负责授予初始技能与权威状态配置
        grant_default_abilities();
    }

    if (is_local) {
        // 本地玩家端：仅负责创建本地 HUD 与输入绑定
        setup_local_hud();
        bind_input_actions();
    }

    // 远端模拟客户端（!is_authority && !is_local）：默认不做，完全依赖属性与状态复制驱动表现
}
```

**反例**：
```cpp
// ❌ 错误：缺少身份分叉，全端无差别执行
void AMyCharacter::init_player_context() {
    // 错！Dedicated Server 会尝试创建 Slate UI 导致崩溃；远端模拟代理也会创建本地 HUD
    create_player_hud();
    // 错！客户端也尝试调用仅服务器有效的授予技能
    grant_default_abilities();
}
```

---

## 24. Git 规范

> **继承 C++ 规范 20**：

### 24.1 提交信息格式

```
[类型]: 简短描述
- 变更描述01
- 变更描述02
...
```

- 类型：`feat` / `fix` / `docs` / `style` / `refactor` / `test` / `chore`
- 简短描述**必须**概括本次提交核心目的
- 变更描述**必须**列出具体改动点，每条以 `- ` 开头
- 变更描述**必须**说明"改了什么"及"为什么改"

### 24.2 分支命名
- 分支命名**必须**遵循：`类型/功能描述`

### 24.3 UE5 特化规则
- **必须**配置 `.gitignore` 忽略 `Binaries/` / `Intermediate/` / `Saved/` / `DerivedDataCache/`
- **禁止**提交 `.uproject` 中的 `Plugins` 数组变更（除非新增/删除插件）
- **必须**在合并前进行代码 review
- **禁止**提交编译产物和临时文件
- `.uasset` / `.umap` 文件**必须**使用 LFS 管理（在 `.gitattributes` 中配置）

---

## 25. 开发七大守则

> **继承 C++ 规范 21**：

1. **单一职责**：每个类/函数**必须**只做一件事
2. **开闭原则**：**必须**对扩展开放，对修改关闭
3. **里氏替换**：子类**必须**能替换基类
4. **依赖倒置**：**必须**依赖抽象，而非具体实现
5. **接口隔离**：**必须**保持接口精简，**禁止**庞大接口
6. **DRY 原则**：**禁止**重复代码，**必须**提取公共逻辑
7. **KISS 原则**：**禁止**过度复杂，**必须**保持简单直接

---

## 附录 A：UE5 反射宏家族速查

| 宏 | 作用 | 强制要求 |
|---|---|---|
| `UCLASS(...)` | 标记类参与反射 + GC | 类**必须**继承 `UObject` 派生类 |
| `USTRUCT(...)` | 标记结构体参与反射（不进 GC） | 结构体**禁止**继承 `UObject` |
| `UENUM(...)` | 标记枚举参与反射 | **必须**用于 `enum class` |
| `UINTERFACE(...)` | 标记接口的 U 类 | 与 `I` 前缀类成对出现 |
| `UPROPERTY(...)` | 标记成员变量可被反射/序列化/GC 跟踪 | `UObject*` 成员**必须**加 |
| `UFUNCTION(...)` | 标记函数可被反射/蓝图调用 | 蓝图函数**必须**加 `Category` |
| `GENERATED_BODY()` | 在类体内插入 UHT 生成的反射代码 | **必须**在类体内第一行 |
| `GENERATED_USTRUCT_BODY()` | USTRUCT 版本 | 同上 |
| `GENERATED_UCLASS_BODY()` | 旧 API | **禁止**使用 |
| `DECLARE_DYNAMIC_MULTICAST_DELEGATE` | 声明蓝图可绑多播委托 | 见附录 D |

### UHT 工作流程

1. 你写完 `.h` 调用 UHT
2. UHT 解析所有 `UCLASS` / `UFUNCTION` 等宏
3. 生成 `XXX.generated.h` 与 `XXX.gen.cpp` 到 `Intermediate/`
4. C++ 编译器再编译这些生成的文件 + 你的源码

**常见错误**：
- 忘记 `#include "XXX.generated.h"` → 链接报错 `unresolved external symbol Z_Construct...`
- 类名前缀错误 → UHT 直接报错
- USTRUCT 继承 UObject → 编译失败

---

## 附录 B：UPROPERTY Specifier 速查

### B.1 可见性 Specifier

| Specifier | 作用 |
|---|---|
| `EditAnywhere` | 编辑器中任意实例可编辑 |
| `EditDefaultsOnly` | 仅蓝图类默认值可编辑（实例不可改） |
| `EditInstanceOnly` | 仅实例可编辑（蓝图默认值不可改） |
| `VisibleAnywhere` | 编辑器中任意实例可见（只读） |
| `VisibleDefaultsOnly` | 仅蓝图默认值可见（只读） |
| `VisibleInstanceOnly` | 仅实例可见（只读） |

### B.2 蓝图 Specifier

| Specifier | 作用 |
|---|---|
| `BlueprintReadWrite` | 蓝图可读可写 |
| `BlueprintReadOnly` | 蓝图只读 |
| `BlueprintAssignable` | 委托可被蓝图绑定 |
| `BlueprintCallable` | 用于委托，蓝图可调用 |

### B.3 网络同步 Specifier

| Specifier | 作用 |
|---|---|
| `Replicated` | 网络同步（服务端 → 客户端） |
| `ReplicatedUsing=OnXxx` | 同步时回调 `OnXxx` 函数 |
| `RepNotify` | 等价于 `ReplicatedUsing=OnRep_Xxx` |

### B.4 序列化 Specifier

| Specifier | 作用 |
|---|---|
| `Transient` | 运行期临时数据，不序列化 |
| `SaveGame` | 写入 SaveGame |
| `DuplicateTransient` | 复制对象时不复制此字段 |
| `NonPIEDuplicateTransient` | 非 PIE 复制时不复制 |

### B.5 元数据 Specifier（meta=）

| Specifier | 作用 |
|---|---|
| `ClampMin = "0"` | 数值最小值 |
| `ClampMax = "100"` | 数值最大值 |
| `UIMin = "0"` | UI 滑块最小值 |
| `UIMax = "100"` | UI 滑块最大值 |
| `MultiLine = true` | 文本框多行 |
| `PasswordField = true` | 密码输入框 |
| `AllowPrivateAccess = "true"` | 允许蓝图访问 private 成员 |
| `BindWidget` | 蓝图子类中同名控件自动绑定 |
| `EditCondition = "OtherProp"` | 条件可编辑 |
| `DisplayName = "Custom Name"` | 编辑器显示名 |
| `Tooltip = "..."` | 编辑器 tooltip |

---

## 附录 C：UFUNCTION Specifier 速查

### C.1 蓝图 Specifier

| Specifier | 作用 |
|---|---|
| `BlueprintCallable` | 蓝图可调用 |
| `BlueprintPure` | 蓝图可调用且无副作用（隐式 const） |
| `BlueprintNativeEvent` | C++ 提供默认实现，蓝图可覆盖（需 `_Implementation`） |
| `BlueprintImplementableEvent` | 纯蓝图实现（C++ 无实现） |
| `BlueprintAuthorityOnly` | 仅服务端可调用 |

### C.2 网络 RPC Specifier

| Specifier | 作用 |
|---|---|
| `Server` | 客户端调用，服务端执行 |
| `Client` | 服务端调用，Owner 客户端执行 |
| `NetMulticast` | 服务端调用，所有客户端执行 |
| `WithValidation` | Server RPC 必须配套 `_Validate` 函数 |
| `Reliable` | 保证送达（用于关键状态） |
| `Unreliable` | 可丢失（用于高频临时数据） |

### C.3 其他 Specifier

| Specifier | 作用 |
|---|---|
| `Category = "X|Y"` | 蓝图分类（用 `\|` 分层） |
| `DisplayName = "..."` | 蓝图显示名 |
| `ToolTip = "..."` | 蓝图 tooltip |
| `Keywords = "add insert"` | 蓝图搜索关键词 |
| `CallInEditor` | 编辑器中可调用按钮 |
| `Exec` | 控制台命令可调用 |
| `Native` | 仅 C++ 可调用（不暴露蓝图） |
| `BlueprintInternalUseOnly` | 内部使用 |

---

## 附录 D：委托类型选择决策树

```
需要蓝图绑定？
├─ 是 → 多订阅？
│       ├─ 是 → DECLARE_DYNAMIC_MULTICAST_DELEGATE
│       │        + UPROPERTY(BlueprintAssignable)
│       │        最常用：UI 事件、广播
│       └─ 否 → DECLARE_DYNAMIC_DELEGATE
│                单订阅回调，蓝图可绑
└─ 否 → 多订阅？
        ├─ 是 → DECLARE_MULTICAST_DELEGATE
        │        C++ 多播，性能高
        │        用于纯 C++ 内部事件
        └─ 否 → DECLARE_DELEGATE
                 C++ 单订阅回调
                 用于异步任务完成回调
```

### D.1 参数个数后缀

| 参数数 | 宏后缀 |
|---|---|
| 0 | 无后缀 |
| 1 | `_OneParam` |
| 2 | `_TwoParams` |
| 3-9 | `_ThreeParams` ~ `_NineParams` |
| >9 | 不支持，需封装为 struct |

### D.2 委托使用模板

```cpp
// 声明
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
    FOnSlotChangedSignature,        // 委托类型名
    int32, slot_index,                // 参数1 类型 + 名字
    const FFlexiItemDelta&, delta);   // 参数2 类型 + 名字

// 类中声明成员
UCLASS()
class UFlexiBagComponent : public UActorComponent {
    GENERATED_BODY()

    UPROPERTY(BlueprintAssignable, Category = "Events")
    FOnSlotChangedSignature on_slot_changed;
};

// C++ 绑定
on_slot_changed.AddDynamic(this, &UMyClass::handle_slot_change);

// 蓝图绑定：在 Details Panel 直接 Assign

// 触发
on_slot_changed.Broadcast(slot_index, delta);

// 解绑（NativeDestruct 中必须）
on_slot_changed.RemoveDynamic(this, &UMyClass::handle_slot_change);
```

### D.3 动态委托 vs 非动态委托

| 特性 | 动态委托（DYNAMIC） | 非动态委托 |
|------|------|------|
| 蓝图可绑 | ✅ | ❌ |
| 性能 | 慢（走反射） | 快（直接函数指针） |
| 参数类型限制 | 仅反射支持类型 | 任意 C++ 类型 |
| 序列化 | ✅ | ❌ |
| 适用场景 | UI 事件 | 纯 C++ 内部事件 |

---

## 附录 E：UE5 容器选择决策树

```
需要存储键值对？
├─ 是 → 需要有序遍历？
│       ├─ 是 → TMap<K, V>（红黑树，O(log n)）
│       └─ 否 → 需要按插入顺序？
│               ├─ 是 → 用 TArray<int32> + TMap<KeyType, int32> 索引
│               └─ 否 → TMap<K, V>（默认哈希）/ TSet<K>
└─ 否 → 顺序访问？
        ├─ 是 → 头尾高效增删？
        │       ├─ 是 → TDeque（UE5.2+）/ TArray 当作双端
        │       └─ 否 → TArray（默认首选，缓存友好）
        └─ 否 → 固定大小？
                ├─ 是 → TFixedArray / std::array（栈分配）
                └─ 否 → TArray
```

### E.1 容器选择原则

- **默认首选** `TArray`：缓存友好、内存连续、随机访问 O(1)
- **禁止**使用 `std::list` / UE5 无原生链表：缓存不友好、内存碎片
- 字符串容器**必须**使用 `TArray<FString>` 或 `FString`，**禁止** `const TCHAR*` 容器
- 网络同步数组**必须**使用 `FFastArraySerializer` 包装

### E.2 常见场景对照

| 场景 | 推荐容器 | 原因 |
|------|---------|------|
| 动态数组 | `TArray` | 默认首选 |
| 固定大小数组 | `TFixedArray` / `std::array` | 栈分配 |
| 哈希查找 | `TMap` | O(1) 查找 |
| 有序遍历 | `TMap<K, V, EDefaultKeySortPredicate>` | 按键排序 |
| 去重集合 | `TSet` | O(1) 查找 |
| 字符串 | `FString` / `FName` / `FText` | UE5 三种字符串各有用途 |
| 网络同步数组 | `TArray<T>` + `FFastArraySerializer` | 增量同步 |
| 软引用 | `TSoftObjectPtr` | 不阻止 GC |
| 弱引用 | `TWeakObjectPtr` | 防止循环引用 |
| 栈结构 | `TArray` + `Push`/`Pop` | 比适配器更灵活 |
| 队列结构 | `TDeque`（UE5.2+）/ `TQueue` | 头尾 O(1) |
| 优先队列 | `TArray` + `HeapPush`/`HeapPop` | 堆实现 |

> 容器性能要点（`Reserve()` 预分配、`Emplace` 替代 `Add`）见正文 13.3。

---

## 附录 F：C++ 规范与 UE5 冲突仲裁表

C++ 通用规范与 UE5 引擎约束发生冲突时，按下表仲裁：

| 冲突点 | C++ 规范 | UE5 约束 | 仲裁结果 | 理由 |
|--------|----------|----------|----------|------|
| 头文件包含顺序 | 对应实现 → C 标准库 → C++ 标准库 → 第三方 → 项目 | `CoreMinimal.h` 必须最前 | **UE5 优先** | UHT/PCH 强制要求 |
| 类命名后缀 | `_t`（如 `manager_t`） | U/A/F/E/I/T 前缀，无 `_t` | **UE5 优先** | `_t` 后缀与蓝图 API 冲突 |
| UPROPERTY 成员后缀 | `_`（如 `mutex_`） | 不带后缀 | **UE5 优先** | 反射系统直接暴露给蓝图 |
| 私有方法后缀 | `_`（如 `init_()`） | 不带后缀 | **UE5 优先** | 与 UFUNCTION 命名一致 |
| 函数体内注释 | 禁止 | 同 C++ 规范 | **遵循 C++ 规范** | 无冲突 |
| 类结构顺序 | public 类型 → private 成员 → private 方法 → public 方法 | 同 C++ 规范 | **遵循 C++ 规范** | 无冲突 |
| `enum class` | 必须 | 同 C++ 规范 | **遵循 C++ 规范** | UE5 也推荐 `enum class` |
| `nullptr` | 必须 | 同 C++ 规范 | **遵循 C++ 规范** | 无冲突 |
| 异常处理 | 默认错误码/optional | UE5 默认关闭异常 | **遵循 C++ 规范** | 无冲突，UE5 也禁用异常 |
| `std::string_view` | 视为非所有权视图 | UE5 用 `FStringView` | **UE5 优先** | 与 `FString` 配套 |
| `std::span` | 替代 `const T*` + `size_t` | UE5 用 `TArrayView` | **UE5 优先** | 与 UE5 容器配套 |
| 智能指针 | `std::unique_ptr` / `std::shared_ptr` | `TUniquePtr` / `TSharedPtr`（UObject 用 GC） | **UE5 优先** | UObject 必须由 GC 管理 |
| `std::thread` | 用 `std::jthread` | UE5 用 `FAsyncTask` / `TFuture` | **UE5 优先** | 与 UE5 任务系统配套 |
| `std::function` | 通用 | `TFunction` | **UE5 优先** | UE5 内存分配优化 |
| `std::optional` | 通用 | `TOptional` | **UE5 优先** | UE5 内存分配优化 |
| `std::map` / `std::unordered_map` | 通用 | `TMap` | **UE5 优先** | 与 UE5 反射/序列化配套 |
| `std::string` | 通用 | `FString` / `FName` / `FText` | **UE5 优先** | UE5 三种字符串各有用途 |
| `cout` / `printf` | （C++ 规范本身也禁止） | `UE_LOG` | **UE5 优先** | UE5 日志系统集成 |
| 单例模式 | `std::call_once` + `std::once_flag` | `USubsystem` | **UE5 优先** | UE5 原生生命周期管理 |
| 模板 UCLASS | 允许 | UHT 不支持 | **UE5 优先** | 反射系统限制 |

---

## 附录 G：版本履历

| 版本 | 日期 | 变更摘要 |
|:---:|:---:|---|
| **2.1.0** | 2026-10-14 | **新增必要防御原则**：第 7.4 节强化引擎上下文与架构契约信任，明确非确定不判断就会出错绝不添加判断，严禁在已被保证的回调中层层判空。 |
| **2.0.0** | 2026-10-14 | **架构重大升级**：剥离原第 26、27 章 AI 协作与行为规范至全局《AI行为规范》；基准规范对齐最新的《代码规范(C:C++) v6.0.0》；保持 UE5 纯引擎技术标准的高内聚与纯粹性。 |
| 1.7.0 | 2026-09-19 | 补充项目命名推断与 AI 交付前自查清单。 |
| 1.0.0 | 2026-06-24 | 初始版本。 |

