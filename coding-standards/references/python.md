# Python 规范

## 工具（格式与语义分离）

- **Formatter：Ruff**（`ruff format`）—— 自动处理缩进/换行/引号，**你不需要关心格式**。
- **Linter：Ruff**（`ruff check`，规则集 E/F/UP/B/SIM/I）—— 语义检查，`error` 会拦你。

## 语义要点（少量，真正要记住的）

- **类型注解**：对外 API 用类型注解；Python 3.10+ 用 `X | Y`，不用 `Optional[X]`（`UP007`）。
- **不吞异常**（`E722`）：空 `except:` 是禁止的，要么处理要么重抛。
- **f-string 优先**（`UP032`）：用 f-string，不用 `%` 或 `.format()`。
- **可变默认参数禁止**（`B006`）：`def f(x=[])` 是 bug 源，用 `x=None` + 内部初始化。
- **import 排序**（`I`）：标准库、第三方、本地分三组，按 isort 规则。

## 规则集映射

你写的代码会被 Ruff 以下规则检查：

- `F`（Pyflakes）：未用导入/变量、未定义名、重复定义 —— 高频错误
- `B`（flake8-bugbear）：可变默认参数、可疑的 `hasattr` 检查、`assert False` 等
- `UP`（pyupgrade）：现代语法（f-string、`X | Y` 注解、`datetime.UTC`）
- `SIM`（flake8-simplify）：可简化的写法（`if x: return True` → `return x`）
- `I`（isort）：import 排序分组
- `E`（pycodestyle）：仅剩语义相关的（`E722` 裸 except），格式类已交 formatter

格式由 Ruff formatter 自动处理，你不用管。真正的规则以 `ruff.toml` 配置为准。
