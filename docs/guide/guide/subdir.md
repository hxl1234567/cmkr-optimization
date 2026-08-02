# [subdir.*]

把本地子目录加进构建，对应 `add_subdirectory()`。

```toml
[subdir.mysubdir]
condition = "mycondition"
cmake-before = """
message(STATUS "CMake injected before the add_subdirectory() call")
"""
cmake-after = """
message(STATUS "CMake injected after the add_subdirectory() call")
"""
include-before = ["cmake/before-subdir.cmake"]
include-after = ["cmake/after-subdir.cmake"]
```

## 字段速查

| 字段 | 类型 | 说明 |
|------|------|------|
| `condition` | 条件 | 满足才 add_subdirectory |
| `cmake-before` | 多行 | `add_subdirectory()` 前注入 CMake |
| `cmake-after` | 多行 | `add_subdirectory()` 后注入 CMake |
| `include-before` | array | 前 `include()` 的 .cmake 文件 |
| `include-after` | array | 后 `include()` 的 .cmake 文件 |

## 嵌套项目

子目录若自带 `cmake.toml`，cmkr 会作为**嵌套项目**递归处理：

- 继承父项目的 `conditions` 与 `templates`
- 子项目的 `[options]` 里 `"root"` 特值变 `false`
- 深层目录有自己 `[project]` 时按嵌套根处理

```toml
[project]
name = "parent"

[subdir.lib]
[subdir.app]
```

`lib/` 与 `app/` 各自是独立 cmkr 工程。

## 实例：条件子目录

```toml
[project]
name = "myapp"

[options]
MYAPP_BUILD_TOOLS = false

[subdir.tools]
condition = "build-tools"
```

`cmake -DMYAPP_BUILD_TOOLS=ON` 才构建 `tools/`。

## 注意事项

- 子目录路径是相对 `cmake.toml` 所在目录
- 子目录**必须存在**，否则 CMake 报错
- 不需要子目录带自己的 cmake.toml——普通 CMake 子目录也能用（只跑 add_subdirectory）

## 下一步

- [fetch-content](./fetch-content)：外部工程
- [template](./template)：复用配置
