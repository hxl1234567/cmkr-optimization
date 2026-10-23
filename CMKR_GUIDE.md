# cmkr 构建配置指南

> 本文件由 cmkr 首次生成时创建,之后不会被覆盖 — 可自由补充团队约定。

## 铁律
- `CMakeLists.txt` 全部由 `cmake.toml` 生成,**不要手改**;改 `cmake.toml` 后 `cmake --build` 自动重生成
  (根 CMakeLists.txt 通过 CMAKE_CONFIGURE_DEPENDS 监听全树 cmake.toml)。
- **gen 只从仓库根跑**(`cmkr gen`):根 gen 递归生成全部含 [project] 的子目录。
  子目录里单独跑 gen 会因缺少根条件种子而报 Unknown condition。

## 心智模型
- **根 cmake.toml** = 全局开关板([options])+ 依赖([fetch-content])+ 子项目挂载([subdir])
- **子 cmake.toml** = 该子项目 target 的编译配置;[variables] 只写"与根默认不同的例外"
  (普通 set 无条件覆盖),与根一致就什么都不写
- **[options] `ENABLE_X = 默认`** = 开关唯一声明点:缓存变量 + cmake-gui/-D 可覆盖 +
  同名条件自动存在,任何 target 直接写 `ENABLE_X.compile-definitions` 等
- 影子默认值:toml 改默认值 → 旧 build 目录下次 configure 跟随;-D/cmake-gui 用户值始终优先
- 同名 option 全构建树只能声明一次(CMKR_OPT_*_PREV 追踪是全局缓存项,重复声明互踩)
- **[conditions]** 只装组合逻辑(AND/OR/NOT)与平台探测(x64/x32);纯布尔开关不用写条件
- 含 [project] 的子目录 = 独立 cmkr 根:根条件表自动种子下发(0.2.48+),变量不继承
- C++20 模块接口(.ixx)用 `module-sources`(需 [cmake] version >= 3.25);.rc 直接写 sources

## 常用操作
- 重新生成:仓库根 `cmkr gen`(或 gen_all.bat)
- 切开关:`cmake -B <build> -DENABLE_X=ON`,或 cmake-gui;toml 改默认值会跟随
- 嵌套子项目自动刷新:改子 cmake.toml 后直接 `cmake --build`,无需手动 gen
