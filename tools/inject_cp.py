#!/usr/bin/env python3
# 翻譯 MI2 防拷畫面([108:SCRP#0128])的無控制碼文字為 GB2312 簡體，驗證中文渲染。
# 保留所有 \255.. 控制碼位元組不動；CRLF 行尾。
import io

SRC = "dumps/mi2_en.txt"
OUT = "out/test-gb/scummtr.txt"
TAG = b"[108:SCRP#0128]"

TR = {
    "PRESS ENTER TO BEGIN LAME-O COPY PROTECTION.": "按 ENTER 开始超逊防拷验证。",
    "PRESS ENTER TO TRY AGAIN.": "按 ENTER 再试一次。",
    "WORMS": "蛔虫",
    "GOUT": "痛风",
    "SCURVY": "坏血病",
    "WARTS": "肉疣",
    "TRENCH MOUTH": "战壕口炎",
    "TATTOO RASH": "刺青疹",
    "PEG LEG ROT": "义肢腐病",
    "CHECK ONE:": "请选一项：",
}
# 先確認全部可 GB2312 編碼
for k, v in TR.items():
    v.encode("gb2312")  # 失敗即丟例外

raw = open(SRC, "rb").read()
out = io.BytesIO()
n = 0
for ln in raw.split(b"\n"):
    ln = ln.rstrip(b"\r")
    if ln.startswith(TAG):
        body = ln[len(TAG):].decode("latin-1")
        if body in TR:
            ln = TAG + TR[body].encode("gb2312")
            n += 1
    out.write(ln + b"\r\n")
open(OUT, "wb").write(out.getvalue())
print(f"翻譯 {n} 條防拷字串 → {OUT}")
