# [cmake]

配置生成的 CMake 行为。单例表。

```toml
[cmake]
version = "3.15"
cmkr-include = "cmkr.cmake"
utf-8 = true   # 默认 true，MSVC 下自动加 /utf-8
```

## version

最低 CMake 版本，对应 `cmake_minimum_required()`。

```toml
[cmake]
version = "3.20"
```

```cmake
cmake_minimum_required(VERSION 3.20)
```

## cmkr-include

引导脚本路径，生成的 `CMakeLists.txt` 会 `include()` 它。默认 `"cmkr.cmake"`，通常不用改。

## utf-8（人性化字段）

MSVC 编译时自动加 `/utf-8`，解决中文源码乱码。**默认 `true`**，只需关闭时才写：

```toml
[cmake]
utf-8 = false
```

开启时（project() 之后、全局）：

```cmake
if(MSVC)
  add_compile_options(/utf-8)
endif()
```

::: tip 只影响 MSVC
`utf-8` 仅 MSVC 生效，其他编译器不生成 `/utf-8` 选项。
:::

## 实例

```toml
[project]
name = "myapp"

[cmake]
version = "3.20"
utf- = true      # ✗ 拼写错误——正确键是 utf-8
```

::: danger 键名是 utf-8
键名 `utf-8` 含短横线，别写成 `utf_8` 或 `utf8`。拼错 cmkr 直接报未知键。
:::

正确写法：

```toml
[cmake]
version = "3.20"
utf-8 = true
```

## 下一步

- [project](./project)：项目声明
- [target](./target)：构建目标
