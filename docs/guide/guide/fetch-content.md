# [fetch-content.*]

拉取外部工程，对应 CMake `FetchContent_Declare`。支持 git / svn / url / **本地目录** 四种来源。

## git

```toml
[fetch-content.gitcontent]
condition = "mycondition"
git = "https://github.com/myuser/gitcontent"
tag = "v0.1"
shallow = false
system = false
subdir = ""
```

## svn

```toml
[fetch-content.svncontent]
svn = "https://svn-host.com/url"
rev = "svn_rev"
```

## url（压缩包）

```toml
[fetch-content.urlcontent]
url = "https://content-host.com/urlcontent.zip"
# 这些算法等价（选一个）：
# md5, sha1, sha224, sha256, sha384, sha512, sha3_224, sha3_256, sha3_384, sha3_512
hash = "SHA1 502a4e25b8b209889c99c7fa0732102682c2e4ff"
sha1 = "502a4e25b8b209889c99c7fa0732102682c2e4ff"
```

## 本地目录（dir）

不拉取，直接指向本地工程目录：

```toml
[fetch-content.mylib]
dir = "E:/path/to/mylib"
```

::: tip 键名透传
`[fetch-content.xxx]` 里匹配 CMake 变量名（`[A-Z_]+`）的键会原样传给 `FetchContent_Declare`。除 `git`/`svn`/`url`/`hash`/`dir` 等特殊键外，可按 CMake 参数自由扩展。
:::

::: warning 状态
`[fetch-content]` 官方标记**未完成**，未来版本可能变化。
:::

## 字段速查

| 字段 | 来源 | 说明 |
|------|------|------|
| `git` | git | 仓库地址 |
| `tag` | git | 拉取 tag |
| `shallow` | git | 浅克隆 |
| `system` | git | 优先用系统包 |
| `subdir` | git | 仓库内子目录 |
| `svn` | svn | SVN 地址 |
| `rev` | svn | SVN 版本 |
| `url` | url | 压缩包地址 |
| `hash` / `sha1` 等 | url | 完整性校验（选一个算法） |
| `dir` | 本地 | 本地目录路径 |
| `condition` | 所有 | 条件前缀 |

## 实例

```toml
[project]
name = "myapp"

[fetch-content.nlohmann_json]
git = "https://github.com/nlohmann/json"
tag = "v3.11.3"

[target.app]
type = "executable"
sources = ["src/main.cpp"]
link-libraries = ["nlohmann_json::nlohmann_json"]
```

## 注意事项

- fetch 引入的 cmkr 工程，其 `[options]` 的 `"root"` 特值变 `false`
- `dir` 用绝对路径或相对 `cmake.toml` 的路径均可
- 想固定拉取版本，用 `tag` + `hash` 双重锁定

## 下一步

- [vcpkg](./vcpkg)：包管理器方案
- [find-package](./find-package)：查找系统包
