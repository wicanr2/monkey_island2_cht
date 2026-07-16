#!/usr/bin/env python3
# 合併翻譯批次 → 逐行驗證(TAG/控制碼) → 產出 GBK 回填檔。
# 用法:
#   python3 tools/merge_and_build.py check     # 只驗證所有 .done，不輸出
#   python3 tools/merge_and_build.py build     # 驗證 + 產出 dumps/scummtr_cht.txt (GBK)
import re, sys, glob, io

SRC = "dumps/mi2_en.txt"
BDIR = "dumps/batches"
OUT = "dumps/scummtr_cht.txt"
PER = 120

tag_re  = re.compile(rb'^(\[[0-9]+:[A-Z]{4}#[0-9]+\])(.*)$', re.S)
ctrl_re = re.compile(rb'\\255\\[0-9]+|\\254\\[0-9]+')

def visible(body):
    t = ctrl_re.sub(b'', body.split(b'@')[0])
    return t.replace(b'\\255', b'').replace(b'\\254', b'').strip()

def translatable(body):
    v = visible(body)
    return len(v) >= 2 and sum(1 for c in v if chr(c).isalpha()) >= 2

def ctrlcount(body):
    return len(ctrl_re.findall(body))

import cht_codec
_CH2CODE = cht_codec.load_table()
def enc_gbk(txt_bytes):
    # 改用 cht_codec 自訂碼(全位元組 0xA1-0xFD，無 ASCII 碰撞)。名稱沿用。
    return cht_codec.encode_line(txt_bytes.decode('utf-8'), _CH2CODE)

# 原 dump 全行 + 可譯行的 (tag,body) 序列
raw = open(SRC, 'rb').read()
orig_lines = raw.split(b'\n')
trans_seq = []
for ln in orig_lines:
    m = tag_re.match(ln.rstrip(b'\r'))
    if m and translatable(m.group(2)):
        trans_seq.append((m.group(1), m.group(2)))

# 載入 .done（照 batch 序）
files = sorted(glob.glob(f'{BDIR}/batch_*.done'))
done = []
for f in files:
    for ln in open(f, 'rb').read().split(b'\n'):
        ln = ln.rstrip(b'\r')
        if ln.strip():
            done.append((f, ln))

# 驗證：done 序 應對齊 trans_seq
errs = []
if len(done) != len(trans_seq):
    errs.append(f'總行數不符: done={len(done)} 可譯={len(trans_seq)}')
n = min(len(done), len(trans_seq))
tr_body = {}     # position i → translated body bytes
for i in range(n):
    f, dl = done[i]
    otag, obody = trans_seq[i]
    if b'\t' not in dl:
        errs.append(f'{f} 行{i}: 無 TAB'); continue
    dtag, dbody = dl.split(b'\t', 1)
    if dtag != otag:
        errs.append(f'{f} 行{i}: TAG 不符 {dtag.decode()}!={otag.decode()}'); continue
    if ctrlcount(obody) != ctrlcount(dbody):
        errs.append(f'{f} 行{i} {otag.decode()}: 控制碼 {ctrlcount(obody)}->{ctrlcount(dbody)}')
    try:
        dbody.decode('utf-8').encode('gbk')
    except Exception as e:
        errs.append(f'{f} 行{i} {otag.decode()}: GBK 打不出 {e}')
    tr_body[i] = dbody

print(f'可譯 {len(trans_seq)} 行, .done {len(done)} 行, 問題 {len(errs)}')
for e in errs[:30]:
    print('  ', e)

if sys.argv[1] == 'build':
    if errs:
        print('有問題，未輸出。先修正。'); sys.exit(1)
    # 逐行重建：可譯行換 GBK 譯文，其餘原樣
    pos = 0
    out = io.BytesIO()
    for ln in orig_lines:
        l = ln.rstrip(b'\r')
        m = tag_re.match(l)
        if m and translatable(m.group(2)):
            out.write(m.group(1) + enc_gbk(tr_body[pos]) + b'\r\n')
            pos += 1
        else:
            out.write(l + b'\r\n')
    open(OUT, 'wb').write(out.getvalue())
    print(f'輸出 {OUT} ({len(out.getvalue())} bytes, 換 {pos} 行)')
