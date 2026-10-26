# 通用 · API 与接口契约规范

**所属域**: 10-通用代码规范  **域版本**: 2.9.0  **日期**: 2026-10-26  **类型**: 多语言通用基准

> **SSOT 声明**：API 契约设计、幂等性、分页标准与向下兼容演进的唯一事实源。
> **关联文档**：[核心铁律](../00-行为规范/01-核心铁律与五阶执行模型.md) · [架构健壮性](./02-架构健壮性与工程安全.md) · [代码可读性](./04-代码可读性与心智负荷.md) · [审查规范](../50-审查规范/01-代码审查规范.md)

---

## 1. 核心契约红线对照表

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-API-IDEMP]** | MUST | 核心写操作必须支持 `Idempotency-Key`；并发以 `(caller, key)` 互斥并持久化结果 | 支付/扣减等非只读接口无防重机制；网络重试引发重复扣款 |
| **[R-API-BOUND]** | MUST | 集合接口必须强制分页；设置默认值（`20`）与硬上限（`100`）；超限主动截断 | 提供无上限全量查询（`list_all()`）；允许客户端传入任意大 Limit |
| **[R-API-CURSR]** | MUST | 高频/海量/实时流数据强制使用游标分页（Cursor-based：自增 ID/时戳组合） | 大数据量使用深度偏移分页（`OFFSET M` 导致全表扫描与数据漂移） |
| **[R-API-COMPAT]**| MUST | 对外契约遵循**只增不减**：新字段必须可选（`optional`）且具备兼容默认值 | 直接删除/重命名已有公共字段；变更已有字段数据类型或相反语义 |
| **[R-API-DEPR]**  | MUST | 废弃遵循展开-收缩：①`[[deprecated]]` 声明；②双轨并存 $\ge 2$ 版本；③流量归零下线 | 直接硬删除正在运行调用的旧接口/旧字段 |
| **[R-API-ENVEL]** | MUST | 跨服务错误响应统一结构化信封（`error_code`, `message`, `trace_id`, `details`） | 各接口自造错误格式；直接将底层数据库报错/原始堆栈暴露给外部 |

---

## 2. 模式契约与微代码示例

### 2.1 游标分页请求/响应信封 [R-API-BOUND / R-API-CURSR]
```cpp
// ✅ 标准游标分页契约（安全限额截断）
template <typename cursor_t>
struct page_request_t {
    std::optional<cursor_t> after_cursor;
    uint32_t limit{20};
    static constexpr uint32_t max_limit{100};
    [[nodiscard]] uint32_t safe_limit() const noexcept { return std::min(limit, max_limit); }
};

template <typename item_t, typename cursor_t>
struct page_response_t {
    std::vector<item_t> items;
    std::optional<cursor_t> next_cursor;
    bool has_more{false};
};
```

### 2.2 统一错误响应信封 [R-API-ENVEL]
```cpp
// ✅ 标准错误结构（隔离内部实现细节）
struct api_error_envelope_t {
    std::string error_code;
    std::string message;
    std::string trace_id;
    std::unordered_map<std::string, std::string> details;
};
```

---

## 3. 验收核验清单 (Checklist)
- [ ] 所有非只读写操作接口均接入幂等键机制或具备防重控制。
- [ ] 集合查询接口强制限定最大 `page_size`，无无界全量查询风险。
- [ ] 契约演进遵循只增不减原则，新增字段为可选或具备默认值。
- [ ] 错误返回结构统一，包含 `trace_id` 且不泄露敏感底层细节。
