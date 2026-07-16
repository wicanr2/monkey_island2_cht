#!/usr/bin/env python3
# 一鍵套用：把 repo 的繁中譯文(translations/mi2_cht.tsv) + 碼表(data/cht_table.json)
# 套到指定 MI2 遊戲夾——抽字→逐行對位換譯文(GB2312 相容碼)→產出 scummtr 回填檔。
# 另需 scummtr 注入(見 build_release.sh)。可完全從本 repo 重現，不依賴 .done 批次檔。
#
# 用法: python3 apply_cht.py <scummtr路徑> <遊戲夾> [輸出回填檔]
import sys, os, re, subprocess, io, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(REPO, "translations", "mi2_cht.tsv")
TABLE = os.path.join(REPO, "data", "cht_table.json")
PERROW, LEAD0, TRAIL0 = 93, 0xA1, 0xA1

tag_re = re.compile(rb'^(\[[0-9]+:[A-Z]{4}#[0-9]+\])(.*)$', re.S)
ctrl_re = re.compile(rb'\\255\\[0-9]+|\\254\\[0-9]+')

def translatable(body):
    t = ctrl_re.sub(b'', body.split(b'@')[0]).replace(b'\\255', b'').replace(b'\\254', b'').strip()
    return len(t) >= 2 and sum(1 for c in t if chr(c).isalpha()) >= 2

def load_codec():
    chars = json.load(open(TABLE, encoding="utf-8"))["chars"]
    return {ch: (LEAD0 + i // PERROW, TRAIL0 + i % PERROW) for i, ch in enumerate(chars)}

def encode(s, ch2code):
    out = bytearray()
    for ch in s:
        if ord(ch) < 128:
            out += ch.encode("latin-1")
        elif ch in ch2code:
            out += bytes(ch2code[ch])
        else:
            out += b'?'
    return bytes(out)

def main():
    scummtr, game = sys.argv[1], sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) > 3 else os.path.join(game, "scummtr_cht.txt")
    # 1. 抽該遊戲英文 dump
    dump = os.path.join(game, "_en_dump.txt")
    subprocess.run([scummtr, "-g", "monkey2", "-cwh", "-A", "aov", "-of", dump],
                   cwd=game, check=True, stdout=subprocess.DEVNULL)
    raw = open(dump, "rb").read()
    orig_lines = raw.split(b"\n")
    # 2. 讀譯文 tsv(TAG<TAB>中文)，順序 = 可譯行順序
    tsv = [l.rstrip(b"\r") for l in open(TSV, "rb").read().split(b"\n") if l.strip()]
    tsv_tag, tsv_zh = [], []
    for l in tsv:
        t, z = l.split(b"\t", 1)
        tsv_tag.append(t); tsv_zh.append(z)
    # 3. 逐行對位 + 驗 TAG
    ch2code = load_codec()
    out = io.BytesIO(); pos = 0; bad = 0
    for ln in orig_lines:
        l = ln.rstrip(b"\r")
        m = tag_re.match(l)
        if m and translatable(m.group(2)):
            if pos >= len(tsv_zh):
                bad += 1; out.write(l + b"\r\n"); continue
            if m.group(1) != tsv_tag[pos]:
                bad += 1  # TAG 不符(遊戲版本不同?) → 保留英文
                out.write(l + b"\r\n"); pos += 1; continue
            enc = encode(tsv_zh[pos].decode("utf-8"), ch2code)
            out.write(m.group(1) + enc + b"\r\n"); pos += 1
        else:
            out.write(l + b"\r\n")
    open(out_file, "wb").write(out.getvalue())
    os.remove(dump)
    print(f"套用 {pos}/{len(tsv_zh)} 行譯文, TAG 不符 {bad}, → {out_file}")
    if pos != len(tsv_zh) or bad:
        print("⚠ 行數/TAG 不完全吻合，可能遊戲版本不同(本專案基於 floppy VGA MONKEY2.000)")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
