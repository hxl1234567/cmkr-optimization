#!/usr/bin/env bash
# 构建 VitePress 指南并把产物提交到 gh-pages 分支。
# 用法:
#   docs/deploy.sh            # 构建 + 本地 gh-pages 提交(不推送)
#   docs/deploy.sh push       # 同上,并强制推送到远端 gh-pages 分支
#
# 默认部署目标 = origin1 (https://hxl1234567.github.io/cmkr-optimization/),
# GitHub Pages 一次性配置: 仓库 Settings -> Pages -> Source 选 gh-pages 分支 /(root)。
# 换目标: REMOTE=origin BASE=/cmkr/ docs/deploy.sh push   (Gitee Pages 同理, 网页开服务)
set -e
cd "$(dirname "$0")/guide"

REMOTE="${REMOTE:-origin1}"
BASE="${BASE:-/cmkr-optimization/}"
ORIGIN_URL="$(git -C ../.. remote get-url "$REMOTE")"

echo "[deploy] remote = $REMOTE ($ORIGIN_URL)"
echo "[deploy] base   = $BASE"

npx vitepress build --base "$BASE"

HEAD_COMMIT="$(git -C ../.. rev-parse --short HEAD)"
cd .vitepress/dist
if [ ! -d .git ]; then
    git init -q -b gh-pages
fi
git add -A
git commit -q -m "deploy: docs from ${HEAD_COMMIT} ($(date '+%Y-%m-%d %H:%M'))" || echo "[deploy] no changes since last deploy"
TREE="$(git rev-parse HEAD)"
cd ..

echo "[deploy] gh-pages tree = $TREE"
if [ "${1:-}" = "push" ]; then
    git -C ../.. push --force "$ORIGIN_URL" "$TREE:refs/heads/gh-pages"
    echo "[deploy] pushed. GitHub Pages: 仓库 Settings -> Pages 确认 Source=gh-pages 后即可访问。"
else
    echo "[deploy] 本地就绪。推送: git push --force $ORIGIN_URL $TREE:refs/heads/gh-pages"
fi
