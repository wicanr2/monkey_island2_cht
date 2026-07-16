#!/usr/bin/env python3
# 切批 + 過濾：把 scummtr dump 分成「可譯」與「跳過」，可譯者切批。
# 格式: [room:TYPE#id]text  → key=[..] 不可變, text 才翻。@@@ 是 padding。
import re, os, io, json

SRC = "dumps/mi2_en.txt"
BATCH_DIR = "dumps/batches"
PER = 120
os.makedirs(BATCH_DIR, exist_ok=True)

tag_re = re.compile(rb'^(\[[0-9]+:[A-Z]{4}#[0-9]+\])(.*)$', re.S)
ctrl_re = re.compile(rb'\\255\\[0-9]+(\\[0-9]+\\[0-9]+)?|\\254\\[0-9]+')

def visible_text(body):
    # 去 @@@ padding、去控制碼、去空白 → 剩下的可見文字
    t = body.split(b'@')[0]
    t = ctrl_re.sub(b'', t)
    t = t.replace(b'\\255', b'').replace(b'\\254', b'')
    return t.strip()

def is_translatable(body):
    vt = visible_text(body)
    if len(vt) < 2:
        return False
    # 至少含 2 個字母
    letters = sum(1 for c in vt if chr(c).isalpha())
    if letters < 2:
        return False
    return True

raw = open(SRC, "rb").read()
trans, skip = [], 0
for ln in raw.split(b"\n"):
    ln = ln.rstrip(b"\r")
    m = tag_re.match(ln)
    if not m:
        continue
    tag, body = m.group(1), m.group(2)
    if is_translatable(body):
        trans.append((tag, body))
    else:
        skip += 1

# 切批
nb = (len(trans) + PER - 1) // PER
for i in range(nb):
    chunk = trans[i*PER:(i+1)*PER]
    out = io.BytesIO()
    for tag, body in chunk:
        # 給 subagent 的底稿：TAG\t原文(含 @@@/控制碼原樣)
        out.write(tag + b"\t" + body + b"\n")
    open(f"{BATCH_DIR}/batch_{i:03d}.txt", "wb").write(out.getvalue())

print(f"可譯 {len(trans)} 行, 跳過 {skip} 行 → {nb} 批 (每批 {PER})")
print(f"批次目錄: {BATCH_DIR}/batch_000.txt .. batch_{nb-1:03d}.txt")
