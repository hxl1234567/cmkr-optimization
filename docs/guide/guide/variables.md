# [variables]

发射普通 CMake `set()` 变量，用于配置子项目与包。

```toml
[variables]
MYBOOL = true
MYSTRING = "hello"
```

```cmake
set(MYBOOL true)
set(MYSTRING "hello")
```

## 实例：给 fetch-content 项目传参

```toml
[variables]
MYPROJECT_BUILD_TESTS = false       # 影响 fetch 引入的工程

[fetch-content.dep]
git = "https://github.com/me/dep"
tag = "v1.0"
```

::: warning 与 [options] 的区别
`[variables]` 发射普通 `set()`（无缓存、不生成条件）；`[options]` 发射 `option()` 缓存变量并自动生成条件。**不要**同名混用——同一名字一个 `set` 一个 `option`，configure 行为冲突。
:::

## 注意事项

- 变量值只支持 TOML 标量（字符串 / 布尔 / 数字）
- 想让变量可在命令行覆盖，用 [options](./options) 而不是 variables

## 下一步

- [options](./options)：缓存选项 + 自动条件
- [fetch-content](./fetch-content)：配合传参
