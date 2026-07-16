#!/bin/bash
# 容器內 headless 截圖：Xvfb + ScummVM + import。
set -e
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
Xvfb :99 -screen 0 640x480x24 >/tmp/xvfb.log 2>&1 &
sleep 2
PREFIX="${PREFIX:-mi2}"
EXTRA="${EXTRA:-}"
mkdir -p /out/shots
timeout 60 /scummvm/scummvm --path=/game --auto-detect \
    --no-fullscreen $EXTRA 2>/tmp/sv.log &
SV=$!
for t in 03 06 10 15 20 26 33 40 48; do
  sleep 3
  import -window root /out/shots/${PREFIX}_${t}s.png 2>/dev/null || true
done
kill $SV 2>/dev/null || true
echo "=== scummvm stderr tail ==="; tail -25 /tmp/sv.log
echo "=== 截圖 ==="; ls -lh /out/shots/
