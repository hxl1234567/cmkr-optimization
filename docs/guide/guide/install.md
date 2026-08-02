# [[install]]

声明安装规则，数组形式（`[[...]]`）可写多条。对应 `install(TARGETS/FILES/DIRECTORY ...)`。

::: warning 未完成功能
`[[install]]` 官方标记**未完成**，接口未来可能变化。
:::

## 语法

```toml
[[install]]
condition = "mycondition"
targets = ["mytarget", "mytest"]
destination = ["bin"]
component = "mycomponent"
files = ["content/my.png"]
dirs = ["include"]
configs = ["Release", "Debug"]
optional = false
```

## 字段速查

| 字段 | 类型 | 说明 |
|------|------|------|
| `targets` | array | 要安装的 target |
| `destination` | array | 目标目录（`bin`、`lib`、`include` 等） |
| `component` | string | 组件名 |
| `files` | array | 额外文件 |
| `dirs` | array | 整个目录 |
| `configs` | array | 限定配置 |
| `optional` | bool | 缺文件不报错 |
| `condition` | 条件 | 满足才安装 |

## 实例

```toml
[project]
name = "mylib"

[target.mylib]
type = "static"
sources = ["src/mylib.cpp"]
include-directories = ["include"]

[[install]]
targets = ["mylib"]
destination = ["lib"]

[[install]]
dirs = ["include"]
destination = ["include"]
```

```cmake
install(TARGETS mylib DESTINATION lib)
install(DIRECTORY include DESTINATION include)
```

用 `cmkr install`（或 `cmake --install build`）执行。

## 注意事项

- `targets` 里的 target 必须在同一 `cmake.toml` 声明
- 未完成功能：接口可能变
- 想带组件打包（CPack 风格），用 `component` 分组

## 下一步

- [test](./test)：测试声明
- [project](./project)：项目级配置
