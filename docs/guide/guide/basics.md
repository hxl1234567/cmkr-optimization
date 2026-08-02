# 基础概念

要用好 cmkr，先理解三个 CMake 基础概念：**project**、**target**、**property**。

## Project（项目）

CMake **project** 是一组 target 的集合。对库而言，project 通常对应其他项目可依赖的**包**。

::: tip 对应关系
Visual Studio 里：CMake **project** ≈ 解决方案，CMake **target** ≈ 工程。
:::

## Target（目标）

CMake 的基本单位是 **target**（CMake 文档叫 [binary target](https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html#binary-targets)）：一个可执行文件或库。cmkr 里对应 `[target.*]`。

```toml
[target.hello_world]
type = "executable"
sources = ["src/main.cpp"]
```

## Target Properties（属性）

target 有一组**属性**描述如何构建：

- **Sources**：编译用到的 `*.cpp`
- **Compile options**：编译器命令行参数
- **Link libraries**：构建所需的**依赖**

完整属性列表见 [CMake 文档](https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html#properties-on-targets)。

::: warning 关键理解：link 的语义
CMake 里 **link** 不只是「把库加进链接器命令行」，还会**传播被链接 target 的属性**。可以把 **linking** 理解为 **depending on**。
:::

## 可见性：private / interface / public

属性传播取决于**可见性**：

| 可见性 | 含义 |
|--------|------|
| **Private** | 仅构建 target 自身时使用 |
| **Interface** | 依赖该 target 的消费者使用时使用 |
| **Public** | private + interface 组合 |

实践中默认用 **private**，只有当库的消费者「必须」这个属性才能编译时才用 **public**。

### 例子：include directories

两个 target：

1. `StringUtils`：字符串工具库
   - Sources：`StringUtils/src/stringutils.cpp`
   - Include directories：`StringUtils/include`
2. `DataProcessor`：使用 `StringUtils` 的可执行程序
   - Sources：`DataProcessor/src/main.cpp`
   - Link libraries：`StringUtils`

`StringUtils` 的 include directories 必须 **public**。若为 private，`DataProcessor` 里 `#include <stringutils.hpp>` 会失败——include directories 属性没有被传播。

`cmake.toml`：

```toml
[project]
name = "DataProcessor"

[target.StringUtils]
type = "static"
sources = ["StringUtils/src/stringutils.cpp"]
headers = ["StringUtils/include/stringutils.hpp"]
include-directories = ["StringUtils/include"]

[target.DataProcessor]
type = "executable"
sources = ["DataProcessor/src/main.cpp"]
link-libraries = ["StringUtils"]
```

### cmkr 默认可见性

未写 `private-` 前缀时，各 target 类型的默认可见性：

| 类型 | 可见性 |
|------|--------|
| `executable` | `PRIVATE` |
| `library` / `shared` / `static` / `object` | `PUBLIC` |
| `interface` | `INTERFACE` |

需要私有时用 `private-` 前缀，例如 `private-compile-options`、`private-link-libraries`。详见 [target](./target)。

## 下一步

- [语法总览](./overview)：全部字段入口
- [条件系统](./conditions)：条件性属性
