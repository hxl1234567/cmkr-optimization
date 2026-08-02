# 综合实例

完整 `cmake.toml` 示例，均取自仓库 [tests](https://gitee.com/cmkr_lib/cmkr/tree/main/tests) 的 fixture。

## 跨平台编译选项

按编译器设置不同 flag / 宏：

```toml
[project]
name = "compile-options"
description = "Compiler flags"

[target.hello]
type = "executable"
sources = ["src/main.cpp"]
msvc.compile-options = ["/W2"]
msvc.compile-definitions = ["PLATFORM=\"msvc\""]
gcc.compile-options = ["-Wall"]
gcc.compile-definitions = ["PLATFORM=\"gcc\""]
clang.compile-options = ["-Wall"]
clang.compile-definitions = ["PLATFORM=\"clang\""]
```

::: tip 原则
只指定**编译必需**的 flag，别堆警告等级。多写警告一般不值得维护。
:::

## 头文件库（interface）

无编译产物的纯头文件库，属性和依赖自动 interface 传播：

```toml
[project]
name = "interface"
description = "Header-only library"

[target.mylib]
type = "interface"
include-directories = ["include"]
compile-features = ["cxx_std_11"]

[target.example]
type = "executable"
sources = ["src/main.cpp"]
link-libraries = ["mylib"]
```

`example` 链接 `mylib` 后自动获得 `include` 目录和 C++11 要求。

## Glob 源文件

cmkr 运行期展开 glob，**不是**生成 `file(GLOB ...)`：

```toml
[project]
name = "globbing"
description = "Globbing sources"

# 递归 glob mylib/ 下全部 .hpp/.cpp
[target.mylib]
type = "static"
alias = "mylib::mylib"
sources = ["mylib/**.hpp", "mylib/**.cpp"]
include-directories = ["mylib/include"]

# 单层 glob example/src/
[target.example]
type = "executable"
sources = ["example/src/*.cpp"]
link-libraries = ["mylib::mylib"]
```

| 模式 | 含义 |
|------|------|
| `*.cpp` | 单层 glob（不递归） |
| `**.cpp` | 递归 glob |
| `"src"` | 裸目录：递归扫描，按源/头扩展名过滤 |

裸目录写法省去逐个列通配：

```toml
[target.mylib]
type = "static"
sources = ["src", "include"]          # 递归扫描，自动收 .cpp/.h/.hpp...，忽略 .md/.txt
include-directories = ["include/**"]  # include/ + 所有子目录作 -I
```

结果按文件名排序，跨平台确定性一致。

::: warning 重新生成时机
glob 在**跑 cmkr 时**展开。新增源文件后，若没有自动触发生成，手动跑一次 `cmkr gen` 或重新 configure。
:::

## 指定 C++ 标准

```toml
[project]
name = "cxx-standard"
description = "Changing C++ standard"

[target.example]
type = "executable"
sources = ["src/main.cpp"]
compile-features = ["cxx_std_11"]
```

等价 `target_compile_features(example PRIVATE cxx_std_11)`。可用的标准特性见 [cmake-compile-features(7)](https://cmake.org/cmake/help/latest/manual/cmake-compile-features.7.html)。

## 自定义 target 类型（template）

多个 target 共享同一套属性：

```toml
[project]
name = "templates"
description = "Target templates"

[template.app]
type = "executable"
sources = ["src/templates.cpp"]
compile-definitions = ["IS_APP"]

# template 也能带 properties（interface 之外可继承）
[template.app.properties]
CXX_STANDARD = "11"
CXX_STANDARD_REQUIRED = true

[target.app-a]
type = "app"
compile-definitions = ["APP_A"]

[target.app-b]
type = "app"
compile-definitions = ["APP_B"]
```

::: tip 何时不用 template
多数场景用 [interface](./basics) target 更简单——但 interface 没有编译产物，不能继承 `sources` 这类 property。详见 [template](./template)。
:::

## 条件大集合

自定义条件 + 内联 CMake 表达式 + 属性条件：

```toml
[project]
name = "conditions"
cmake-after = "set(CUSTOM ON)"

[options]
CONDITIONS_BUILD_TESTS = "root"

[conditions]
custom = "CUSTOM"

[target.example]
type = "executable"
sources = ["src/main.cpp"]
windows.sources = ["src/windows_specific.cpp"]
cmake-after = "message(STATUS cmake-after)"
windows.cmake-after = "message(STATUS win32-after)"
linux.cmake-after = "message(STATUS linux-after)"
custom.cmake-after = "message(STATUS custom-after)"
build-tests.cmake-after = "message(STATUS build-tests)"
"CONDITIONS_BUILD_TESTS AND $<linux>".cmake-after = "message(STATUS linux-tests)"

[target.example.properties]
AUTOMOC = false
custom.OUTPUT_NAME = "example2"   # 属性也能条件化
custom.AUTORCC = true
```

## Windows GUI + 构建后拷贝

人性化字段组合，真实项目（DbgWebview 类）用法：

```toml
[project]
name = "dbg_webview"

[cmake]
utf-8 = true

[target.DbgWebview]
type = "executable"
sources = ["src/main.cpp"]
win32-executable = true
post-build = [
    "scripts/pack_resources.bat",
    "${CMAKE_COMMAND} -E copy_if_different ${CMAKE_BINARY_DIR}/x.dll $<TARGET_FILE_DIR:DbgWebview>",
]
```

## 自定义命令（custom-command）

`[[target.x.custom-command]]` 支持两种形式：

```toml
[target.hello]
type = "executable"
sources = ["src/hello.cpp"]

# target 形式：构建后跑命令。build-event 可选 pre-build / pre-link / post-build
[[target.hello.custom-command]]
build-event = "post-build"
command = ["${CMAKE_COMMAND}", "-E", "echo", "Built executable: $<TARGET_FILE_NAME:hello>"]
comment = "Print the built executable name"

# output 形式：生成文件，自动加入 target sources
[[target.hello.custom-command]]
outputs = ["generated/generated.cpp"]
byproducts = ["generated/generated.hpp"]
```

::: tip 优先用 post-build 字段
简单的构建后命令用 [`post-build`](./target) 字段更简洁；`[[target.x.custom-command]]` 用于需要 `comment`、`byproducts` 或 output 形式等精细控制时。
:::

## 下一步

- [注意事项](./notes)：从实例里踩出的坑
- 更多示例：仓库 [tests](https://gitee.com/cmkr_lib/cmkr/tree/main/tests) 每个 fixture 都是完整可用工程
