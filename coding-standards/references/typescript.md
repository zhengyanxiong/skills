# TypeScript / React 规范

## 工具（格式与语义分离）

- **Formatter：Biome**（`biome format`）—— 自动处理缩进/换行/引号/分号，**你不需要关心格式**。
- **Linter：Biome recommended preset**（`biome lint`）—— 语义检查，`error` 会拦你，`warning` 提示你。

## 语义要点（少量，真正要记住的）

这些是 Biome recommended 规则集背后最重要的语义约定，生成代码时主动遵守，减少被 lint 拦截：

- **禁 `any`**（`noExplicitAny`）：不确定时用 `unknown` + 类型收窄。
- **不吞异常**（`noEmptyBlockStatements`）：空 `catch {}` 是禁止的，要么处理要么重抛。
- **依赖数组完整**（React `useExhaustiveDependencies`）：`useEffect`/`useMemo`/`useCallback` 依赖不遗漏。
- **连续值不用 `useState` 驱动**（React 性能）：滚动位置、鼠标坐标、动画值用 `useRef` 或 motion value，避免每帧重渲染。
- **显式返回类型**：对外 API（导出函数、组件 props）标注参数和返回类型。

## 规则集映射

你写的代码会被 Biome recommended preset 检查，规则分四类：

- `correctness`：`noUnusedVariables`、`noUnusedImports`、`useExhaustiveDependencies`（默认 error）
- `suspicious`：`noExplicitAny`、`noDoubleEquals`、`noEmptyBlockStatements`
- `style`：`useConst`、`useImportType`、`useSingleVarDeclarator`
- `complexity`：`noBannedTypes`、`noUselessFragments`

格式（缩进/换行/引号/分号）由 Biome formatter 自动处理，你不用管。真正的规则以 Biome 配置为准，本文是语义要点的精简提醒。
