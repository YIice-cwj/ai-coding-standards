# 前端 · TypeScript 与现代基础规范

**所属域**: 60-Web前端规范  **域版本**: 1.2.0  **日期**: 2026-11-09  **类型**: Web 与全栈前端基准

> **SSOT 依赖**：[00-行为规范](../00-行为规范/01-核心铁律与五阶执行模型.md) · [通用规范](../10-通用代码规范/01-风格命名与注释.md) · [前端工程化、测试与安全](./03-前端工程化测试与安全规范.md)。

---

## 1. TypeScript 强类型与语法红线

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-TS-NO-ANY]** | MUST | 严禁使用 `any`；不确定类型用 `unknown` 并配合类型守卫 (Type Guard) 收缩 | 滥用 `as any` 逃避类型检查；隐式 `any` |
| **[R-TS-TYPE-DEF]**| MUST | 面向对象/公共契约优先 `interface`；联合类型/映射类型用 `type` | 混用隐晦命名；为类型添加过时 `I` 前缀（如 `IUser`） |
| **[R-TS-ENUM]**    | MUST | 优先使用联合字面量（`type Status = 'IDLE' | 'BUSY'`）；确需运行时枚举使用普通 `enum` | 使用 `const enum`（与 `isolatedModules`、Babel、esbuild 等现代构建链冲突） |
| **[R-TS-ASYNC]**   | MUST | 所有 Promise 必须 `await` 或链式 `.catch()`；并发加载用 `Promise.allSettled` | Floating Promise（悬挂未处理 Promise） |
| **[R-TS-OPT-CHAIN]**| MUST| 外部未知数据使用可选链 `obj?.field` 与空值合并 `??` | 强行使用非空断言 `obj!.field`（除非前置逻辑已 100% 窄化） |
| **[R-TS-STRICT]**  | MUST | `strict: true`，并开启 `noUncheckedIndexedAccess`、`exactOptionalPropertyTypes`、`noImplicitOverride`、`noFallthroughCasesInSwitch` | 仅开 `strict` 却关闭关键子项；用 `// @ts-ignore` 掩盖类型错误 |
| **[R-TS-IMPORT]**  | MUST | 类型导入使用 `import type`；开启 `verbatimModuleSyntax`；禁止循环依赖 | 运行时导入仅用于类型的模块；用路径别名绕开模块边界 |
| **[R-TS-ERROR]**   | MUST | `catch` 变量视为 `unknown`，先窄化再使用；错误携带可行动上下文 | `catch (e: any)`；空 `catch {}` 吞异常；仅 `console.log` 不处理 |
| **[R-TS-SAFE-DOM]**| MUST | 不可信内容禁止进入 `eval`、`new Function`、未净化 `innerHTML` | 用 `eval` 执行外部输入；直接渲染未净化 HTML（详见 [03 前端安全](./03-前端工程化测试与安全规范.md)） |

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

### 2.3 严格编译配置 [R-TS-STRICT]
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true
  }
}
```

### 2.4 错误处理与 unknown 窄化 [R-TS-ERROR]
```typescript
// ❌ 反例：catch 变量隐式 any，错误被吞掉
try {
    await saveOrder(order);
} catch (error) {
    console.log(error);
}

// ✅ 正例：unknown + 类型窄化 + 可行动上下文
try {
    await saveOrder(order);
} catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'unknown error';
    throw new SaveOrderError(`save order failed: ${message}`, { cause: error });
}
```

### 2.5 空值默认与真值陷阱 [R-TS-OPT-CHAIN]
```typescript
// ❌ 反例：|| 把合法的 0 与空字符串当成缺失
const timeoutMs = config.timeoutMs || 30_000;

// ✅ 正例：?? 仅处理 null/undefined
const timeoutMs = config.timeoutMs ?? 30_000;
```

---

## 3. 自检清单 (Checklist)
- [ ] `tsconfig.json` 开启 `strict` 及关键子项，源码零 `any`、零隐式类型丢失。
- [ ] 类型导入使用 `import type`，无循环依赖，无 `@ts-ignore` 掩盖。
- [ ] 异步 Promise 100% 处理异常与完成状态，无 Floating Promise。
- [ ] `catch` 变量按 `unknown` 窄化，错误带可行动上下文，无空 `catch`。
- [ ] 杜绝未经保护的 `!` 非空断言；空值默认使用 `??`。
- [ ] 不可信内容不进入 `eval`、`new Function` 或未净化 `innerHTML`。

