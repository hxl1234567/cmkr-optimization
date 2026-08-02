# [vcpkg]

vcpkg 包管理器集成。单例表。

```toml
[vcpkg]
version = "2024.11.16"
url = "https://github.com/microsoft/vcpkg/archive/refs/tags/2024.11.16.tar.gz"
packages = ["fmt", "zlib"]
overlay-ports = ["my-ports"]
overlay-triplets = ["my-triplets"]
```

## version / url

| 字段 | 说明 |
|------|------|
| `version` | 自动从[官方仓库](https://github.com/microsoft/vcpkg/releases)生成 `url` |
| `url` | 自定义注册源；写了 `url` 可省 `version` |

```toml
[vcpkg]
version = "2024.11.16"    # url 自动生成
```

## packages：包列表

```toml
[vcpkg]
packages = ["fmt", "zlib", "spdlog"]
```

### 特性语法

| 写法 | 含义 |
|------|------|
| `imgui[docking-experimental,freetype,sdl2-binding,opengl3-binding]` | 指定特性 |
| `cpp-httplib[core,openssl]` | 禁默认特性，只用列出的 |

## overlay-ports / overlay-triplets

| 字段 | 说明 |
|------|------|
| `overlay-ports` | 内嵌自定义 port，免 fork 官方注册源 |
| `overlay-triplets` | 自定义 triplet（如 Windows 默认静态库） |
| `overlay` | 两者一步指定，指向同一目录树 |

overlay 用法参考 [vcpkg 文档](https://learn.microsoft.com/en-us/vcpkg/concepts/overlay-ports) 与 [vcpkg_template](https://github.com/build-cpp/vcpkg_template)。

## 实例

```toml
[project]
name = "myapp"

[vcpkg]
version = "2024.11.16"
packages = ["fmt", "spdlog"]

[target.app]
type = "executable"
sources = ["src/main.cpp"]
link-libraries = ["fmt", "spdlog"]
```

## 注意事项

- 包名带 `[]` 特性时，`link-libraries` 用基础名（`imgui` 而非 `imgui[...]`）
- 包在 vcpkg.io / vcpkg.link 搜索
- vcpkg 是单例表，只能声明一个

## 下一步

- [fetch-content](./fetch-content)：直接拉源码
- [find-package](./find-package)：系统查找
