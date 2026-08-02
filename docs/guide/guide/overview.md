# 语法总览

`cmake.toml` 是标准的 [TOML](https://toml.io) 文件。理解三种语法后即可上手：**顶层表**、**条件键**、**可见性前缀**。

## 文件结构

顶层只有两类表：**单例配置表**（`[project]`、`[cmake]` 等）和**具名表**（`[target.xxx]`、`[conditions]` 等）。

一个完整最小文件：

```toml
[project]
name = "myproject"
version = "1.0.0"

[cmake]
version = "3.15"

[target.app]
type = "executable"
sources = ["src/main.cpp"]
```

## 值类型

| 类型 | 写法 | 示例 |
|------|------|------|
| 字符串 | 双引号 | `name = "myproject"` |
| 布尔 | `true` / `false` | `shallow = false` |
| 数组 | 方括号 | `sources = ["a.cpp", "b.cpp"]` |
| 多行字符串 | 三引号 | `cmake-before = """..."""` |
| 表 | `[key]` | `[target.app]` |

**多行字符串**用于内嵌原生 CMake 代码：

```toml
[project]
cmake-after = """
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
"""
```

::: tip TOML 合法子集
所有键值都是合法 TOML。数组元素可跨行，字符串可含转义；**多行字符串** `"""` 里可以自由写 CMake 的 `"` 和换行，不必转义。
:::

## 条件键：`condition.key`

大多数键可加 **条件前缀**，编译期按条件展开成 `if()` 块：

```toml
[target.app]
sources = ["src/main.cpp"]
windows.sources = ["src/win_main.cpp"]      # 仅 Windows 额外编译
x64.definitions = ["IS_64BIT"]              # 仅 64 位定义宏
```

展开结果：

```cmake
add_executable(app src/main.cpp)
if(WIN32)
  target_sources(app PRIVATE src/win_main.cpp)
endif()
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  target_compile_definitions(app PRIVATE IS_64BIT)
endif()
```

`condition.` 可加在**任意**键前：`windows.compile-options`、`linux.link-libraries`、`root.cmake-after`……条件名来自预定义条件或自定义 `[conditions]`，也可以是带引号的 CMake 表达式。详见 [条件系统](./conditions)。

## 可见性前缀：`private-`

对应 `target_xxx` 命令的属性键默认可见性取决于 target 类型（见 [target](./target)）。需要**私有**时加 `private-` 前缀：

```toml
[target.lib]
type = "static"
include-directories = ["include"]          # PUBLIC：传播给消费者
private-compile-options = ["-Wall"]        # PRIVATE：仅自己
```

## 顶层表清单（按使用频率排序）

| 顶层表 | 用途 | 详见 |
|--------|------|------|
| `[project]` | 项目名 / 版本 / 语言 / CMake 注入 | [project](./project) |
| `[target.*]` | 构建目标（含 post-build / win32-executable） | [target](./target) |
| `[cmake]` | CMake 版本 / 引导脚本 / utf-8 | [cmake](./cmake) |
| `[conditions]` | 自定义条件 | [conditions](./conditions) |
| `[options]` | CMake 缓存选项 → 条件 | [options](./options) |
| `[variables]` | 发射 `set()` 的变量 | [variables](./variables) |
| `[fetch-content.*]` | 拉取外部依赖 | [fetch-content](./fetch-content) |
| `[vcpkg]` | vcpkg 包管理 | [vcpkg](./vcpkg) |
| `[find-package.*]` | `find_package()` | [find-package](./find-package) |
| `[subdir.*]` | 子目录 | [subdir](./subdir) |
| `[template.*]` | 自定义 target 类型 | [template](./template) |
| `[[target.*.custom-command]]` | `add_custom_command` / `add_custom_target` | [custom-command](./custom-command) |
| `[[test]]` | CTest 测试（未完成） | [test](./test) |
| `[[install]]` | 安装规则（未完成） | [install](./install) |

## 键 → CMake 构造映射

多数键名对应同名 CMake 命令（去掉短横线）：

| cmake.toml 键 | CMake 构造 |
|---------------|------------|
| `sources` | `target_sources` |
| `compile-definitions` | `target_compile_definitions` |
| `compile-options` | `target_compile_options` |
| `include-directories` | `target_include_directories` |
| `link-libraries` | `target_link_libraries` |
| `link-options` | `target_link_options` |
| `precompile-headers` | `target_precompile_headers` |
| `[target.x.properties]` | `set_target_properties` |

## 下一步

- [基础概念](./basics)：理解 project / target / property / 可见性
- [target](./target)：最常用表语法
- [条件系统](./conditions)：条件键完整规则
