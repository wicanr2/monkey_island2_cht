#!/bin/bash
# 實機 playtest 截圖：boot 進 ROOM，循環點 verb + 點場景觸發對白/物件描述，連拍。
set -e
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
Xvfb :99 -screen 0 640x480x24 >/tmp/xvfb.log 2>&1 &
sleep 2
ROOM="${ROOM:-4}"
mkdir -p /out/shots
timeout 70 /scummvm/scummvm --path=/game --auto-detect \
    --boot-param=$ROOM --no-fullscreen --no-aspect-ratio 2>/tmp/sv.log &
SV=$!
sleep 5
shot(){ import -window root /out/shots/pt${ROOM}_$1.png 2>/dev/null||true; }
click(){ xdotool mousemove $1 $2 click 1 2>/dev/null||true; }
shot enter
# verb 介面在下方(640x480 letterbox：遊戲畫面約 y0-320，verb 區 y~360-470)
# 查看(Look at) 約在中排中；點它再點場景中央角色/物件
click 300 390; sleep 1   # 選一個 verb(查看)
for xy in "320 200" "200 230" "430 210" "300 260" "150 180" "480 240"; do
  click $xy; sleep 2; shot "look_${xy// /_}"
done
# 換 verb：拿起/打開 等，再點場景
click 130 360; sleep 1
for xy in "300 230" "250 200"; do click $xy; sleep 2; shot "act_${xy// /_}"; done
# 走動觸發
click 500 250; sleep 3; shot walk
kill $SV 2>/dev/null||true
grep -aiE "error|fatal|room" /tmp/sv.log | tail -5
ls /out/shots/pt${ROOM}_*.png 2>/dev/null | wc -l
