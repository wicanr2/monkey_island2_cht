#!/usr/bin/env python3
# 把介面動詞([004:SCRP#0021])替換成 GB2312 簡體中文，產出 scummtr -r 可匯入的 bytes 檔。
# PoC 目的：驗證 MI2(v5) 走 ZH_CHN 2-byte 渲染管線。CRLF 行尾(Zak: scummtr _unEsc bug)。
import io

SRC = "dumps/mi2_en.txt"
OUT = "out/test-gb/scummtr.txt"

# 英文 → 簡體(GB2312)。只針對 [004:SCRP#0021] 的介面動詞。
VERB = {
    "Walk to": "走到", "Give": "给", "Open": "打开", "Close": "关上",
    "Pick up": "拿起", "Look at": "查看", "Talk to": "交谈",
    "Use": "使用", "Push": "推", "Pull": "拉",
}
TAG = b"[004:SCRP#0021]"

raw = open(SRC, "rb").read()
lines = raw.split(b"\n")
out = io.BytesIO()
n = 0
for ln in lines:
    ln = ln.rstrip(b"\r")
    if ln.startswith(TAG):
        body = ln[len(TAG):]
        # 取 @@@ 之前的英文
        eng = body.split(b"@")[0].decode("latin-1")
        if eng in VERB:
            pad = body[len(eng.encode("latin-1")):]  # 保留 @@@ padding
            ln = TAG + VERB[eng].encode("gb2312") + pad
            n += 1
    out.write(ln + b"\r\n")
open(OUT, "wb").write(out.getvalue())
print(f"注入 {n} 個動詞 → {OUT} ({len(out.getvalue())} bytes)")
