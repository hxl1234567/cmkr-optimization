import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'cmkr',
  description: 'cmake.toml 语法指南 — 声明式 CMake 构建系统的配置语法',

  lastUpdated: true,
  cleanUrls: true,

  head: [
    ['meta', { name: 'theme-color', content: '#0EA5E9' }],
    ['link', { rel: 'icon', type: 'image/x-icon', href: '/cmkr.ico' }]
  ],

  themeConfig: {
    siteTitle: 'cmkr',

    nav: [
      { text: '快速上手', link: '/guide/getting-started' },
      { text: '语法总览', link: '/guide/overview' },
      { text: 'Gitee', link: 'https://gitee.com/cmkr_lib/cmkr' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: '入门',
          collapsed: false,
          items: [
            { text: '快速上手', link: '/guide/getting-started' },
            { text: '语法总览', link: '/guide/overview' },
            { text: '基础概念', link: '/guide/basics' }
          ]
        },
        {
          text: '核心语法',
          collapsed: false,
          items: [
            { text: '[project]', link: '/guide/project' },
            { text: '[target]', link: '/guide/target' },
            { text: '[cmake]', link: '/guide/cmake' },
            { text: '[conditions]', link: '/guide/conditions' },
            { text: '[options]', link: '/guide/options' },
            { text: '[variables]', link: '/guide/variables' }
          ]
        },
        {
          text: '依赖管理',
          collapsed: false,
          items: [
            { text: '[fetch-content]', link: '/guide/fetch-content' },
            { text: '[vcpkg]', link: '/guide/vcpkg' },
            { text: '[find-package]', link: '/guide/find-package' },
            { text: '[subdir]', link: '/guide/subdir' }
          ]
        },
        {
          text: '扩展',
          collapsed: false,
          items: [
            { text: '[template]', link: '/guide/template' },
            { text: '[[target.*.custom-command]]', link: '/guide/custom-command' },
            { text: '[[test]]', link: '/guide/test' },
            { text: '[[install]]', link: '/guide/install' }
          ]
        },
        {
          text: '实例与注意',
          collapsed: false,
          items: [
            { text: '综合实例', link: '/guide/examples' },
            { text: '注意事项', link: '/guide/notes' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/build-cpp/cmkr' }
    ],

    outline: {
      level: [2, 3],
      label: '本页导航'
    },

    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    },

    lastUpdatedText: '最后更新',

    search: { provider: 'local' }
  }
})
