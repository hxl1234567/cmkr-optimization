# [[test]]

声明 CTest 测试，数组形式（`[[...]]`）可写多条。对应 `add_test()`。

::: warning 未完成功能
`[[test]]` 官方标记**未完成**，接口未来可能变化。当前仓库测试主要走 fixture 方式——每个 `tests/<name>/` 目录一个完整 cmake.toml 工程，`cmkr build` 配置编译成功即通过。
:::

## 语法

```toml
[[test]]
condition = "mycondition"
name = "mytest"
command = "$<TARGET_FILE:mytest>"
arguments = ["arg1", "arg2"]
configurations = ["Debug", "Release", "RelWithDebInfo", "MinSizeRelease"]
working-directory = "mytest-dir"
```

## 字段速查

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 测试名，**全局唯一** |
| `command` | string | 命令；常用 `$<TARGET_FILE:mytest>` 取 target 产物路径 |
| `arguments` | array | 参数列表 |
| `configurations` | array | 只在列出的配置下注册 |
| `working-directory` | string | 工作目录 |
| `condition` | 条件 | 满足才注册 |

## 实例

```toml
[project]
name = "mylib"

[target.mylib]
type = "static"
sources = ["src/mylib.cpp"]

[target.mylib_tests]
type = "executable"
sources = ["tests/main.cpp"]
link-libraries = ["mylib"]

[[test]]
name = "unit"
command = "$<TARGET_FILE:mylib_tests>"
arguments = ["--verbose"]
```

```cmake
add_test(NAME unit COMMAND $<TARGET_FILE:mylib_tests> --verbose)
```

## 注意事项

- `name` 全局唯一，重复会生成失败
- 未完成功能：接口可能变，别在生产 build 上重度依赖
- 多配置生成器（VS）下 `command` 用 `$<TARGET_FILE:xxx>` 能自动解析配置路径

## 下一步

- [install](./install)：安装规则
- [custom-command](./custom-command)：构建钩子配合测试
