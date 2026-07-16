#!/bin/bash
# 一鍵重建 MI2 繁中版：烘字型 → 套譯文 → scummtr 注入到指定遊戲夾。
# 用法: ./build_release.sh <遊戲夾> [scummtr路徑]
# 需求: docker(烘字型用 PIL+WQY) 或本機 python3-pil+fonts-wqy-microhei；scummtr binary。
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
GAME="${1:?用法: build_release.sh <遊戲夾> [scummtr]}"
SCUMMTR="${2:-scummtr}"
command -v "$SCUMMTR" >/dev/null || { echo "找不到 scummtr(參數2 指定路徑)"; exit 1; }

echo "=== 1/3 烘字型 chinese_gb16x12.fnt ==="
if command -v python3 >/dev/null && python3 -c "import PIL" 2>/dev/null && \
   [ -f /usr/share/fonts/truetype/wqy/wqy-microhei.ttc ]; then
  (cd "$REPO" && PYTHONPATH="$REPO/tools" python3 "$REPO/tools/build_cht_font.py" "$GAME/chinese_gb16x12.fnt")
else
  echo "本機缺 PIL/WQY → 用 docker 烘"
  docker run --rm -v "$REPO:/repo" -v "$GAME:/game" ubuntu:24.04 bash -c '
    set -e
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq && apt-get install -y -qq python3-pil fonts-wqy-microhei >/dev/null 2>&1
    cd /repo
    PYTHONPATH=/repo/tools python3 /repo/tools/build_cht_font.py /game/chinese_gb16x12.fnt'
fi

echo "=== 2/3 套譯文 → 回填檔 ==="
python3 "$REPO/tools/apply_cht.py" "$SCUMMTR" "$GAME" "$GAME/scummtr.txt"

echo "=== 3/3 scummtr 注入 ==="
( cd "$GAME" && rm -f ./*scummio-tmp && "$SCUMMTR" -g monkey2 -rwh -A aov -if && rm -f scummtr.txt ./*scummio-tmp )

echo "=== 完成 ==="
echo "遊戲夾 $GAME 已中文化。放進 ScummVM(自動偵測 Chinese)即可玩。"
echo "MONKEY2.001: $(stat -c%s "$GAME/MONKEY2.001" 2>/dev/null) bytes; 字型: $(stat -c%s "$GAME/chinese_gb16x12.fnt" 2>/dev/null) bytes"
