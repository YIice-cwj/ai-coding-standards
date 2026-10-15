# C++ 代码规范 (C++ Coding Standards)

**版本**: 6.2.0  **日期**: 2026-10-15  **语言**: C++20 / C++23 (最低兼容 C++17)

> **行为规范继承**：AI 编码助手在执行本规范代码任务时，**必须严格遵循 [AI行为规范.md](./AI行为规范.md)**（含 5 阶执行模型、最小变更、计划先行与高强度验证）。
> **适用范围**：所有 C++ 新代码；修改老代码时遵循最小变更原则，不强制重构未触及的代码。
> **优先级（高→低）**：[AI行为规范](./AI行为规范.md) > 安全规范（16）> 正确性（11, 14）> 可读性（3, 4）> 性能（10）> 风格（1, 2）。
> **版本规则**：遵循语义化版本（SemVer）。

---

## 目录

- [1. 代码格式与排版](#1-代码格式与排版)
- [2. 命名规范](#2-命名规范)
- [3. 注释规范](#3-注释规范)
- [4. 类结构规范](#4-类结构规范)
- [5. 头文件与依赖规范](#5-头文件与依赖规范)
- [6. 函数设计规范](#6-函数设计规范)
- [7. 现代 C++ 核心特性](#7-现代-c-核心特性)
- [8. 构造、移动语义与生命周期](#8-构造移动语义与生命周期)
- [9. 模板与泛型编程](#9-模板与泛型编程)
- [10. 性能与最佳实践](#10-性能与最佳实践)
- [11. 错误处理与返回值](#11-错误处理与返回值)
- [12. 日志规范](#12-日志规范)
- [13. 并发与多线程](#13-并发与多线程)
- [14. 内存管理与资源安全](#14-内存管理与资源安全)
- [15. 宏与预处理器](#15-宏与预处理器)
- [16. 安全编码规范](#16-安全编码规范)
- [17. 测试与构建规范](#17-测试与构建规范)
- [18. 架构设计与工程七大守则](#18-架构设计与工程七大守则)
- [附录 A：容器选择决策树](#附录-a容器选择决策树)
- [附录 B：C++ 编码高频自检对照表](#附录-bc-编码高频自检对照表)
- [附录 C：版本履历](#附录-c版本履历)

---

## 1. 代码格式与排版

### 1.1 缩进
- **必须**使用 4 空格缩进，**严禁**使用 Tab。

### 1.2 大括号与代码块
- 类、函数、控制语句、命名空间的大括号与关键字**必须**在同一行（K&R / OTB 风格）。
- **禁止**大括号单独占一行。

### 1.3 头文件引用顺序
头文件包含**必须**按以下优先级自顶向下排列，组间**必须**用空行分隔：
1. 本文件对应的头文件/实现接口（如 `foo.cc` 中优先 `#include "foo.h"`）
2. C 标准库（如 `<cstddef>`, `<cstdint>`）
3. C++ 标准库（如 `<vector>`, `<string>`, `<memory>`）
4. 第三方库（如 `<boost/...>`, `<fmt/...>`）
5. 项目内部头文件（如 `"core/manager.h"`）

### 1.4 文件编码与换行
- **必须**使用 UTF-8 无 BOM 编码。
- **必须**使用 LF（`\n`）换行符，**严禁**使用 CRLF。

---

## 2. 命名规范

> **项目优先原则**：进入已有项目时，AI **必须**先分析现有代码的类、函数、变量命名风格并严格保持一致；仅在无既有项目约定时遵循本章规范。

### 2.1 类型命名
- `class` / `struct` / `enum` / `using` 类型名**必须**使用小写下划线并以 `_t` 结尾。
- 接口抽象类**必须**使用 `i_` 前缀 + `_t` 后缀（如 `i_handler_t`），且**必须**声明虚析构函数。
- **禁止**使用 `typedef`，统一使用 `using`。

| 类型分类 | 命名规则 | 正确示例 | 错误示例 |
|---|---|---|---|
| 类 / 结构体 | `小写_t` | `task_manager_t`, `user_data_t` | `TaskManager`, `tagUserData` |
| 接口类 | `i_小写_t` | `i_network_service_t` | `INetworkService`, `network_service` |
| 枚举类 | `小写_t` | `status_t` | `Status`, `EStatus` |
| 类型别名 | `using ... = ..._t` | `using id_t = std::uint64_t;` | `typedef uint64_t id_t;` |

### 2.2 枚举类型
- **必须**使用 `enum class`（强类型作用域枚举），**严禁**裸 `enum`。
- 枚举成员命名**必须**为全小写下划线，以 `类型_t::值` 访问。
- 示例：`enum class state_t { idle, running, stopped };`

### 2.3 变量命名
- 普通变量、局部变量、函数形参**必须**使用小写下划线：`user_id`, `is_active`。
- **禁止**驼峰命名法（`userId`, `bActive`）或匈牙利命名法。

### 2.4 类成员变量
- 私有（private）及保护（protected）成员变量**必须**以单下划线 `_` 结尾。
- 示例：`std::string name_;`、`int retry_count_;`。
- **禁止**下划线开头（`_name`）或 `m_` 前缀。

### 2.5 成员函数
- 普通成员函数**必须**使用小写下划线：`calculate_total()`, `get_name()`。
- 私有成员函数（private）**建议**使用单下划线 `_` 结尾，与私有成员变量保持对称（如 `init_internal_()`）。
- **严禁**使用双下划线前缀 `__`（C++ 保留标识符，触发未定义行为）。
- **严禁**使用单下划线前缀 `_`（避免与系统级实现符号冲突）。

### 2.6 常量与全局变量
- 常量（`constexpr` / `const`）**必须**使用全大写加下划线：`MAX_BUFFER_SIZE`。
- 全局变量（严格限制使用）**必须**添加 `global_` 前缀：`global_config`。

### 2.7 命名空间
- 命名空间**必须**使用小写字母，单词之间使用下划线分隔或直接小写连接：`namespace core::net`。

---

## 3. 注释规范

### 3.1 文件头注释
所有 `.h` / `.hpp` 头文件顶部**必须**包含文件头注释，标明文件职责与所属模块。

### 3.2 函数注释与内部无注释原则
- 函数声明/定义上方**必须**使用 `/** */` Doxygen 格式文档注释，说明功能、参数、返回值及异常安全性。
- **核心铁律：禁止在函数体内添加任何业务解释性行内或块注释**。函数的实现思路、核心算法、关键步骤与注意事项**必须集中写在函数上方的文档注释中**。
- **唯一例外**：允许且仅允许代码静态分析/编译器抑制指令（如 `// NOLINT`、`/* fallthrough */`）。
- 若函数体内部逻辑必须依靠解释性注释才能看懂，说明函数违反了单一职责或过于复杂，**必须予以拆分**。

**正例**：
```cpp
/**
 * @brief 计算用户综合评分
 * @param user 待计算的用户数据结构体
 * @return 综合折算后的最终得分
 *
 * 实现思路：基础积分 + (连续活跃天数 * 每日加成) - (违规次数 * 扣分权重)
 */
int calc_score(const user_t& user) {
    const int base = user.base_score;
    const int bonus = user.active_days * BONUS_PER_DAY;
    const int penalty = user.violations * PENALTY;
    return base + bonus - penalty;
}
```

**反例**：
```cpp
int calc_score(const user_t& user) {
    int base = user.base_score;
    int bonus = user.active_days * BONUS_PER_DAY;  // 计算活跃天数加成（错！禁止行内注释）
    int penalty = user.violations * PENALTY;       // 扣除违规惩罚（错！禁止行内注释）
    return base + bonus - penalty;                  // 返回总分（错！废话注释）
}
```

---

## 4. 类结构规范（接口优先原则）

类声明内部**必须**严格遵循以下 15 层顺序组织，使结构具备高度确定性并坚持“公开接口优先 (Interface-First)”：

```
class example_t {
public:
    // 1. public 类型定义 (using / enum class)
protected:
    // 2. protected 类型定义
private:
    // 3. private 类型定义
public:
    // 4. public 常量 (static constexpr)
protected:
    // 5. protected 常量
private:
    // 6. private 常量
public:
    // 7. public 成员函数 (构造/析构/核心业务接口 - 接口优先对外展现)
protected:
    // 8. protected 成员函数
private:
    // 9. private 成员函数 (带 _ 后缀)
public:
    // 10. public 静态函数
protected:
    // 11. protected 静态函数
private:
    // 12. private 静态函数
private:
    // 13. private 成员变量与静态变量 (带 _ 后缀，实现细节封装于底)
protected:
    // 14. protected 成员变量与静态变量
public:
    // 15. public 成员变量与静态变量 (纯数据 POD/struct 除外，普通 class 极力避免)
};
```

- **实现顺序对齐**：源文件（`.cc` / `.cpp`）中的函数实现顺序，**必须与头文件类声明中的先后顺序 1:1 严格对齐**，禁止乱序排布。

---

## 5. 头文件与依赖规范

| 文件后缀 | 对应职责 |
|---|---|
| `.h` | 类与接口的纯声明 |
| `.cc` / `.cpp` | 业务与函数实现 |
| `.hpp` | Header-only 库专用（声明+实现内联） |
| `.inl` | 模板与复杂内联函数的实现文件 |

- **Header Guard**：**必须**统一使用 `#pragma once`。
- **前向声明**：头文件中能使用前向声明（Forward Declaration）解决的指针/引用依赖，**必须**使用前向声明，减少物理编译耦合。
- **内联放置**：头文件内的小型内联函数，**必须**集中放置在对应权限区域末尾，禁止穿插在普通声明之间。

---

## 6. 函数设计规范

### 6.1 基本设计约束
- **函数长度**：单个函数代码行数**建议控制在 50 行以内**；超过必须拆分。
- **参数个数**：函数参数**建议不超过 4 个**；过多时必须封装为配置结构体。
- **禁止输出参数**：**禁止**使用非 const 引用作为出参传出结果，必须通过返回值、`std::pair`、结构体或 `std::optional` / `std::expected` 返回。

### 6.2 控制流线性化与提前返回 (Guard Clause)
- 主逻辑**必须**保持线性一路向下，**禁止**深层嵌套与逻辑在多分支中反复横跳。
- **必须**使用提前返回（Guard Clause）在函数入口前置拦截无效条件：

**正例**：
```cpp
bool process_message(const packet_t& packet) {
    if (!packet.is_valid()) {
        return false;
    }
    if (packet.payload().empty()) {
        return false;
    }
    return execute_dispatch(packet);
}
```

**反例**：
```cpp
bool process_message(const packet_t& packet) {
    if (packet.is_valid()) {
        if (!packet.payload().empty()) {  // 错！多层嵌套，逻辑右漂
            return execute_dispatch(packet);
        }
    }
    return false;
}
```

### 6.3 必要防御原则与严禁过度防御（Like Human Engineers）
- **核心铁律：非确定不判断就会出错，绝不添加判断**。
  - AI **必须像资深人类工程师一样思考与编码**，只在真正的关键边界（系统外部不可信输入、或接口显式契约声明可能返回空指针/失败态）做必要校验。
  - **严禁过度防御**：绝不能因为某个地方出错的几率只有 0.1% 甚至 0% 就去写一个防御分支；**严禁**为不存在或概率极低的臆想场景层层设卡。
- **充分信任 C++ 语言契约与内部不变式**：
  - **引用语义**：通过引用（`const T&` 或 `T&`）传入的参数，C++ 语言标准在语法层面已保证其必然绑定有效对象，**严禁判断 `&param == nullptr`**。
  - **this 指针**：类成员函数内 **严禁判断 `this == nullptr`**（在标准 C++ 中这是未定义行为且现代编译器会直接优化掉）。
  - **类不变式**：由类构造函数与内部状态机维护的不变量（如计数非负、缓冲区容量合法等），内部私有函数调用时**严禁重复做有效性检查**。
  - **新分配内存**：`std::make_unique` / `std::make_shared` / `new` 失败默认抛出 `std::bad_alloc`，**严禁在之后判断返回指针是否为 `nullptr`**。
- **防御边界划分准则**：
  - **外部不可信边界（必须校验）**：网络/反序列化入参、未经验证的用户输入、Public 导出 SDK 接口（如对外的 C API 或头文件库需防护非法调用）。
  - **内部受信任链路（信任契约）**：类不变式、引用传递、已断言校验的对象。严禁在内部可信路径层层重复设卡。

**正例（像资深人类工程师一样直接、清晰）**：
```cpp
/**
 * @brief 添加物品到背包。仅在超过物理容量这一真实业务边界时返回失败。
 */
bool inventory_t::add_item(const item_t& item) {
    if (items_.size() >= capacity_) {
        return false;
    }
    items_.push_back(item);
    return true;
}
```

**反例（AI 典型的神经过敏过度防御）**：
```cpp
// 错！典型的过度防御：堆砌了 5 处根本不可能发生或纯属臆想的无用检查
bool inventory_t::add_item(const item_t& item) {
    if (this == nullptr) { return false; }         // 错！this 绝不可能为空
    if (&item == nullptr) { return false; }        // 错！引用绝不可能为空
    if (capacity_ <= 0) { return false; }          // 错！构造函数已保证 capacity_ > 0
    if (item.id() <= 0) { return false; }          // 错！内部上游已校验 item 合法性
    if (items_.size() > 1000000) { return false; } // 错！虚构的 0.1% 极端情况臆想防御

    if (items_.size() >= capacity_) {
        return false;
    }
    items_.push_back(item);
    return true;
}
```

---

## 7. 现代 C++ 核心特性

### 7.1 初始化规则
- **优先**使用大括号列表初始化 `{}` 防止隐式窄化转换。
- **例外**：当 `{}` 会被优先解析为 `std::initializer_list` 从而改变语义时（如 `std::vector<int> v(10, 0)` 创建 10 个 0），**必须**使用圆括号 `()`。
- **必须**使用 `nullptr`，**严禁**使用 `NULL` 或裸字面量 `0` 表示空指针。

### 7.2 auto 类型推导
- `auto` **必须**在声明时立即初始化，**禁止**用于无明显初始类型推导的场景。
- **禁止的 auto 反模式**：
  ```cpp
  auto x = {1, 2, 3};      // 错！推导为 std::initializer_list<int> 而非 vector
  auto* p = new widget_t;   // 错！严禁裸 new
  ```

### 7.3 结构化绑定与编译期分支
- 多返回值与键值对解构**必须**使用结构化绑定（C++17）：`const auto& [id, name] = *record_iter;`。
- 编译期分支**必须**使用 `if constexpr` 代替 SFINAE。

### 7.4 C++20 Concept 与模板约束
- 模板参数约束**必须优先使用 C++20 `concept`**，替代过时的 `std::enable_if_t` / SFINAE：

**正例**：
```cpp
template<std::integral T>
T add(T a, T b) noexcept {
    return a + b;
}
```

**反例**：
```cpp
template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>
T add(T a, T b) { return a + b; }  // 错！过时的 SFINAE
```

### 7.5 标准属性 (Attributes)
- 有返回值且忽略返回值属于严重逻辑漏洞的函数，**必须**标记 `[[nodiscard]]`：
  ```cpp
  [[nodiscard]] bool connect();
  [[nodiscard]] std::unique_ptr<session_t> create_session();
  ```
- 接口预留或回调中暂未使用的形参，**必须**显式标记 `[[maybe_unused]]`，**禁止**使用 `(void)param;` 强转：
  ```cpp
  void on_notify([[maybe_unused]] const event_t& evt) noexcept {}
  ```

---

## 8. 构造、移动语义与生命周期

### 8.1 构造与析构
- 单参数构造函数**必须**标记为 `explicit`，杜绝隐式类型转换。
- **必须**在成员变量声明处执行默认成员初始化（Default Member Initializer），**禁止**在构造函数体内做简单赋值初始化。
- 派生类重写虚函数**必须**标注 `override`，**禁止**在同一函数同时使用 `virtual` 和 `override`。
- 不修改成员状态的成员函数**必须**严格标记为 `const`。

### 8.2 特殊成员函数策略 (Rule of 0 / Rule of 5)
- **优先 Rule of 0**：使用标准库容器与智能指针管理资源，不显式声明任何析构函数、拷贝/移动函数，交由编译器默认合成。
- **严格 Rule of 5**：一旦因持有外部原生句柄而自定义了析构函数、拷贝或移动函数中的任意一个，**必须显式声明全部 5 个特殊成员函数**（`= default`, `= delete` 或自定义实现）。

### 8.3 移动语义与 noexcept
- 移动构造函数和移动赋值运算符**必须**标记 `noexcept`。若未标注 `noexcept`，STL 容器在扩容重新分配时将降级为深拷贝。
- 不抛出异常的函数（查表、纯数值计算、析构、swap 等）**必须**显式标记为 `noexcept`。

---

## 9. 模板与泛型编程

### 9.1 类模板语义化别名
- 类模板**必须**通过 `using` 为模板参数及派生类型定义标准的语义别名（如 `value_type`, `size_type`, `reference` 等），放置在 public 类型定义区。
- 类模板内部（含成员函数参数与返回值）**禁止直接出现裸类型形参 `T`**，必须使用别名：

**正例**：
```cpp
template<typename T>
class buffer_queue_t {
public:
    using value_type = T;
    using size_type  = std::size_t;

    [[nodiscard]] size_type size() const noexcept;
    void push(const value_type& val);
};
```

### 9.2 模板实现分离与 .inl
- 类模板与函数模板的复杂实现**必须**放置在 `.inl` 文件中，并在对应头文件末尾使用 `#include "xxx.inl"` 引入。
- 极短实现（1~3 行的简单 getter/转发或概念受约束函数）**允许**直接内联在头文件类体内。
- **禁止**将模板实现单独写入 `.cpp`（显式实例化特例除外）。

---

## 10. 性能与最佳实践

### 10.1 返回值优化 (RVO/NRVO)
- 返回局部对象时，**必须直接按值返回局部变量**，依靠编译器的 RVO / NRVO。
- **严禁对局部返回值使用 `std::move`**：这会阻止编译器的 NRVO 优化，反而强制引发一次移动构造：

**正例**：
```cpp
payload_t make_payload() {
    payload_t p;
    p.init();
    return p;  // 正确：NRVO 零拷贝
}
```

**反例**：
```cpp
payload_t make_payload() {
    payload_t p;
    p.init();
    return std::move(p);  // 错！禁用 NRVO，产生额外开销
}
```

### 10.2 容器使用最佳实践
- 容器在已知元素数量或能够估算上限时，**必须在填充前调用 `reserve()`** 预分配容量，杜绝连续扩容导致的重复内存拷贝。
- 插入元素**优先**使用 `emplace_back` / `emplace` 替代 `push_back` / `insert`，原位构造避免临时对象。
- 顺序容器**默认首选 `std::vector`**，**严禁默认使用 `std::list`**（节点离散分配导致极高的缓存不命中率与内存开销）。

---

## 11. 错误处理与返回值

### 11.1 错误处理模型选择
- 核心业务与高性能路径**必须默认使用状态码 / `std::optional` / `std::expected`（C++23 或 Polyfill）** 表示可能发生的可恢复故障。
- **仅在系统/第三方库边界且必要时**方可使用 C++ 异常。

### 11.2 异常处理硬约束
- **严禁裸 `catch(...)`** 默默吞掉异常。
- **禁止捕获过宽异常基类**（如 `catch (const std::exception&)`），必须精确捕获具体的异常类型（如 `std::filesystem::filesystem_error`）。
- **禁止在构造函数与析构函数中抛出异常**：构造失败通过静态工厂方法返回 `std::expected` / `std::optional`；析构函数抛出异常会直接导致 `std::terminate`。

---

## 12. 日志规范

- **严禁**在业务生产代码中使用裸 `std::cout`, `printf`。
- **必须**使用统一的结构化日志库，并按严重等级严格划分（`DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`）。
- 日志格式**必须**统一包含：时间戳、日志级别、文件名/行号、线程 ID、业务上下文。
- **严禁在日志中打印敏感信息**（密码、密钥、Token、未脱敏个人隐私）。
- **严禁在高频循环内部输出无限制的 INFO 级日志**。

---

## 13. 并发与多线程

### 13.1 锁与同步原语
- 互斥锁**必须**使用 RAII 管理器（`std::lock_guard`, `std::unique_lock`, `std::scoped_lock`），**严禁**手动调用 `.lock()` 和 `.unlock()`。
- 需要同时持有多个互斥锁时，**必须使用 `std::scoped_lock`** 消除死锁隐患。
- 读多写少场景**必须使用 `std::shared_mutex`**（读端 `std::shared_lock`，写端 `std::unique_lock`）。
- **禁止使用 `std::recursive_mutex`**（通常反映出锁粒度设计混乱）。
- **严禁在持锁区间内执行耗时 I/O 或外部不可控回调**。

### 13.2 线程管理
- **必须优先使用 `std::jthread` (C++20)** 替代裸 `std::thread`，依靠其析构自动 join 与内置 `std::stop_token` 机制确保安全退出。
- 若在 C++17 环境使用 `std::thread`，**必须**确保在所有退出路径中显式 `join()`。

### 13.3 原子操作与条件变量
- 共享简单标志位**必须使用 `std::atomic<bool>`**，禁止使用 `volatile` 做线程间同步。
- 默认使用顺序一致性 `memory_order_seq_cst`；仅在性能基准测试证明存在瓶颈时方可使用宽松内存序。
- 条件变量等待**必须使用谓词版本 `cv.wait(lk, [&]{ return ready; })`**，防止虚假唤醒（Spurious Wakeup）。

---

## 14. 内存管理与资源安全

### 14.1 RAII 与智能指针
- **绝对禁止裸 `new` 与裸 `delete`**。所有动态内存分配必须直接交由智能指针托管。
- 独占所有权使用 `std::unique_ptr`（通过 `std::make_unique` 创建）。
- 共享所有权使用 `std::shared_ptr`（通过 `std::make_shared` 创建）。
- 存在相互观察或父子回环引用风险时，**必须使用 `std::weak_ptr` 打破循环引用**。
- 类构造函数内部**严禁**使用裸 `new[]` 分配原始数组，必须使用 `std::vector` 或 `std::array`。

### 14.2 智能指针选择决策树
```
是否需要共享所有权？
├─ 是 ──► 存在循环引用风险？
│          ├─ 是 ──► std::weak_ptr<T> (观察者，无所有权)
│          └─ 否 ──► std::shared_ptr<T> (通过 std::make_shared 创建)
└─ 否 ──► 是否需要堆动态生命周期？
           ├─ 是 ──► std::unique_ptr<T> (通过 std::make_unique 创建)
           └─ 否 ──► 优先栈对象或值语义传递
```

---

## 15. 宏与预处理器

- **优先**使用 `constexpr` 常量替代 `#define` 常量。
- **优先**使用 `inline` / `constexpr` 函数或泛型模板替代宏函数。
- 必须定义的条件编译宏**必须使用全大写加下划线**。
- 包含多条语句的必要宏**必须使用 `do { ... } while(0)` 包裹**。
- **禁止**使用宏拼接代码来模拟模板或泛型机制。

---

## 16. 安全编码规范

### 16.1 危险函数替代
- **严禁**使用 C 风格不安全字符串函数：`strcpy`, `strcat`, `sprintf`, `strncpy`。
- **必须优先使用** `std::string`, `std::string_view`, `std::format` (C++20)；在与 C 接口互操作时必须使用带边界检查的 `snprintf`。
- **禁止**使用 C 标库 `rand()` 生成安全相关的随机数，**必须使用 `<random>` 中的 `std::random_device`**。

### 16.2 视图类型与悬垂生命周期安全
- `std::string_view` 与 `std::span` 均为**非所有权视图**，生命周期完全依附于源对象。
- **严禁返回指向局部临时对象的 `std::string_view` 或 `std::span`**（悬垂引用未定义行为）。
- **类成员变量禁止使用 `std::string_view`** 存储字符串字段，必须使用拥有独立内存所有权的 `std::string`。
- 函数参数需要连续内存切片时，**必须使用 `std::span<const T>`** 替代过时的 `const T* + size_t` 裸指针传参组合。

---

## 17. 测试与构建规范

- **工程构建**：**必须**使用 Modern CMake 管理项目，统一开启编译警告与静态分析：`-Wall -Wextra -Wpedantic -Werror`。
- **单测覆盖**：所有新增核心业务模块**必须**配套单元测试（如 GoogleTest / Catch2），覆盖正常通路、边界条件与错误路径。
- **异步测试禁 sleep**：测试异步逻辑时，**严禁使用 `std::this_thread::sleep_for`** 盲等，必须使用条件变量、Promise/Future 或事件同步通知。

---

## 18. 架构设计与工程七大守则

所有 C++ 架构设计与重构必须符合软件工程七大基本原则：
1. **单一职责 (SRP)**：每个类与函数只专注于完成一件事。
2. **开闭原则 (OCP)**：对扩展开放，对修改关闭；通过多态或策略模式进行功能扩展。
3. **里氏替换 (LSP)**：子类必须能安全透明地替换基类接口。
4. **依赖倒置 (DIP)**：高层模块必须依赖抽象接口（`i_xxx_t`），严禁直接耦合具体实现。
5. **接口隔离 (ISP)**：接口设计精简独立，严禁把大量不相关功能聚合在单一巨型接口中。
6. **DRY 原则**：严禁复制粘贴代码，公共计算与校验逻辑必须收敛复用。
7. **KISS 原则**：保持实现简单直接，严禁毫无价值的过度设计与过早泛化。

---

## 附录 A：容器选择决策树

```
需要存储键值对 (Key-Value)？
├─ 是 ──► 是否要求按键有序遍历？
│          ├─ 是 ──► std::map / std::set (红黑树，O(log N))
│          └─ 否 ──► std::unordered_map / std::unordered_set (哈希表，平均 O(1))
└─ 否 ──► 顺序线性容器：
           ├─ 是否编译期固定大小？
           │    └─ 是 ──► std::array (栈分配，零额外开销)
           └─ 动态大小：
                ├─ 是否需要高效的首尾两端双向插入/弹出？
                │    └─ 是 ──► std::deque (双端队列)
                └─ 默认通用场景 ──► std::vector (连续内存、缓存友好、局部性最佳)
```

> **注意**：除频繁在超大序列中间进行节点级拆分拼接且完全无需随机访问的罕见场景外，**严禁默认使用 `std::list`**。

---

## 附录 B：C++ 编码高频自检对照表

在输出 C++ 代码前，对照下表快速核验常见语法陷阱：

| 检查维度 | 合规要求 | 常见反模式拦截 |
|---|---|---|
| **空指针** | 使用 `nullptr` | 出现 `NULL` 或字面量 `0` |
| **单参构造** | 声明 `explicit` | 隐式转换构造导致偶发类型转换 bug |
| **虚函数重写** | 显式标注 `override` | 漏标 `override` 导致签名变更时虚函数失效 |
| **常量修饰** | 观察方法全标注 `const` | 成员函数明明不改状态却漏加 `const` |
| **移动操作** | 移动构造与移动赋值标注 `noexcept` | 漏标 `noexcept` 导致 `vector` 扩容退化为深拷贝 |
| **返回值优化** | 直接按值返回局部变量 | 多余写了 `return std::move(local_var);` 阻断 NRVO |
| **视图生命周期** | string_view 绝不绑定临时对象，类成员不用 string_view | 返回了函数内部局部变量的 view 导致悬垂内存 |
| **资源安全** | 绝无裸 new/delete，全用 make_unique/make_shared | 出现裸 `delete ptr;` 或直接 `new` 赋值 |
| **类型别名** | 模板类提供 `value_type`，使用 `using` | 模板内满屏直接裸写 `T`，或使用 `typedef` |
| **控制流** | 提前返回，严禁过度防御（非必死不判断） | 多层嵌套 `if`；对引用、this 或内部已有指针重复判断；为 0.1% 极小概率设卡 |

---

## 附录 C：版本履历

| 版本 | 日期 | 变更摘要 |
|:---:|:---:|---|
| **6.2.0** | 2026-10-15 | **消除冲突与接口优先**：类结构重构为现代工业标准“公开接口优先 (Interface-First)”15 层布局；放行 Linter 抑制指令；消除 6.3 正例行内注释；明确划定不可信边界与 SDK 防御边界。 |
| **6.1.0** | 2026-10-14 | **新增必要防御原则**：第 6.3 节扩充 C++ 引用语义、this 指针、类不变式与动态内存分配的信任规则；明确"非确定不判断就会出错绝不判断"铁律，增加正反例代码对比。 |
| **6.0.0** | 2026-10-14 | **架构重大升级**：彻底剥离 AI 行为与协作规范至独立全局《AI行为规范》；本规范更名为《代码规范(C:C++)》，全面纯化为 C++ 领域标准；优化现代特性排版与高频自检对照表。 |
| 5.5.0 | 2026-09-19 | 第 4 章类结构顺序表重排扩展：新增 private 类型定义、常量三层块、静态函数访问级别细分。 |
| 5.4.0 | 2026-09-19 | 新增命名规范项目优先原则与反模式清单。 |
| 5.0.0 | 2026-08-22 | 章节重构精简，新增需求确认与计划先行原则。 |
