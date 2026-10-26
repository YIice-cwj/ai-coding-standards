# 前端 · React 与现代前端架构

**所属域**: 60-Web前端规范  **域版本**: 1.0.0  **日期**: 2026-10-26  **类型**: Web 与全栈前端基准

> **SSOT 依赖**：[00-行为规范](../00-行为规范/01-核心铁律与五阶执行模型.md) · [TypeScript规范](./01-TypeScript与基础规范.md)。

---

## 1. React 核心红线对照表

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-REACT-HOOK-DEP]**| MUST | `useEffect` / `useCallback` / `useMemo` 必须如实填写**全量依赖项**；严禁 ESLint 禁用注释 | 遗漏依赖产生闭包陷阱（Stale Closure）；死循环更新 |
| **[R-REACT-STATE-LOC]**| MUST| 状态尽量**下沉到叶子组件**；高频变动状态使用局部 State 或 Context 拆分 | 顶层组件存放大对象 State，导致无关子树全量 Re-render |
| **[R-REACT-CLIENT-BND]**| MUST| Next.js / 全栈框架中 `'use client'` 必须**下沉至最小交互叶子组件** | 页面或根布局顶部无脑标 `'use client'`，破坏 RSC 优势 |
| **[R-REACT-HYDRATE]**  | MUST| 浏览器专属 API（`window`, `localStorage`）必须在 `useEffect` 或挂载判定后访问 | 在组件渲染顶层直接调用 `window` 导致 SSR 水合崩溃 |
| **[R-REACT-CLEANUP]**  | MUST| 事件监听、定时器与 WebSocket 必须在 `useEffect` 返回清理函数 | 遗留未注销的回调导致严重内存泄露与脏状态更新 |

---

## 2. 模式对比与正反例 (❌ vs ✅)

### 2.1 Hooks 闭包陷阱防范 [R-REACT-HOOK-DEP]
```typescript
// ❌ 反例：隐瞒依赖项导致闭包陈旧值
useEffect(() => {
    const timer = setInterval(() => { console.log(count); }, 1000); // 始终打印初始 count
    return () => clearInterval(timer);
}, []); // 错！遗漏 count 依赖

// ✅ 正例：使用函数式更新或如实声明依赖
useEffect(() => {
    const timer = setInterval(() => {
        setCount(prev => prev + 1); // 零闭包陈旧风险
    }, 1000);
    return () => clearInterval(timer);
}, []);
```

### 2.2 SSR 水合安全 (Hydration Safety) [R-REACT-HYDRATE]
```typescript
// ❌ 反例：SSR 环境下执行浏览器特有 API 导致水合不匹配或报错
const theme = localStorage.getItem('theme') ?? 'dark';

// ✅ 正例：安全挂载后读取，或提供同构默认值
const [theme, setTheme] = useState('dark');
useEffect(() => {
    const saved = localStorage.getItem('theme');
    if (saved) setTheme(saved);
}, []);
```

---

## 3. 自检清单 (Checklist)
- [ ] 零 Hooks 依赖项省略；无 ESLint `react-hooks/exhaustive-deps` 忽略警告。
- [ ] `'use client'` 仅置于必要的用户交互组件，服务端组件保持纯净。
- [ ] 外部事件与定时器 100% 配备清理函数，零 SSR 水合崩溃隐患。

