# cmkr 人性化 API 增强设计

日期:2026-08-02
状态:草稿

## Context

分析用户在 14 个真实项目(DbgrDriver/DbgHook/DbgWebview/cf/pubg/tzmManage/webview/MyDriver/commonDriverTools 等)的 `cmake.toml` 使用,发现 `cmake-before`/`cmake-after` 块中 **80% 是重复固定套路**:

| 用途 | 出现处 | 现状 |
|---|---|---|
| POST_BUILD 跑 bat/命令 | 10 处 | `add_custom_command(TARGET x POST_BUILD ...)` 手写 |
| WIN32 GUI 子系统 | 4+ 处 | `set_target_properties(LINK_FLAGS "/SUBSYSTEM:WINDOWS /ENTRY:...")` |
| `/utf-8` 编译选项 | 5 处 | `add_compile_options(/utf-8)` |

目标:将这些重复套路提炼为 cmkr 原生字段,减少手写 CMake。纯增强,不破坏现有语法。

用户已确认取舍:
- `post-build` 单数组自动区分 bat 文件与命令,**只支持数组不支持字符串**
- `win32-executable` 支持
- `utf-8` **默认开启**,可手动关闭
- 未选:`cxx-standard` 别名、`copy-dlls` 独立字段(并入 post-build)、配置级编译选项

## 新 API 设计

### 1. `[target.x] post-build`(POST_BUILD 钩子)

```toml
[target.DbgDriver]
post-build = [
    "scripts/build.bat",                                  # .bat 结尾 → cmd /c scripts/build.bat
    "cmd /c ${CMAKE_CURRENT_BINARY_DIR}/../../build/a.bat",  # 命令,自动不带 cmd /c 前缀
    "${CMAKE_COMMAND} -E copy_if_different a.dll b.dll $<TARGET_FILE_DIR:x>",  # 命令
]
```

**规则:**
- 数组类型,每个元素一条命令。**元素必须是数组;写成字符串报错**(提示:post-build 需用数组,每条一个 bat 或命令)。
- 元素以 `.bat`/`.cmd` 结尾(大小写不敏感)→ 生成 `cmd /c <元素>`。
- 其余元素 → 原样作为 `COMMAND` 传给 `add_custom_command`。
- 支持条件前缀:`windows.post-build`、`x64.post-build` 等。

**生成**(target 定义后,按条件包 if 块):
```cmake
add_custom_command(TARGET x POST_BUILD COMMAND cmd /c scripts/build.bat)
add_custom_command(TARGET x POST_BUILD COMMAND cmd /c ${CMAKE_CURRENT_BINARY_DIR}/../../build/a.bat)
add_custom_command(TARGET x POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different a.dll b.dll $<TARGET_FILE_DIR:x>)
```

### 2. `[target.x] win32-executable`

```toml
[target.DbgWebview]
win32-executable = true
entry-point = "wWinMainCRTStartup"   # 可选;缺省 "wWinMainCRTStartup"
```

**规则:**
- `win32-executable = true` 仅对 `type = "executable"` 生效;其他类型忽略。
- `entry-point` 可选字符串,缺省 `wWinMainCRTStartup`(MSVC `wWinMain` 入口)。
- 支持条件前缀(可选,简单 bool 即可,设计为 `Condition<bool>` 一致性)。

**生成**(target 后):
```cmake
set_target_properties(x PROPERTIES WIN32_EXECUTABLE ON)
if(MSVC)
  target_link_options(x PRIVATE "/SUBSYSTEM:WINDOWS /ENTRY:wWinMainCRTStartup")
endif()
```
非 MSVC 只设 `WIN32_EXECUTABLE`。

### 3. `[cmake] utf-8`(默认开启)

```toml
[cmake]
utf-8 = false    # 显式关闭;缺省 true
```

**规则:**
- 缺省 `true`。`false` 显式关闭。
- 仅 MSVC 生效。

**生成**(project() 后,全局):
```cmake
if(MSVC)
  add_compile_options(/utf-8)
endif()
```
`utf-8 = false` 时不生成。

## 数据模型变更

`include/project_parser.hpp`:
- `Target` 新增 `ConditionVector post_build;`(`post-build`)
- `Target` 新增 `Condition<bool> win32_executable;`(`win32-executable`)
- `Target` 新增 `Condition<std::string> entry_point;`(`entry-point`)
- `Project` 新增 `bool utf8 = true;`(`[cmake] utf-8`,缺省 true)

`src/project_parser.cpp`:解析上述字段(带 TomlChecker 校验,post-build 元素类型检查)。

`src/cmake_generator.cpp`:
- project() 后按 `utf8` 生成 `add_compile_options(/utf-8)`(MSVC 条件)
- target 后按 `post_build` 生成 POST_BUILD 命令(自动 cmd /c 前缀)
- target 后按 `win32_executable` + `entry_point` 生成属性与链接选项

## 测试

新增测试 fixture `tests/post-build/`:
- 一个 executable + `post-build` 数组(含 1 个 .bat 元素 + 1 个命令元素)
- 验证生成 CMakeLists 包含对应 `add_custom_command(TARGET ... POST_BUILD ...)`
- `win32-executable = true` 生成验证
- `[cmake] utf-8 = false` 生成验证(不含 /utf-8)
- 构建成功即通过(ctest 框架:fixture 内 `cmkr build`)

测试列表加入 `tests/cmake.toml`,重新生成 `tests/CMakeLists.txt`。

## 验证

1. 构建:`cmake -B build && cmake --build build`
2. `cmkr gen` 后生成物与 cmake.toml 同步:`git diff --exit-code`
3. `ctest --test-dir build/tests` 全过
4. 用新字段重写用户一个真实项目(DbgDriver 的 post-build/win32/utf-8)验证少写 cmake-before/after
5. clang-format + editorconfig 通过

## 兼容性

- 纯新增字段,现有 cmake.toml 零影响。
- `post-build` 写字符串报错为行为变化,但此前无此字段,无破坏。
