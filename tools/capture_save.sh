#!/bin/bash
# 載入原版存檔跳過防拷，截圖看介面動詞是否顯示中文。
set -e
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
Xvfb :99 -screen 0 640x480x24 >/tmp/xvfb.log 2>&1 &
sleep 2
mkdir -p /out/shots
# 有 chinese_gb16x12.fnt → 自動 ZH_CHN。載 save-slot 1 跳過防拷。
timeout 55 /scummvm/scummvm --path=/game --auto-detect \
    --save-slot=1 --no-fullscreen 2>/tmp/sv.log &
SV=$!
sleep 6
# 保險：送幾個 Enter/空白鍵（若停在選單或防拷）
for k in Return space Return; do xdotool key --clearmodifiers $k 2>/dev/null || true; sleep 1; done
for t in 08 14 20 28 36 44 52; do
  sleep 3
  import -window root /out/shots/gb_${t}s.png 2>/dev/null || true
done
kill $SV 2>/dev/null || true
echo "=== sv.log ==="; grep -aiE "error|save|language|chinese|ZH|detect|slot" /tmp/sv.log | tail -15
