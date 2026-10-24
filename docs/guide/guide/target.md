# [target]

`[target.xxx]` 是 cmake.toml 最常用的表，声明一个构建目标。

```toml
[target.mytarget]
type = "executable"
sources = ["src/main.cpp"]
```

## type

| 值 | 对应 CMake | 说明 |
|----|-----------|------|
| `executable` | `add_executable` | 可执行程序 |
| `library` | `add_library`（未指定类型） | 默认库 |
| `shared` | `add_library(... SHARED)` | 动态库（DLL / .so） |
| `static` | `add_library(... STATIC)` | 静态库 |
| `object` | `add_library(... OBJECT)` | 目标文件库 |
| `interface` | `add_library(... INTERFACE)` | 头文件库，无编译产物 |
| `custom` | — | 自定义，配合 `add-function` |

## 常用字段

```toml
[target.mytarget]
condition = "mycondition"        # 整个 target 按条件启用
alias = "mytarget::mytarget"     # 创建别名目标，用于命名空间/清晰
type = "static"
headers = ["src/mytarget.h"]     # 头文件（阅读性 + 未来打包用）
sources = ["src/mytarget.cpp"]
msvc-runtime = ""                # dynamic（默认）/ static

compile-definitions = [""]       # 宏定义 (-DFOO)
compile-features = [""]          # C++ 标准 (cxx_std_20)
compile-options = [""]           # 编译器参数
include-directories = [""]       # include 路径
link-directories = [""]          # 库目录
link-libraries = [""]            # 依赖
link-options = [""]              # 链接器参数
precompile-headers = [""]        # 预编译头

cmake-before = ""                # target 定义前注入 CMake（多行字符串）
cmake-after = ""                 # target 定义后注入 CMake
include-before = "cmake/x.cmake" # 同前，但 include 文件
include-after = "cmake/y.cmake"

[target.mytarget.properties]     # 直接设 target 属性
CXX_STANDARD = 17
CXX_STANDARD_REQUIRED = true
FOLDER = "MyFolder"
```

## 可见性：`private-` 前缀

除 `properties` 外，所有 `target_xxx` 类字段都支持 `private-` 前缀，控制属性传播：

```toml
[target.lib]
type = "static"
include-directories = ["include"]         # PUBLIC
private-include-directories = ["src"]     # PRIVATE：仅自己编译需要
private-compile-options = ["-Wall"]
```

默认可见性（未加前缀时）取决于 type：

| 类型 | 默认可见性 |
|------|-----------|
| `executable` | `PRIVATE` |
| `library` / `shared` / `static` / `object` | `PUBLIC` |
| `interface` | `INTERFACE` |

::: tip 为什么 interface 特殊
`interface` 目标没有编译产物，所有属性都只能有 interface 可见性，所以 `INTERFACE` 是唯一合理默认。`headers`、`include-directories` 等对纯头文件库很常见。
:::

## 字段 → CMake 命令映射

| 字段 | CMake | 说明 |
|------|-------|------|
| `alias` | [Alias Libraries](https://cmake.org/cmake/help/latest/command/add_library.html#alias-libraries) | 别名目标 |
| `sources` | `target_sources` | 源文件（interface 之外 PRIVATE） |
| `headers` | `target_sources` | 头文件，仅阅读性 |
| `msvc-runtime` | `MSVC_RUNTIME_LIBRARY` | 自动设 `CMP0091` 策略 |
| `compile-definitions` | `target_compile_definitions` | `-DMYMACRO=XXX` |
| `compile-features` | `target_compile_features` | C++ 标准 `cxx_std_20` |
| `compile-options` | `target_compile_options` | 编译器参数 |
| `include-directories` | `target_include_directories` | include 路径 |
| `link-directories` | `target_link_directories` | 库目录 |
| `link-libraries` | `target_link_libraries` | 依赖，用 `::mylib` 确保 target 存在 |
| `link-options` | `target_link_options` | 链接器参数 |
| `precompile-headers` | `target_precompile_headers` | 预编译头 |
| `properties` | `set_target_properties` | 见 [CMake 属性文档](https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html#properties-on-targets) |
| `post-build` | `add_custom_command(POST_BUILD)` | 构建后命令，见下方 |
| `win32-executable` | `WIN32_EXECUTABLE` + 链接选项 | Windows GUI 子系统，见下方 |
| `entry-point` | `target_link_options /ENTRY:` | MSVC 入口点，见下方 |

## sources：路径展开规则

`sources`（及 `headers`）支持多种写法，cmkr 在 `gen` 阶段把路径展开成具体文件：

```toml
[target.mytarget]
type = "executable"
sources = [
    "src/main.cpp",      # 1. 具体文件
    "src",               # 2. 裸目录 → 递归扫描
    "src/*",             # 3. 单层通配
    "src/**.cpp",        # 4. 递归通配 + 扩展名过滤
    "../other/lib.cpp",  # 5. 外部路径(项目目录之外)
]
```

| 写法 | 行为 |
|------|------|
| 具体文件 | 原样输出 |
| **裸目录** | 递归扫描该目录，按已知源/头文件扩展名过滤 |
| `dir/*` | 单层展开，所有文件（不限扩展名） |
| `dir/**` | 递归展开，所有文件（不限扩展名） |
| `dir/**.cpp` | 递归展开，仅 `.cpp` |
| 外部路径 | 输出为**绝对路径**（不再报 path traversal 错误） |

### 裸目录扫描的扩展名

裸目录递归扫描时，只保留已知源文件 / 头文件扩展名，过滤 `.md`/`.txt`/`.json` 等非源文件：

- **源文件**：`.c .cc .cpp .cxx .c++ .C .m .mm .rc .cu .hip .ispc .cs .java .swift .s .S .asm .nasm` 及 Fortran (`.f .f90 .for ...`)
- **头文件**：`.h .hpp .hh .hxx .h++ .inl .ipp .txx`

::: tip .rc 资源脚本
Windows 资源脚本(`.rc`)是合法的 sources;`RC` 语言对本仓项目**始终自动启用**,`sources = ["version.rc"]` 无需额外配置。跨平台项目请用 `windows.sources = [...]` 条件前缀。
:::

::: tip 裸目录 vs `dir/**`
- `sources = ["src"]` → 只收源/头文件，自动忽略非源文件
- `sources = ["src/**"]` → 收该目录下**所有**文件（含非源文件），不做扩展名过滤
:::

::: warning 外部路径
外部路径（`cmake.toml` 所在目录之外）会输出为绝对路径，便于引用共享代码。但绝对路径会绑定本机位置，**跨机器/CI 不可移植**，慎用。
:::

## include-directories：`dir/**` 递归子目录

`include-directories` 支持 `dir/**` 后缀，展开为 `dir` + 其下**所有递归子目录**，每个作为一条 `-I`：

```toml
[target.mytarget]
include-directories = ["include/**"]   # include/ + include/a/ + include/a/b/ ...
```

生成：

```cmake
target_include_directories(mytarget PUBLIC include include/a include/a/b)
```

::: tip 为何不默认递归
默认 `include-directories = ["include"]` 只加该目录本身，**不递归**——避免改变头文件搜索顺序。需要递归时显式写 `/**` opt-in。
:::

::: danger 仅 include-directories
`dir/**` 展开只对 `include-directories` / `private-include-directories` 生效。`sources` 用的是上表的 `dir/**` 通配（展开成文件，不是子目录）。
:::

## 条件键与 target

target 内所有字段都可加 `condition.` 前缀：

```toml
[target.app]
type = "executable"
sources = ["src/main.cpp"]
windows.sources = ["src/win.cpp"]
linux.compile-options = ["-pthread"]
root.cmake-after = """
message(STATUS "Only when root project")
"""
```

target 自身也可整体条件化（`condition` 字段）。详见 [条件系统](./conditions)。

## post-build：构建后命令（人性化字段）

`POST_BUILD` 钩子，**必须用数组**，每个元素一条命令：

```toml
[target.DbgDriver]
type = "executable"
sources = ["src/main.cpp"]
post-build = [
    "scripts/build.bat",                                    # .bat/.cmd → 自动加 cmd /c 前缀
    "cmd /c ${CMAKE_CURRENT_BINARY_DIR}/../../build/a.bat", # 命令，原样传递
    "${CMAKE_COMMAND} -E copy_if_different a.dll b.dll $<TARGET_FILE_DIR:x>",  # 命令
]
```

规则：

| 元素 | 处理 |
|------|------|
| 以 `.bat` / `.cmd` 结尾（大小写不敏感） | 生成 `cmd /c <元素>` |
| 其他字符串 | 原样作为 `COMMAND` 传给 `add_custom_command` |

```cmake
add_custom_command(TARGET x POST_BUILD COMMAND cmd /c scripts/build.bat)
add_custom_command(TARGET x POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different a.dll b.dll $<TARGET_FILE_DIR:x>)
```

::: danger 必须用数组
`post-build` 写字符串会**报错**（提示用数组，每条一个 bat 或命令）。
:::

支持条件前缀：`windows.post-build = [...]`。

## exclude-sources：从最终源列表剔除

glob/目录展开后,把匹配项从源列表删除(支持条件前缀,与 `exclude-sources` 同名机制):

```toml
[target.mydriver]
type = "driver"
sources = ["src"]
exclude-sources = ["src/memLoadDriver.cpp"]   # 目录 glob 收进来, 再剔除冲突文件
windows.exclude-sources = ["src/posix_*.cpp"]
```

剔除是**精确路径匹配**(展开后的相对/绝对路径逐字比对),发生在 glob 展开之后。

## module-sources：C++20 模块接口

`.ixx` / `.cppm` 模块接口单元,生成 `target_sources(<t> PRIVATE FILE_SET CXX_MODULES FILES ...)`:

```toml
[cmake]
version = "3.25"          # FILE_SET CXX_MODULES 要求 CMake >= 3.25

[target.webview]
type = "static"
module-sources = ["include/webview/app.ixx", "include/webview/*.ixx"]   # 支持通配
```

- `.ixx` / `.cppm` 声明在 `module-sources` 后会**自动从普通 sources 剔除**(目录 glob 双收录防护)
- 编译器需 C++20+(`compile-features = ["cxx_std_20"]` 起)
- `type = "custom"` 的 target 不支持,gen 直接报错

## function：条件函数调用（configure 期）

`条件名.function = [调用, ...]` — configure 期执行函数,gen 自动生成**双层守卫**:

```toml
[conditions]
pack-assets = "NOT ENABLE_DEV STREQUAL ON"

[target.Loader]
pack-assets.function = ["webview_package_assets(Loader \"${CMAKE_SOURCE_DIR}/Loader\")"]
```

生成:

```cmake
if(NOT ENABLE_DEV STREQUAL ON)      # 你的条件
	if(COMMAND webview_package_assets)   # 自动存在性守卫
		webview_package_assets(Loader "${CMAKE_SOURCE_DIR}/Loader")
	endif()
endif()
```

| 语义 | 说明 |
|------|------|
| 条件包裹 | 复用 [conditions] 定义,支持 AND/OR/NOT 组合 |
| `if(COMMAND fn)` 守卫 | 函数不存在时**静默跳过**(典型场景:fetch 的依赖仅在特定开关下定义该函数) |
| 条目格式 | 必须是完整调用表达式 `fn(args)`,缺 `(` 直接报错 |

不同条件 = 不同条目,平铺即"条件调用数组"。需要 else 分支的复杂逻辑仍用 `cmake-after`。

## win32-executable：GUI 子系统（人性化字段）

Windows 下无控制台窗口。**仅对 `type = "executable"` 生效**，其他类型静默忽略。

```toml
[target.DbgWebview]
type = "executable"
win32-executable = true
entry-point = "wWinMainCRTStartup"   # 可选;缺省 "wWinMainCRTStartup"
```

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `win32-executable` | bool | `false` | GUI 子系统 |
| `entry-point` | string | `"wWinMainCRTStartup"` | MSVC 入口点（`wWinMain` 用） |

```cmake
set_target_properties(x PROPERTIES WIN32_EXECUTABLE ON)
if(MSVC)
  target_link_options(x PRIVATE "/SUBSYSTEM:WINDOWS /ENTRY:wWinMainCRTStartup")
endif()
```

::: tip 非 MSVC
非 MSVC 只设 `WIN32_EXECUTABLE`，不设 `/ENTRY`。
:::

## 实例：库 + 可执行

```toml
[project]
name = "DataProcessor"

[target.StringUtils]
type = "static"
sources = ["StringUtils/src/stringutils.cpp"]
headers = ["StringUtils/include/stringutils.hpp"]
include-directories = ["StringUtils/include"]   # public：消费者要 include

[target.DataProcessor]
type = "executable"
sources = ["DataProcessor/src/main.cpp"]
link-libraries = ["StringUtils"]
```

## 下一步

- [基础概念](./basics)：可见性 private/interface/public 详解
- [条件系统](./conditions)：`windows.sources` 这类条件键
- [custom-command](./custom-command)：更精细的构建钩子（pre-build / output 形式）
- [project](./project)：项目级配置
