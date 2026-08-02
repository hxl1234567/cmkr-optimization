# 快速上手

从零写第一个 `cmake.toml` 并构建。只需 CMake + C++ 编译器。

## 1. 写 cmake.toml

最小三元素：`[project]` 声明项目，`[target.xxx]` 声明目标，`sources` 列源文件。

```toml
[project]
name = "hello_world"

[target.hello]
type = "executable"
sources = ["src/main.cpp"]
```

```cpp
// src/main.cpp
#include <iostream>
int main() { std::cout << "hello cmkr\n"; }
```

## 2. 生成 CMakeLists.txt

```bash
# 方式 A：有 cmkr 二进制在 PATH
cmkr gen

# 方式 B：没装 cmkr——用引导脚本（首次会编译 cmkr 自身）
curl https://gitee.com/cmkr_lib/cmkr/raw/master/cmake/cmkr.cmake -o cmkr.cmake
cmake -P cmkr.cmake
```

::: tip 引导做了什么
目录里没有 `cmake.toml` 时 `cmake -P cmkr.cmake` 会执行 `cmkr init` 生成工程；有则执行 `cmkr gen` 生成 `CMakeLists.txt`。引导产物是标准 CMakeLists，之后**不需要**再手动跑 cmkr。
:::

## 3. 构建

```bash
cmake -B build
cmake --build build
```

产物 `build/hello`（Windows 上 `build/Debug/hello.exe` 或 `build/Release/hello.exe`，取决于配置）。

## 4. 改语法，自动生效

编辑 `cmake.toml` 加一个条件源文件：

```toml
[project]
name = "hello_world"

[target.hello]
type = "executable"
sources = ["src/main.cpp"]
windows.definitions = ["UNICODE"]          # 条件键：Windows 下定义宏
linux.compile-options = ["-pthread"]       # Linux 下加编译参数
```

照常 `cmake --build build`。生成的 `CMakeLists.txt` 检测到 `cmake.toml` 变了，会自动重新 `cmkr gen`，新条件立即生效。**不用**手动重新生成。

## 更完整的骨架

结合常用语法：

```toml
[project]
name = "myapp"
version = "1.0.0"
description = "Demo app"
languages = ["C", "CXX"]

[cmake]
version = "3.15"

[options]
MYAPP_BUILD_TESTS = false

[target.mylib]
type = "static"
sources = ["src/mylib.cpp"]
include-directories = ["include"]          # public：头文件库给消费者
private-compile-options = ["/W4"]          # 仅自己

[target.app]
type = "executable"
sources = ["src/main.cpp"]
link-libraries = ["mylib"]

[target.tests]
condition = "build-tests"                  # 选项归一化条件：MYAPP_BUILD_TESTS
type = "executable"
sources = ["tests/main.cpp"]
link-libraries = ["mylib"]
```

各语法详解：

- 语法总览：[overview](./overview)
- `[project]` / `[cmake]`：[project](./project)
- `[target]`：[target](./target)
- 条件：[conditions](./conditions)
- `[options]` / `[variables]`：[options](./options) / [variables](./variables)

## 下一步

- [基础概念](./basics)：target / property / 可见性
- [综合实例](./examples)：完整工程示例
- [注意事项](./notes)：常见坑
