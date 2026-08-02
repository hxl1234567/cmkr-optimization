# [options]

声明 CMake 缓存选项。每个选项**自动生成两个条件**，可直接用在条件键里。

```toml
[options]
MYPROJECT_BUILD_TESTS = false
MYPROJECT_SPECIAL_OPTION = { value = true, help = "Docstring for this option." }
MYPROJECT_BUILD_EXAMPLES = "root"
```

## 三种写法

| 写法 | 含义 |
|------|------|
| `NAME = true` / `false` | 简单布尔选项 |
| `NAME = { value = true, help = "..." }` | 带 help 文本 |
| `NAME = "root"` | 顶层项目才为 `true`；被 fetch-content / subdir 引入时 `false` |

对应 CMake `option()` 缓存变量，configure 时用 `-DMYPROJECT_BUILD_TESTS=ON` 切换。

## 自动生成条件

每个选项生成两个条件：

1. **原名**：`MYPROJECT_BUILD_TESTS`
2. **归一化短横线**（基于 `[project].name`）：`MYPROJECT_BUILD_TESTS` → `build-tests`

```toml
[project]
name = "myproject"

[options]
MYPROJECT_BUILD_TESTS = false

[target.tests]
condition = "build-tests"               # 归一化条件
type = "executable"
sources = ["tests/main.cpp"]
```

## 实例：条件启用

```toml
[project]
name = "myproject"

[options]
MYPROJECT_BUILD_EXAMPLES = "root"       # 根项目默认开，被 fetch 时关

[target.ex_demo]
condition = "build-examples"
type = "executable"
sources = ["examples/demo.cpp"]
```

`cmake -DMYPROJECT_BUILD_EXAMPLES=OFF` 可手动关；作为依赖被引入时自动关。

## 注意事项

- 选项名惯例**全大写 + 下划线**；条件键里用归一化短横线更简洁
- `"root"` 特值只在条件里起作用，选项值本身不是布尔
- 选项名要与 `[variables]` 区分——options 生成缓存变量，variables 生成普通 `set()`

## 下一步

- [conditions](./conditions)：条件怎么用选项
- [variables](./variables)：普通变量
