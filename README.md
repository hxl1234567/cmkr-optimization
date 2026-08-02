# cmkr

> 本仓库是 [build-cpp/cmkr](https://github.com/build-cpp/cmkr) 的 Fork · 中文文档：<https://c.vt01.com> · 源码：<https://gitee.com/cmkr_lib/cmkr>

`cmkr`（读作 "cmaker"）是一个基于 [CMake](https://cmake.org/) 与 [TOML](https://toml.io/) 的现代化构建系统。

`cmkr` 解析 `cmake.toml`，自动为你生成一份现代、地道的 `CMakeLists.txt`。最小示例：

```toml
[project]
name = "cmkr_for_beginners"

[target.hello_world]
type = "executable"
sources = ["src/main.cpp"]
```

`cmkr` 可以自举——使用它只需 CMake 和一个 C++ 编译器。

## 文档

📖 **<https://c.vt01.com>** —— 中文语法指南（[快速上手](https://c.vt01.com/guide/getting-started) · [语法总览](https://c.vt01.com/guide/overview) · [target](https://c.vt01.com/guide/target) · [cmake](https://c.vt01.com/guide/cmake)）

官方上游文档：<https://build-cpp.github.io/cmkr/cmake-toml>

## 快速上手

在你的项目目录下执行：

```sh
curl https://gitee.com/cmkr_lib/cmkr/raw/master/cmake/cmkr.cmake -o cmkr.cmake
cmake -P cmkr.cmake
```

引导完成后，按需修改 [`cmake.toml`](https://c.vt01.com/guide/overview)，然后正常运行 CMake：

```sh
cmake -B build
cmake --build build
```

自举完成后，`cmkr` 不给你的工作流增加额外步骤。修改 `cmake.toml` 后，只需重新构建/配置 CMake 工程，`cmkr` 会在必要时自动重新生成 `CMakeLists.txt`。

<sub>**提示**：`cmake.toml`、生成的 `CMakeLists.txt` 以及 `cmkr.cmake` 引导脚本都应纳入版本控制。</sub>

CI 环境下 `cmkr` 引导流程会被跳过，不会给流水线带来额外开销。

## 模板仓库

另一种上手方式是使用 [cmkr_for_beginners](https://github.com/build-cpp/cmkr_for_beginners) 模板仓库。可以直接在 [Gitpod](https://gitpod.io/#https://github.com/build-cpp/cmkr_for_beginners) 打开，或克隆后运行：

```sh
cmake -B build
cmake --build build
```

更多示例与模板可查看 [cmkr topic](https://github.com/topics/cmkr)、[build-cpp organization](https://github.com/build-cpp) 或 [tests](https://gitee.com/cmkr_lib/cmkr/tree/master/tests)。

## 命令行

也可以把 [`cmkr` release](https://gitee.com/cmkr_lib/cmkr/releases) 放到 `PATH` 中，作为命令行工具使用：

```
Usage: cmkr [arguments]
arguments:
    init    [executable|library|shared|static|interface] 创建项目。
    gen                                                  生成 CMakeLists.txt。
    build   <extra cmake args>                           运行 cmake 并构建。
    install                                              运行 cmake --install。
    clean                                                清理构建目录。
    help                                                 显示帮助。
    version                                              当前 cmkr 版本。
```

## 与官方库的不同点

本 Fork 同步自上游 `build-cpp/cmkr` `0.2.46`，并在保持兼容的前提下新增了一组**人性化 API**和路径增强。详细写法见 [target](https://c.vt01.com/guide/target) / [cmake](https://c.vt01.com/guide/cmake)。

### `[target]` 新增字段

#### `sources` 裸目录递归扫描

官方上游只支持具体文件 / `*` / `**` 通配。本 Fork 允许直接写目录名，递归扫描并按已知源/头文件扩展名过滤：

```toml
[target.mylib]
type = "static"
sources = ["src", "include"]   # 递归收集 .cpp/.c/.rc/.h/.hpp/.inl/...，自动忽略 .md/.txt
```

- 收集的源文件扩展名：`.c .cc .cpp .cxx .c++ .m .mm .rc .cu .hip .ispc .cs .java .swift .s .S .asm .nasm` 及 Fortran（`.f .f90 .for ...`）
- 收集的头文件扩展名：`.h .hpp .hh .hxx .h++ .inl .ipp .txx`
- 官方要达到同样效果需逐子目录列 `dir/**.cpp` / `dir/**.hpp`，繁琐

#### `sources` 允许外部路径

官方上游对源文件路径有 `path traversal` 限制，禁止引用 `cmake.toml` 所在目录之外的文件。本 Fork **取消该限制**，外部绝对/相对路径均可使用（输出为绝对路径）：

```toml
[target.x]
sources = ["../shared/src/helper.cpp", "D:/code/common/util.cpp"]
```

> 注意：外部路径会输出为绝对路径，绑定本机位置，**跨机器/CI 不可移植**，谨慎使用。

#### `include-directories` 支持 `dir/**` 递归子目录

官方上游的 `include-directories` 每条只作为一个 `-I`。本 Fork 支持 `dir/**` 后缀，展开为该目录 + 其下**所有递归子目录**，每条各作为一个 `-I`：

```toml
[target.x]
include-directories = ["include/**"]   # → include/ + include/a/ + include/a/b/ ...
```

```cmake
target_include_directories(x PUBLIC include include/a include/a/b)
```

默认（不带 `/**`）行为与官方一致：只加该目录本身，**不递归**——避免改变头文件搜索顺序。需要递归时显式写 `/**`。

#### `post-build`：构建后命令（数组化）

官方上游的 `POST_BUILD` 钩子需手写 `cmake-after` + `add_custom_command`。本 Fork 提供数组化字段，每元素一条命令，`.bat`/`.cmd` 自动加 `cmd /c` 前缀，支持条件前缀：

```toml
[target.x]
post-build = [
    "scripts/build.bat",                                    # 自动 → cmd /c scripts/build.bat
    "${CMAKE_COMMAND} -E copy_if_different a.dll $<TARGET_FILE_DIR:x>",  # 命令原样传递
]
windows.post-build = ["scripts/win_post.bat"]              # 支持条件前缀
```

> `post-build` 必须是数组；写字符串会报错。

#### `win32-executable` + `entry-point`：Windows GUI 子系统

官方上游需手动设 `WIN32_EXECUTABLE` 属性 + 链接选项。本 Fork 一行搞定：

```toml
[target.app]
type = "executable"
win32-executable = true
entry-point = "wWinMainCRTStartup"   # 可选，缺省即此值
```

生成（仅 MSVC 加 `/ENTRY`）：

```cmake
set_target_properties(app PROPERTIES WIN32_EXECUTABLE ON)
if(MSVC)
  target_link_options(app PRIVATE "/SUBSYSTEM:WINDOWS /ENTRY:wWinMainCRTStartup")
endif()
```

> 仅对 `type = "executable"` 生效，其他类型静默忽略。

### `[cmake]` 新增字段

#### `utf-8`：MSVC 默认 `/utf-8`

官方上游无此字段。本 Fork 在 `[cmake]` 下新增，**默认开启**，MSVC 编译时自动加 `/utf-8`，解决中文源码乱码：

```toml
[cmake]
utf-8 = true   # 默认 true；想关掉写 utf-8 = false
```

> 仅 MSVC 生效，其他编译器不生成 `/utf-8`。键名是 `utf-8`（短横线），别写成 `utf_8`/`utf8`。

### `[fetch-content]` 新增字段

#### `dir`：本地目录来源

官方上游的 `[fetch-content.*]` 仅支持 git/svn/url。本 Fork 额外支持 `dir`，直接指向本地工程目录，不拉取：

```toml
[fetch-content.mylib]
dir = "E:/path/to/mylib"
```

> 绝对路径或相对 `cmake.toml` 的路径均可。

### 增强项汇总表

| 字段 | 所在表 | 官方上游 | 本 Fork |
|------|--------|---------|---------|
| `sources = ["src"]` 裸目录 | `[target]` | ✗ 仅文件/通配 | ✓ 递归扫描 + 扩展名过滤 |
| `sources` 外部路径 | `[target]` | ✗ path traversal 报错 | ✓ 允许（输出绝对路径） |
| `include-directories = ["dir/**"]` | `[target]` | ✗ 仅单目录 | ✓ 递归子目录 |
| `post-build` | `[target]` | ✗（需手写 cmake-after） | ✓ 数组化，.bat 自动 cmd /c |
| `win32-executable` / `entry-point` | `[target]` | ✗（需手写属性+链接选项） | ✓ 一行配置 |
| `utf-8` | `[cmake]` | ✗ | ✓ 默认 /utf-8（MSVC） |
| `dir` | `[fetch-content]` | ✗（仅 git/svn/url） | ✓ 本地目录来源 |

> 全部增强均**向后兼容**：不使用这些新字段时，行为与官方上游一致。

## 致谢

- 上游：[build-cpp/cmkr](https://github.com/build-cpp/cmkr)
- [gulrak/filesystem](https://github.com/gulrak/filesystem)
- [Tessil/ordered-map](https://github.com/Tessil/ordered-map)
- [ToruNiina/toml11](https://github.com/ToruNiina/toml11)
- [mpark/variant](https://github.com/mpark/variant)
- [SVG Repo Hammer](https://www.svgrepo.com/svg/192268/hammer)
- [can1357](https://github.com/can1357) 买下了 `cmkr.build` ❤️
- [JustasMasiulis](https://github.com/JustasMasiulis) 修复了暗色主题 ❤️
