# [project]

单例配置表，描述项目本身。生成后的 CMake 配置（版本、utf-8）见 [cmake](./cmake)。

```toml
[project]
name = "myproject"
version = "1.0.0"
description = "Description of the project"
languages = ["C", "CXX"]
msvc-runtime = "" # dynamic (implicit default), static
cmake-before = """
message(STATUS "CMake injected before the project() call")
"""
cmake-after = """
message(STATUS "CMake injected after the project() call")
"""
include-before = ["cmake/before-project.cmake"]
include-after = ["cmake/after-project.cmake"]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 项目名，对应 `project()` |
| `version` | string | 版本号 |
| `description` | string | 描述 |
| `languages` | array | 启用的语言，见下表 |
| `msvc-runtime` | string | `dynamic`（默认）或 `static`，见 [target](./target) |
| `cmake-before` | string（多行） | 在 `project()` **前**注入原生 CMake |
| `cmake-after` | string（多行） | 在 `project()` **后**注入原生 CMake |
| `include-before` | array | 在 `project()` 前 `include()` 的 .cmake 文件 |
| `include-after` | array | 在 `project()` 后 `include()` 的 .cmake 文件 |

### languages

支持语言（对应 [`enable_language`](https://cmake.org/cmake/help/latest/command/enable_language.html)）：

`C`、`CXX`（C++）、`CSharp`、`CUDA`、`OBJC`、`OBJCXX`、`Fortran`、`HIP`、`ISPC`、`Swift`、`ASM`、`ASM_MASM`、`ASM_NASM`、`ASM_MARMASM`、`ASM-ATT`、`Java`（未文档化）、`RC`（未文档化）

启用语言后，给 target 加对应扩展名源文件会自动使用对应编译器/汇编器。

::: warning 别禁用 C
除非确定不用，否则**不要禁用 `C` 语言**。有时 `fetch-content` 加进来的项目隐式依赖它，报错信息会非常难懂。
:::

### cmake-before / cmake-after

最重要的逃生舱：任何原生 CMake 都能塞进多行字符串。常用于全局配置：

```toml
[project]
cmake-after = """
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
"""
```

## 实例

```toml
[project]
name = "myapp"
version = "2.1.0"
description = "Cross-platform demo"
languages = ["C", "CXX"]
cmake-after = """
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
"""
```

生成物要点：`project(myapp VERSION 2.1.0 ...)`、project() 后注入的 `set(...)`。CMake 版本与 utf-8 配置放 `[cmake]` 表（见 [cmake](./cmake)）。

::: danger [project] 是单例表
`[project]`、`[cmake]` 只能写**一个**。重复声明同名表是 TOML 语法错误，所有项目级键放同一张表。
:::

## 下一步

- [cmake](./cmake)：CMake 版本 / utf-8 配置
- [target](./target)：真正构建单元
- [条件系统](./conditions)：`windows.cmake-after` 这类条件键
