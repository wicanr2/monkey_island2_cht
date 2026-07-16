#!/bin/bash
# boot-param 直接進房間，跳過防拷；截圖看中文對白。
set -e
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
Xvfb :99 -screen 0 640x480x24 >/tmp/xvfb.log 2>&1 &
sleep 2
ROOM="${ROOM:-4}"
mkdir -p /out/shots
timeout 40 /scummvm/scummvm --path=/game --auto-detect \
    --boot-param=$ROOM --no-fullscreen 2>/tmp/sv.log &
SV=$!
sleep 5
# 送幾個鍵/點擊觸發互動與對白
for k in space Return; do xdotool key $k 2>/dev/null||true; sleep 1; done
for t in 06 10 14 18 24 30; do
  sleep 3
  import -window root /out/shots/boot${ROOM}_${t}s.png 2>/dev/null||true
done
kill $SV 2>/dev/null||true
grep -aiE "error|room|boot|fatal" /tmp/sv.log | tail -8
