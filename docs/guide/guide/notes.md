# 注意事项

踩坑合集。按层次分组：TOML → cmkr 语法 → 语义 → 工作流。

## TOML 层面

### [project] / [cmake] 是单例表

`[project]`、`[cmake]` 只能写**一个**。重复声明同名表是 TOML 语法错误。所有项目级键放同一张表。

```toml
[project]
name = "a"
[project]        # ✗ TOML 语法错误
name = "b"
```

### 数组 vs 字符串

`post-build` **必须是数组**，写成字符串报错。`sources`、`link-libraries` 等也是数组。用错类型 cmkr 直接拒绝并提示。

### 多行字符串里写 `"` 不必转义

`"""..."""` 内嵌 CMake 时，内部的 `"` 和换行随意写：

```toml
[project]
cmake-after = """
target_compile_definitions(app PRIVATE PLATFORM="win")   # " 不用转义
"""
```

## cmkr 语法层面

### 条件名规则

条件名只能小写字母数字 + 短横线（`[0-9a-z-]`）。`Windows`、`BUILD_TESTS`、`my_cond` 都不合法。选项归一化条件（`build-tests`）满足此规则。

### `private-` 前缀才私有

不写前缀时可见性取决于 target 类型（executable 默认 PRIVATE，库默认 PUBLIC）。**想要私有必须显式 `private-`**，否则头文件库的 include 目录会传播出去（通常是想要的），编译参数也会传播（通常不想要）。

### 条件键与字段名不重复

`windows.windows` 这类写法无意义。条件键名必须是已定义条件（预定义或 `[conditions]`）或带引号的 CMake 表达式。

### `$<name>` 只做文本替换

`"$<linux>"` 在 cmkr 里是**字符串替换**为 linux 条件的 CMake 表达式，不是 cmkr 自己求值。引号内其它内容原样进入 `if()` 条件。

## 语义层面

### link = 依赖

`link-libraries` 不只是链接器参数，还**传播**被链 target 的属性。用 `::` 确保 target 存在：

```toml
[target.example]
type = "executable"
link-libraries = ["mylib::mylib"]   # 推荐：拼写错误立刻报错
```

### include-directories 要 public

库的头文件目录不设 public，消费者 `#include` 会失败。这是最常踩的坑，见 [基础概念](./basics)。

### 别禁用 C 语言

`languages = ["CXX"]` 偶尔让 fetch-content 引入的工程失败，报错难懂。不确定就保留 `C`。

## 工作流层面

### 别手改生成的 CMakeLists.txt

`CMakeLists.txt` 是**生成物**。手改会在下次 `cmkr gen` 时被覆盖。改 `cmake.toml`，重新构建自动再生。

### 提交时保持同步

`cmake.toml`、生成的 `CMakeLists.txt`、`cmkr.cmake` 都提交到版本控制。CI 会跑 `cmkr gen` 并 `git diff` 检查——CMakeLists 与 cmake.toml 不同步会**挂 CI**。

### CI 不执行引导

CI 里 `cmkr()` 宏跳过生成（`CI` / `CMKR_SKIP_GENERATION` / `CMKR_BUILD_SKIP_GENERATION`）。本地改完语法记得提交同步的 CMakeLists。

## 平台层面

| 注意 | 说明 |
|------|------|
| `win32-executable` 只对 executable 生效 | 写在 static/library 上静默忽略 |
| `utf-8` 仅 MSVC 生效 | 其他编译器不生成 `/utf-8` |
| `.bat` 需 `cmd /c` | `post-build` 已自动加前缀；手写命令时若目标平台是 Windows，注意命令行长度与引号转义 |
| `msvc-runtime` 需 MSVC | 非 MSVC 忽略，自动设 `CMP0091` 策略 |
| `relative-paths` 测试仅 WIN32 | 平台特定语法用条件键保护 |
| sources 外部路径输出绝对路径 | 跨机器/CI 不可移植，慎用 |
| 裸目录扫描按扩展名过滤 | `sources = ["src"]` 只收源/头文件；要全收用 `src/**` |
| `include-directories` 默认不递归 | 需递归子目录显式写 `dir/**` |

## 未完成功能

`[[test]]`、`[[install]]`、`[fetch-content]` 官方标记**未完成**，接口可能变。生产 build 别重度依赖。测试目前主流走 fixture 方式（`tests/<name>/cmake.toml` 完整工程 + ctest 构建）。

## 下一步

- [语法总览](./overview)：回到基础
- [综合实例](./examples)：看正确写法
