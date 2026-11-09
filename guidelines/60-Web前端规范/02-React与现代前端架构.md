# 前端 · React 与现代前端架构

**所属域**: 60-Web前端规范  **域版本**: 1.2.0  **日期**: 2026-11-09  **类型**: Web 与全栈前端基准

> **SSOT 依赖**：[00-行为规范](../00-行为规范/01-核心铁律与五阶执行模型.md) · [TypeScript规范](./01-TypeScript与基础规范.md) · [前端工程化、测试与安全](./03-前端工程化测试与安全规范.md)。

---

## 1. React 核心红线对照表

| 规则标识 | 约束级别 | 强制行为 (DO) | 严禁行为 (DON'T / 一票打回) |
|---|:---:|---|---|
| **[R-REACT-HOOK-DEP]**| MUST | `useEffect` / `useCallback` / `useMemo` 必须如实填写**全量依赖项**；严禁 ESLint 禁用注释 | 遗漏依赖产生闭包陷阱（Stale Closure）；死循环更新 |
| **[R-REACT-STATE-LOC]**| MUST| 状态尽量**下沉到叶子组件**；高频变动状态使用局部 State 或 Context 拆分 | 顶层组件存放大对象 State，导致无关子树全量 Re-render |
| **[R-REACT-CLIENT-BND]**| MUST| Next.js / 全栈框架中 `'use client'` 必须**下沉至最小交互叶子组件** | 页面或根布局顶部无脑标 `'use client'`，破坏 RSC 优势 |
| **[R-REACT-HYDRATE]**  | MUST| 浏览器专属 API（`window`, `localStorage`）必须在 `useEffect` 或挂载判定后访问 | 在组件渲染顶层直接调用 `window` 导致 SSR 水合崩溃 |
| **[R-REACT-CLEANUP]**  | MUST| 事件监听、定时器与 WebSocket 必须在 `useEffect` 返回清理函数 | 遗留未注销的回调导致严重内存泄露与脏状态更新 |
| **[R-REACT-EFFECT]**   | MUST | `useEffect` 仅用于同步外部系统（网络、订阅、DOM、存储）；派生状态用渲染期计算或事件处理 | 用 `useEffect` 计算派生状态、同步 props 到 state、驱动业务状态机 |
| **[R-REACT-KEY]**      | MUST | 列表使用业务稳定 ID 作为 `key` | 使用数组索引作为动态列表 `key`，导致重排后状态错位 |
| **[R-REACT-DATA]**     | MUST | 数据获取具备取消、错误处理与竞态保护；服务端状态与本地 UI 状态分离 | 无 `AbortController` 的竞态请求；失败静默；把缓存数据当本地状态 |
| **[R-REACT-ERROR]**    | MUST | 关键 UI 区域使用错误边界；异步错误必须上报并给用户可行动提示 | 空 `catch` 吞错；仅 `console.log`；整页无错误兜底 |
| **[R-REACT-A11Y]**     | MUST | 语义化 HTML、可访问名称、键盘可达、焦点管理、可见焦点与足够对比度 | `div` 充当按钮；无 label；键盘不可操作；移除焦点轮廓 |
| **[R-REACT-PERF]**     | MUST | 先测量再优化；对确认热点使用 memo、虚拟化与代码分割 | 未测量就全量 `useMemo/useCallback`；首屏加载全量巨型 Bundle |

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

### 2.3 数据获取与竞态取消 [R-REACT-DATA]
```tsx
// ❌ 反例：无取消、无错误处理，旧请求覆盖新结果
useEffect(() => {
    fetch(`/api/orders/${orderId}`)
        .then(response => response.json())
        .then(setOrder);
}, [orderId]);

// ✅ 正例：AbortController + 错误处理 + 清理
useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    fetch(`/api/orders/${orderId}`, { signal: controller.signal })
        .then(response => {
            if (!response.ok) throw new HttpError(response.status);
            return response.json();
        })
        .then(order => {
            setOrder(order);
            setStatus('ready');
        })
        .catch(error => {
            if (error.name !== 'AbortError') setStatus('error');
        });
    return () => controller.abort();
}, [orderId]);
```

### 2.4 稳定 key 与列表渲染 [R-REACT-KEY]
```tsx
// ❌ 反例：数组索引 key，重排或过滤后状态错位
items.map((item, index) => <Row key={index} item={item} />);

// ✅ 正例：业务稳定 ID
items.map(item => <Row key={item.id} item={item} />);
```

### 2.5 可访问性基线 [R-REACT-A11Y]
```tsx
// ❌ 反例：div 当按钮，无键盘与语义
<div onClick={saveOrder}>保存</div>;

// ✅ 正例：语义化 button + 可访问名称 + 状态
<button type="button" onClick={saveOrder} aria-busy={saving}>
    保存
</button>;
```

### 2.6 错误边界与错误上报 [R-REACT-ERROR]
```tsx
// ✅ 正例：关键区域包裹错误边界，错误上报并给用户兜底
<ErrorBoundary fallback={<ErrorPanel />} onError={reportError}>
    <CheckoutPanel />
</ErrorBoundary>;
```

---

## 3. 自检清单 (Checklist)
- [ ] 零 Hooks 依赖项省略；无 ESLint `react-hooks/exhaustive-deps` 忽略警告。
- [ ] `'use client'` 仅置于必要的用户交互组件，服务端组件保持纯净。
- [ ] 外部事件与定时器 100% 配备清理函数，零 SSR 水合崩溃隐患。
- [ ] `useEffect` 仅用于外部系统同步，派生状态不在 Effect 中计算。
- [ ] 动态列表使用业务稳定 `key`，无索引 key。
- [ ] 数据请求具备取消、错误处理与竞态保护。
- [ ] 关键区域具备错误边界，异步错误已上报且有用户提示。
- [ ] 交互组件满足语义化、键盘可达、焦点可见与可访问名称。
- [ ] 性能优化基于测量证据，无未测量的全量 memo 化。

