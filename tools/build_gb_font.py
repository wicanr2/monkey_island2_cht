#!/usr/bin/env python3
# 產生 ScummVM SCUMM ZH_CHN 用的 chinese_gb16x12.fnt (GB2312, 12x12)。
# 格式(charset.cpp): numChar=8178, idx=(lead-0xa1)*94+(trail-0xa1),
#   每字 rowBytes=(12+7)//8=2, 12 rows → 24 bytes/glyph, 共 8178*24=196272 bytes。
import sys
from PIL import Image, ImageFont, ImageDraw

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
OUT = sys.argv[1] if len(sys.argv) > 1 else "chinese_gb16x12.fnt"
W = H = 12
ROWBYTES = (W + 7) // 8   # =2
NUMCHAR = 8178

font = ImageFont.truetype(FONT_PATH, 12)
buf = bytearray(NUMCHAR * ROWBYTES * H)

def render(ch):
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    # 微調基線讓 12px 字盡量填滿
    d.text((0, -1), ch, fill=255, font=font)
    px = img.load()
    glyph = bytearray(ROWBYTES * H)
    for y in range(H):
        for x in range(W):
            if px[x, y] > 96:
                glyph[y * ROWBYTES + (x >> 3)] |= (0x80 >> (x & 7))
    return glyph

count = 0
for lead in range(0xa1, 0xff):
    for trail in range(0xa1, 0xff):
        idx = (lead - 0xa1) * 94 + (trail - 0xa1)
        if idx >= NUMCHAR:
            continue
        try:
            ch = bytes([lead, trail]).decode("gb2312")
        except Exception:
            continue
        g = render(ch)
        off = idx * ROWBYTES * H
        buf[off:off + len(g)] = g
        count += 1

with open(OUT, "wb") as f:
    f.write(buf)
print(f"寫出 {OUT}: {len(buf)} bytes, 烘 {count} 字 (numChar={NUMCHAR})")
