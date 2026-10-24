# 条件系统

cmake.toml 的键可以按条件生效，编译期展开成 CMake `if()` 块。

## 条件键语法

大多数键可加 **条件前缀**：`<条件>.键名`。

```toml
[target.app]
sources = ["src/main.cpp"]
windows.sources = ["src/win_main.cpp"]
x64.definitions = ["IS_64BIT"]
custom.cmake-after = """
message(STATUS "Custom condition applied")
"""
```

同一字段可以出现多次，每次一个不同条件：

```toml
[target.app]
sources = ["src/main.cpp"]
windows.sources = ["src/win_main.cpp"]
linux.sources = ["src/linux_main.cpp"]
```

展开：

```cmake
add_executable(app src/main.cpp)
if(WIN32)
  target_sources(app PRIVATE src/win_main.cpp)
endif()
if(CMAKE_SYSTEM_NAME MATCHES "Linux")
  target_sources(app PRIVATE src/linux_main.cpp)
endif()
```

条件键可以加在 `[project]`、`[target]`、`[options]`、`[[test]]`、`[[install]]` 等的任何字段上。

## [conditions]：自定义条件

```toml
[conditions]
ptr64 = "CMAKE_SIZEOF_VOID_P EQUAL 8"
ptr32 = "CMAKE_SIZEOF_VOID_P EQUAL 4"
```

之后 `ptr64.sources = [...]` 就可用了。

### 条件命名规则

条件名只能包含**小写字母数字**（`[0-9a-z]`）和**短横线**（`-`）。如 `win32-executable`、`build-tests`。

## 内联 CMake 表达式

除了具名条件，还能直接写**带引号的 CMake 表达式**：

```toml
[target.app]
sources = ["src/main.cpp"]
"CMAKE_SYSTEM_NAME MATCHES \"Linux\"".definitions = ["ON_LINUX"]
```

表达式里用 `$<name>` 引用其他条件：

```toml
[conditions]
ptr64 = "CMAKE_SIZEOF_VOID_P EQUAL 8"

[target.app]
sources = ["src/main.cpp"]
"CONDITIONS_BUILD_TESTS AND $<linux>".definitions = ["WITH_TESTS"]
```

`$<linux>` 会被替换为 linux 条件的完整 CMake 表达式（`(CMAKE_SYSTEM_NAME MATCHES "Linux")`）。

## 预定义条件

以下条件内置（可在 `[conditions]` 里覆盖）：

| 条件 | CMake 表达式 |
|------|--------------|
| `windows` | `WIN32` |
| `macos` | `CMAKE_SYSTEM_NAME MATCHES "Darwin"` |
| `unix` | `UNIX` |
| `bsd` | `CMAKE_SYSTEM_NAME MATCHES "BSD"` |
| `linux` | `CMAKE_SYSTEM_NAME MATCHES "Linux"` |
| `gcc` | `CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "GNU"` |
| `msvc` | `MSVC` |
| `clang` | Clang 编译器（非 MSVC 前端） |
| `clang-cl` | Clang 的 MSVC 前端 |
| `clang-any` | 任意 Clang |
| `root` | `CMKR_ROOT_PROJECT`（顶层项目才为真） |
| `x64` | `CMAKE_SIZEOF_VOID_P EQUAL 8` |
| `x32` | `CMAKE_SIZEOF_VOID_P EQUAL 4` |
| `android` | `ANDROID` |
| `apple` | `APPLE` |
| `cygwin` | `CYGWIN` |
| `ios` | `IOS` |
| `xcode` | `XCODE` |
| `wince` | `WINCE` |

`clang` 完整表达式（含 MSVC 前端排除）：

```cmake
(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND NOT CMAKE_CXX_COMPILER_FRONTEND_VARIANT MATCHES "^MSVC$")
OR (CMAKE_C_COMPILER_ID MATCHES "Clang" AND NOT CMAKE_C_COMPILER_FRONTEND_VARIANT MATCHES "^MSVC$")
```

::: tip root 条件
`root` = `CMKR_ROOT_PROJECT`，顶层项目才为真。子项目被 `fetch-content` / `[subdir]` 引入时 `root` 为假——常用于「只有根项目才构建 examples/tests」。
:::

## options 自动生成条件

`[options]` 里的每个选项自动生成两个条件：原名（如 `MYPROJECT_BUILD_TESTS`）和基于项目名归一化的短横线形式（如 `build-tests`）。详见 [options](./options)。

## 条件与 target 整体

target 可整体条件化：

```toml
[target.example]
condition = "MYPROJECT_BUILD_EXAMPLES"
type = "executable"
sources = ["src/example.cpp"]
```

`condition` 为假时整个 `add_executable` 不生成。

条件还可以直接驱动**函数调用**——`条件名.function = [调用, ...]`,gen 自动生成 `if(条件)` + `if(COMMAND fn)` 双守卫:

```toml
[conditions]
pack-assets = "NOT ENABLE_DEV STREQUAL ON"

[target.Loader]
pack-assets.function = ["webview_package_assets(Loader \"${CMAKE_SOURCE_DIR}/Loader\")"]
```

详见 [target · function](./target#function-条件函数调用-configure-期)。

## 注意事项

- 条件键的键名**不能**与字段本身重复——`windows.windows` 无意义
- 条件表达式求值是纯文本展开，**不是**在 cmkr 里求值；`$<name>` 只做字符串替换
- 预定义条件可被 `[conditions]` 覆盖，但覆盖会影响**所有**用到该名字的位置

## 下一步

- [options](./options)：选项如何变成条件
- [target](./target)：条件键在 target 中的应用
