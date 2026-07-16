#!/usr/bin/env python3
# 產生 GBK 全 range(含繁體) 12x12 字型 chinese_gb16x12.fnt (MI2 繁體用)。
# index 與引擎 charset.cpp GID_MONKEY2 分支同構：
#   idx = (b0-0x81)*190 + (b1<0x7f ? b1-0x40 : b1-0x41)    (b0=lead, b1=trail)
# 每字 rowBytes=2, 12 rows → 24 bytes/glyph; numChar=(0xfe-0x81+1)*190=23940。
import sys
from PIL import Image, ImageFont, ImageDraw

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
OUT = sys.argv[1] if len(sys.argv) > 1 else "chinese_gb16x12.fnt"
W = H = 12
ROWBYTES = (W + 7) // 8
NUMCHAR = (0xfe - 0x81 + 1) * 190   # 23940
font = ImageFont.truetype(FONT_PATH, 12)
buf = bytearray(NUMCHAR * ROWBYTES * H)

def render(ch):
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).text((0, -1), ch, fill=255, font=font)
    px = img.load()
    g = bytearray(ROWBYTES * H)
    for y in range(H):
        for x in range(W):
            if px[x, y] > 96:
                g[y * ROWBYTES + (x >> 3)] |= (0x80 >> (x & 7))
    return g

count = 0
for b0 in range(0x81, 0xff):          # lead
    for b1 in range(0x40, 0xff):      # trail
        if b1 == 0x7f:
            continue
        idx = (b0 - 0x81) * 190 + (b1 - (0x40 if b1 < 0x7f else 0x41))
        if not (0 <= idx < NUMCHAR):
            continue
        try:
            ch = bytes([b0, b1]).decode("gbk")
        except Exception:
            continue
        if not ch.strip():
            continue
        g = render(ch)
        off = idx * ROWBYTES * H
        buf[off:off + len(g)] = g
        count += 1

open(OUT, "wb").write(buf)
print(f"寫出 {OUT}: {len(buf)} bytes, 烘 {count} 字 (numChar={NUMCHAR})")
