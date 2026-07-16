#!/usr/bin/env python3
# 依 cht_codec 碼表烘 chinese_gb16x12.fnt(12x12)。
# idx=(lead-0xa1)*94+(trail-0xa1)，與 upstream ScummVM ZH_CHN 公式一致，numChar=8178。
import sys
from PIL import Image, ImageFont, ImageDraw
import cht_codec

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
OUT = sys.argv[1] if len(sys.argv) > 1 else "chinese_gb16x12.fnt"
W = H = 12
ROWBYTES = (W + 7) // 8   # 2
NUMCHAR = 8178
font = ImageFont.truetype(FONT_PATH, 12)
buf = bytearray(NUMCHAR * ROWBYTES * H)

ch2code = cht_codec.load_table()

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

n = 0
for ch, (lead, trail) in ch2code.items():
    idx = (lead - 0xa1) * 94 + (trail - 0xa1)
    if not (0 <= idx < NUMCHAR):
        continue
    g = render(ch)
    off = idx * ROWBYTES * H
    buf[off:off + len(g)] = g
    n += 1

open(OUT, "wb").write(buf)
print(f"寫出 {OUT}: {len(buf)} bytes, 烘 {n} 字")
