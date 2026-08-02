# [template]

用 `[template.xxx]` 定义**自定义 target 类型**，避免重复声明相同的属性组合。

## 语法

```toml
[template.example]
condition = "MYPROJECT_BUILD_EXAMPLES"
type = "executable"
link-libraries = ["myproject::mylib"]
add-function = ""
pass-sources = false

# 使用模板：type 指向模板名
[target.myexample]
type = "example"
sources = ["src/myexample.cpp"]
```

`template` 的属性和 `[target]` 一样，两个例外字段：

| 字段 | 说明 |
|------|------|
| `add-function` | 自定义 add 函数。有的工程（如 [pybind11](https://pybind11.readthedocs.io/en/stable/cmake/index.html#new-findpython-mode)）有自己的 `add_xxx`，在这里指定 |
| `pass-sources` | 为 `true` 时直接把 sources 传给 add 函数，而不是用 `target_sources` |

## 合并规则

模板属性与 target 自身属性**合并**：

```toml
[template.console-app]
type = "executable"
compile-options = ["/W4"]

[target.one]
type = "console-app"
sources = ["src/one.cpp"]
compile-options = ["/W4", "/WX"]      # 模板的 + 自己的，数组拼接
```

- 数组字段：模板与 target 的数组**拼接**
- 标量字段：target 覆盖模板
- 条件键同样继承：模板里 `windows.xxx` 也会带到使用它的 target

## 条件化模板

模板整体可以带 `condition`。子项目会继承父项目的 templates——在根项目定义一次，所有子目录都能用。

## 实例：examples 模板

```toml
[project]
name = "myproject"

[options]
MYPROJECT_BUILD_EXAMPLES = "root"

[template.example]
condition = "build-examples"              # 只有构建 examples 时 target 才生成
type = "executable"
link-libraries = ["myproject::mylib"]     # 所有 example 都链库

[target.ex_demo]
type = "example"
sources = ["examples/demo.cpp"]

[target.ex_render]
type = "example"
sources = ["examples/render.cpp"]
```

两个 example target 只需写差异部分（sources），公共配置全在模板里。

## 注意事项

- 模板名与 target 的 `type` 同名即生效；`type` 写内置类型（executable 等）时不用模板
- `pass-sources = true` 时**不要**再在 target 里写 `sources` 之外的其他 sources 字段，避免重复传
- 模板的 `add-function` 若为空字符串，回落到标准 `add_executable` / `add_library`

## 下一步

- [target](./target)：模板最终展开成 target
- [综合实例](./examples)：模板 + 条件组合实战
