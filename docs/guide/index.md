---
layout: home

hero:
  name: cmkr
  text: cmake.toml 语法指南
  tagline: 用声明式 TOML 描述项目，自动生成现代 CMakeLists.txt
  actions:
    - theme: brand
      text: 快速上手
      link: /guide/getting-started
    - theme: alt
      text: 语法总览
      link: /guide/overview

features:
  - title: 声明式表
    details: "用 [project] / [target.*] / [conditions] 等表描述项目，每个键对应一个 CMake 构造。"
    icon: 📄
  - title: 条件键
    details: windows.sources、x64.definitions 等 `condition.` 前缀，编译期展开为 if() 块。
    icon: 🌿
  - title: 可见性前缀
    details: private-compile-options 控制属性传播，接口/私有/公共一键切换。
    icon: 🔒
  - title: 多行字符串
    details: cmake-before / cmake-after 用 """ """ 内嵌原生 CMake，复杂逻辑任意注入。
    icon: 📝
  - title: 人性化字段
    details: post-build 钩子、win32-executable、utf-8，把真实项目套路提炼为原生语法。
    icon: 🍬
  - title: 依赖语法
    details: fetch-content / vcpkg / find-package / subdir 统一声明式语法，零样板。
    icon: 🔗
---
