#!/usr/bin/env python3
# 自訂 GB2312 相容碼空間：所有位元組 0xA1-0xFD(無 0x40/0x5C/0xFE/0xFF/低 trail)。
# 每列 93 字(trail 0xA1-0xFD)，lead 0xA1 起。idx=(lead-0xa1)*94+(trail-0xa1) 與 upstream 公式一致。
# 共用模組：build_table / encode / (font gen 另檔用 char_at)。
import glob, re, json, os

TAG_RE = re.compile(r'^(\[[0-9]+:[A-Z]{4}#[0-9]+\])\t(.*)$')
# 歷史 workspace 用 dumps/cht_table.json；公開 repo 則保存於 data/cht_table.json。
# 讓工具可從任意 cwd 重現，不依賴開發機的 dumps/ 目錄。
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.environ.get("MI2_CHT_TABLE") or (
    os.path.join(_REPO, "data", "cht_table.json")
    if os.path.exists(os.path.join(_REPO, "data", "cht_table.json"))
    else os.path.join("dumps", "cht_table.json")
)
PERROW = 93          # trail 0xA1..0xFD
LEAD0 = 0xA1
TRAIL0 = 0xA1

def collect_chars():
    chars = []
    seen = set()
    for f in sorted(glob.glob("dumps/batches/batch_*.done")):
        for l in open(f, encoding="utf-8").read().split("\n"):
            m = TAG_RE.match(l)
            if not m: continue
            for ch in m.group(2):
                if ord(ch) >= 0x2e80 and ch not in seen:   # CJK 漢字/標點
                    seen.add(ch); chars.append(ch)
    return chars

def build_table():
    chars = collect_chars()
    ch2code = {}
    for i, ch in enumerate(chars):
        lead = LEAD0 + i // PERROW
        trail = TRAIL0 + i % PERROW
        assert lead <= 0xFD, f"字太多，lead 溢出: {i}"
        ch2code[ch] = (lead, trail)
    json.dump({"chars": chars}, open(TABLE, "w", encoding="utf-8"), ensure_ascii=False)
    return ch2code

def load_table():
    chars = json.load(open(TABLE, encoding="utf-8"))["chars"]
    return {ch: (LEAD0 + i // PERROW, TRAIL0 + i % PERROW) for i, ch in enumerate(chars)}

def encode_line(s, ch2code):
    # s: 譯文(含字面 \255 控制碼)。ASCII 原樣；CJK 走自訂碼(兩 byte 皆 0xA1-0xFD)。
    out = bytearray()
    for ch in s:
        if ord(ch) < 128:
            out += ch.encode("latin-1")
        elif ch in ch2code:
            lead, trail = ch2code[ch]
            out += bytes([lead, trail])
        else:
            out += b'?'   # 表外字(理論上不會有)
    return bytes(out)

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "build":
        t = build_table()
        print(f"建表: {len(t)} 字, lead {LEAD0:#x}..{LEAD0 + (len(t)-1)//PERROW:#x}, 全位元組 0xA1-0xFD")
