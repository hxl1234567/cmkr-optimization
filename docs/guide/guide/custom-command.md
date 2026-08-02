# [[target.*.custom-command]]

`[[target.xxx.custom-command]]` 声明 `add_custom_command` / `add_custom_target`，支持两种形式：

1. **output 形式**：生成文件，自动加入 target 的 sources / 依赖
2. **target 形式**：构建时跑命令（pre-build / pre-link / post-build）

外加 `type = "custom"` 声明独立 custom target（`add_custom_target`）。

## output 形式：代码生成

```toml
[target.custom-command]
type = "executable"
sources = ["src/main.cpp"]
include-directories = ["${CMAKE_CURRENT_BINARY_DIR}/generated"]

# 生成的源文件自动作为 target 的 sources
[[target.custom-command.custom-command]]
outputs = ["generated/generated.cpp"]
byproducts = ["generated/generated.hpp"]
depends = ["cmake/generate_source.cmake"]
command = [
    "${CMAKE_COMMAND}",
    "-DOUTPUT_CPP=${CMAKE_CURRENT_BINARY_DIR}/generated/generated.cpp",
    "-DOUTPUT_HPP=${CMAKE_CURRENT_BINARY_DIR}/generated/generated.hpp",
    "-P",
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/generate_source.cmake",
]
comment = "Generate source files"
verbatim = true
```

::: tip 相对路径
`outputs` 等相对路径按 CMake 惯例，从**二进制目录**解释。生成文件自动加进 target sources，无需手动声明。
:::

## target 形式：构建事件

```toml
[target.hello]
type = "executable"
sources = ["src/hello.cpp"]

[[target.hello.custom-command]]
build-event = "post-build"              # pre-build / pre-link / post-build
command = ["${CMAKE_COMMAND}", "-E", "echo", "Built executable: $<TARGET_FILE_NAME:hello>"]
comment = "Print the built executable name"
```

`build-event` 只允许三种值：`pre-build`、`pre-link`、`post-build`。target 形式与 output 形式**二选一**——不写 `outputs` 必须写 `build-event`，反之亦然（parser 强制校验）。

## type = "custom"：独立 target

不依赖任何可执行/库，独立跑命令。`all = true` 让它在默认构建里执行：

```toml
[target.custom-codegen]
type = "custom"
all = true
command = ["${CMAKE_COMMAND}", "-E", "touch", "${CMAKE_CURRENT_BINARY_DIR}/stamp"]
byproducts = ["${CMAKE_CURRENT_BINARY_DIR}/stamp"]
comment = "Run custom target"
verbatim = true
```

```toml
[target.custom-codegen-disabled]
type = "custom"
all = false                      # 不默认构建，需显式目标
command = ["${CMAKE_COMMAND}", "-E", "false"]
```

target 级 `all` 可覆盖模板的 `all`。

## 字段速查

| 字段 | 形式 | 说明 |
|------|------|------|
| `command` / `commands` | 两者 | 命令及参数（数组，可二者并用） |
| `comment` | 两者 | 构建时显示的注释 |
| `outputs` | output | 生成的文件 |
| `byproducts` | output/custom | 附加产物（`BYPRODUCTS`） |
| `depends` | output | 依赖文件/目标（`DEPENDS`） |
| `implicit-depends` | output | 隐式依赖表 `{lang, source}`（`IMPLICIT_DEPENDS`） |
| `build-event` | target | `pre-build` / `pre-link` / `post-build` |
| `append` | output | 追加到已有同名命令（`APPEND`） |
| `main-dependency` | output | 主依赖（`MAIN_DEPENDENCY`） |
| `working-directory` | 两者 | 工作目录 |
| `depfile` | output | 依赖文件（`DEPFILE`） |
| `job-pool` | 两者 | 并行池（`JOB_POOL`） |
| `job-server-aware` | 两者 | job server 感知 |
| `uses-terminal` | 两者 | 使用终端 |
| `verbatim` | 两者 | 原样传递不 shell 展开（`VERBATIM`） |
| `condition` | 两者 | 条件前缀 |
| `all` | custom target | `true` 默认构建（`ALL`） |

## 实例：生成源文件 → custom target

```toml
[target.custom-codegen-template]
type = "custom"
command = [
    "${CMAKE_COMMAND}",
    "-DINPUT=${CMAKE_CURRENT_BINARY_DIR}/template-custom-target.stamp",
    "-P", "${CMAKE_CURRENT_SOURCE_DIR}/cmake/verify_file_exists.cmake",
]

# output 形式自动成为 custom target 的依赖
[[target.custom-codegen-template.custom-command]]
outputs = ["template-custom-target.stamp"]
command = ["${CMAKE_COMMAND}", "-E", "touch", "${CMAKE_CURRENT_BINARY_DIR}/template-custom-target.stamp"]
verbatim = true
```

## 注意事项

- `outputs` 与 `build-event` **必须恰好指定一个**，否则报错
- `build-event` 不能用于 `type = "interface"` / `"object"`；`pre-link` 不能用于 `type = "custom"`
- 简单构建后命令优先用 [`post-build`](./target) 字段；`custom-command` 用于需要 `comment`/`byproducts`/output 形式等精细控制时

## 下一步

- [target](./target)：字段总览 + post-build 简化写法
- [test](./test)：跑起来验证生成结果
