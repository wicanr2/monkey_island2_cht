#!/usr/bin/env python3
# 繁體版防拷字串注入(GBK 編碼)。驗證 Route A GBK patch 顯示繁體。
# trail byte 0x5C(='\') 撞 scummtr → 轉 '5C 5C'（Zak 解法）。CRLF 行尾。
import io

SRC = "dumps/mi2_en.txt"
OUT = "out/test-gbk/scummtr.txt"
TAG = b"[108:SCRP#0128]"

TR = {
    r"PRESS ENTER TO BEGIN LAME-O COPY PROTECTION.\255\002": r"按 ENTER 開始超遜防拷驗證。\255\002",
    r"PRESS ENTER TO TRY AGAIN.\255\002": r"按 ENTER 再試一次。\255\002",
    "WORMS": "蛔蟲", "GOUT": "痛風", "SCURVY": "壞血病", "WARTS": "肉疣",
    "TRENCH MOUTH": "戰壕口炎", "TATTOO RASH": "刺青疹", "PEG LEG ROT": "義肢腐病",
    "CHECK ONE:": "請選一項：",
}

def enc_gbk_escaped(s):
    # 逐字元：ASCII(含 \255 控制碼、ENTER)原樣不動；CJK 走 GBK 且 trail 0x5C 雙寫。
    out = bytearray()
    for ch in s:
        if ord(ch) < 128:
            out += ch.encode("latin-1")       # 反斜線保持單一 → 控制碼不壞
        else:
            for b in ch.encode("gbk"):
                out += b"\x5c\x5c" if b == 0x5c else bytes([b])
    return bytes(out)

# 驗證全部可 GBK 編碼
for v in TR.values():
    v.encode("gbk")

raw = open(SRC, "rb").read()
out = io.BytesIO(); n = 0
for ln in raw.split(b"\n"):
    ln = ln.rstrip(b"\r")
    if ln.startswith(TAG):
        body = ln[len(TAG):].decode("latin-1")
        if body in TR:
            ln = TAG + enc_gbk_escaped(TR[body]); n += 1
    out.write(ln + b"\r\n")
import os
os.makedirs("out/test-gbk", exist_ok=True)
open(OUT, "wb").write(out.getvalue())
print(f"繁體注入 {n} 條 → {OUT}")
