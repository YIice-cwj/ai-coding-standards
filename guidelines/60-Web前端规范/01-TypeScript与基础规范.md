# 前端 · TypeScript 与现代基础规范

**所属域**: 60-Web前端规范  **域版本**: 1.0.0  **日期**: 2026-10-26  **类型**: Web 与全栈前端基准

> **SSOT 依赖**：[00-行为规范](../00-行为规范/01-核心铁律与五阶执行模型.md) · [通用规范](../10-通用代码规范/01-风格命名与注释.md)。

---

## 1. TypeScript 强类型与语法红线

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-TS-NO-ANY]** | MUST | 开启 `strict: true`；严禁使用 `any`；不确定类型用 `unknown` 并配合类型守卫 (Type Guard) 收缩 | 滥用 `as any` 逃避类型检查；隐式 `any` |
| **[R-TS-TYPE-DEF]**| MUST | 面向对象/公共契约优先 `interface`；联合类型/映射类型用 `type` | 混用隐晦命名；为类型添加过时 `I` 前缀（如 `IUser`） |
| **[R-TS-ENUM]**    | MUST | 优先使用 `const enum` 或联合字面量（`type Status = 'IDLE' | 'BUSY'`） | 裸 `enum` 产生额外运行时 IIFE 膨胀 |
| **[R-TS-ASYNC]**   | MUST | 所有 Promise 必须 `await` 或链式 `.catch()`；并发加载用 `Promise.allSettled` | Floating Promise（悬挂未处理 Promise） |
| **[R-TS-OPT-CHAIN]**| MUST| 外部未知数据使用可选链 `obj?.field` 与空值合并 `??` | 强行使用非空断言 `obj!.field`（除非前置逻辑已 100% 窄化） |

---

## 2. 模式对比与正反例 (❌ vs ✅)

### 2.1 严禁 any 与未知类型收缩 [R-TS-NO-ANY]
```typescript
// ❌ 反例：滥用 any 击穿类型安全
function parseUser(data: any): string {
    return data.profile.name; // 运行时极易因 undefined 崩溃
}

// ✅ 正例：使用 unknown + 类型窄化守卫
interface UserProfile { name: string; }
function isUserProfile(val: unknown): val is UserProfile {
    return typeof val === 'object' && val !== null && 'name' in val;
}
function parseUser(data: unknown): string {
    if (isUserProfile(data)) { return data.name; }
    throw new TypeError('Invalid user payload');
}
```

### 2.2 杜绝非空断言与安全取值 [R-TS-OPT-CHAIN]
```typescript
// ❌ 反例：无脑非空断言（崩溃高发点）
const userName = response.data!.user!.name!;

// ✅ 正例：可选链与空值合并
const userName = response?.data?.user?.name ?? 'Anonymous';
```

---

## 3. 自检清单 (Checklist)
- [ ] `tsconfig.json` 开启严格模式，源码零 `any`、零隐式类型丢失。
- [ ] 异步 Promise 100% 处理异常与完成状态，无 Floating Promise。
- [ ] 杜绝未经保护的 `!` 非空断言，外部输入使用类型守卫验证。

