# [find-package.*]

查找已安装的包，对应 `find_package()`。

```toml
[find-package.mypackage]
condition = "mycondition"
version = "1.0"
required = true
config = true
components = ["mycomponent"]
```

## 字段速查

| 字段 | 类型 | 说明 |
|------|------|------|
| `condition` | 条件 | 满足才 find_package |
| `version` | string | 版本要求；不带 `=` 是最低版本，带 `=` 是精确版本 |
| `required` | bool | 找不到报错（REQUIRED） |
| `config` | bool | 强制 CONFIG 模式 |
| `components` | array | 组件列表 |

```toml
[find-package.OpenGL]
required = true
components = ["GL", "GLU"]
```

## 实例：选项条件化查找

```toml
[project]
name = "myapp"

[options]
MYAPP_USE_OPENCV = false

[find-package.OpenCV]
condition = "use-opencv"          # 选项归一化条件
required = true

[target.app]
type = "executable"
sources = ["src/main.cpp"]
condition = "use-opencv"
link-libraries = ["OpenCV::core"]
```

## 注意事项

- `version` 语义：`"1.0"` = ≥1.0；`"=1.0"` = 精确 1.0
- `config = true` 强制 Config 模式查找，适合无 FindXXX 模块的包
- 找不到且 `required = false` 时，`link-libraries` 里的目标可能不存在——用条件键保护

## 下一步

- [fetch-content](./fetch-content)：源码级依赖
- [vcpkg](./vcpkg)：包管理器
