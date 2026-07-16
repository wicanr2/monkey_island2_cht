#!/usr/bin/env python3
# 離線驗證 ScummVM charset.cpp ZH_TWN getCharPtr 的 offset 公式。
# 目的：判定 idx 的位元組序 + 每個 Big5 字是否 1:1 落在字型陣列界內。
# numChar=13630, glyph=30 bytes(16x15, rowBytes=2) → 檔案 = 13630*30 = 408900 bytes
NUMCHAR = 13630
GLYPH = 30
SIZE = NUMCHAR * GLYPH  # 408900

def base_of(idx):
    """逐行照抄 charset.cpp:266-301 的 ZH_TWN 分支。"""
    low = idx % 256
    high = 0
    if 0x20 <= low <= 0x7e:
        base = (3 * low + 81012) * 5
    else:
        if 0xa1 <= low <= 0xa3:
            base = 392820; low += 0x5f
        elif 0xa4 <= low <= 0xc6:
            base = 0; low += 0x5c
        elif 0xc9 <= low <= 0xf9:
            base = 162030; low += 0x37
        else:
            base = 392820; low = 0xff
        if low != 0xff:
            high = idx // 256
            if 0x40 <= high <= 0x7e:
                high -= 0x40
            else:
                high -= 0x62
            base += (low * 0x9d + high) * 30
    return base

def big5_chars():
    """(lead, trail) 全 Big5 常用+次常用範圍。"""
    for lead in range(0xa4, 0xfa):          # 常用 0xa4-0xc6, 次常用 0xc9-0xf9
        for trail in list(range(0x40, 0x7f)) + list(range(0xa1, 0xff)):
            yield lead, trail

for order_name, mk_idx in [
    ("idx=(lead<<8)|trail", lambda l, t: (l << 8) | t),
    ("idx=(trail<<8)|lead", lambda l, t: (t << 8) | l),
]:
    inb = 0; oob = 0; seen = {}; collide = 0; mn = 1 << 30; mx = -1
    for lead, trail in big5_chars():
        idx = mk_idx(lead, trail)
        b = base_of(idx)
        mn = min(mn, b); mx = max(mx, b)
        if 0 <= b <= SIZE - GLYPH:
            inb += 1
            if b in seen: collide += 1
            seen[b] = (lead, trail)
        else:
            oob += 1
    print(f"[{order_name}] 界內={inb} 越界={oob} 碰撞={collide} base範圍=[{mn},{mx}] (檔上限={SIZE-GLYPH})")
