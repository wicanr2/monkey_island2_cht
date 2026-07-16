# 猴島小英雄 II：里察克的復仇 — 繁體中文化計畫書

> Monkey Island 2: LeChuck's Revenge (1991, LucasArts) — ScummVM patch-only 繁中化
> 本檔為探勘後的技術計畫。引擎軌 = **LucasArts SCUMM v5**，非 Sierra AGI/SCI（與 CLAUED.md 原模板 ③④⑦ 不同軌）。
> 探勘日期基準：2026-07-16；ScummVM 原始碼版本 2026.2.1git（commit cb8802d6）。

## 0. 一句話結論

ScummVM **原生已能顯示 MI2 中文**（簡體 GB / 12×12，`GID_MONKEY2` 已在白名單），但你要的**繁體 Big5（ZH_TWN / 16×15）目前被 gate 在 SCUMM v7+**，MI2 是 v5 → 需 patch 引擎放行。當年 **FM-Towns 日版 MI2 就是 v5 native 繪 16×16 漢字**（`charset.cpp:71`），證明 v5 的雙位元組繪字管線現成可用——這是繁中路線的最強支撐。

---

## 1. 遊戲與素材現況

| 項目 | 內容 |
|---|---|
| 版本 | SCUMM **v5**、DOS floppy、VGA 256 色、320×200 |
| 遊戲檔 | `MONKEY2.000`(索引 11KB) + `MONKEY2.001`(資料 9MB) + `MONKEY2.EXE` |
| gameid（ScummVM / scummtr）| `monkey2` |
| 語音 | **無**（floppy 版純文字，非 talkie；不涉 rulebook 84 對齊兩版） |
| 音樂 | AdLib(`ADLIB.IMS`) + **MT-32(`ROLAND.IMS`)**；ROM 兩顆已隨附 |
| 防拷 | **"Mix 'N' Mojo" 巫毒配方比例轉盤**（非初代的 Dial-A-Pirate）；**實測 ScummVM 顯示「LAME-O COPY PROTECTION」簡化版轉盤畫面**（非完全略過，PoC 時確認能否自動過關 / 是否 hook） |
| 手冊 | 30 張 JPG 掃描 + 軟體世界中文補完 → 已整理成 `docs/手冊-manual.md` |

素材位置：`workplace/original/`（不動的快照）、`workplace/working/mi2/`（工作副本）。

---

## 2. 探勘結論（對現行 ScummVM 原始碼實查，非憑舊筆記）

### 2.1 ScummVM 的 SCUMM CJK 現況（`engines/scumm/charset.cpp`）

進入 CJK 字型載入的語言 gate（`loadCJKFont`, 約 line 103-105）：

```cpp
} else if (_language == Common::KO_KOR ||
           (_game.version >= 7 && (_language == Common::JA_JPN || _language == Common::ZH_TWN)) ||
           (_game.version >= 3 && _language == Common::ZH_CHN)) {
```

| 語言 | 字型檔 | 尺寸 | numChar | 版本 gate | MI2(v5) 能用? |
|---|---|---|---|---|---|
| **ZH_TWN**(繁/Big5) | `chinese.fnt` | 16×15 | 13630 | **v≥7** | ❌ 需 patch |
| **ZH_CHN**(簡/GB) | `chinese_gb16x12.fnt` | 12×12 | 8178 | v≥3 | ✅ 現成 |

- `GID_MONKEY2` **已明文列在 ZH_CHN 白名單**（line 125）。
- ZH_TWN 的 index 公式（line 266-301）是 The Dig / COMI 共用的 Big5→字模 offset 對照（含 base 392820/162030 等分段），與 ZH_CHN 的 GB2312 EUC 公式（`(lead-0xa1)*94+(trail-0xa1)`, line 304）不同。
- 繪字尺寸：ZH_TWN 走 `_2byteWidth=16 / _2byteHeight=15`；ZH_CHN 走 12/12。

### 2.2 FM-Towns / PC-98 native CJK 參考（使用者指定要參考）

`charset.cpp` 內 LucasArts 當年硬體級 CJK 的三條 native 路徑，證明 v5 引擎能繪雙位元組：

| 路徑 | 條件(charset.cpp) | 字型來源 | 尺寸 | 手法 |
|---|---|---|---|---|
| **FM-Towns v3/v5 漢字** | line 71：`version<=5 && FMTowns && JA_JPN` | **`FMT_FNT.ROM`**（FontSJIS） | 16×16 | `_textSurfaceMultiplier=2` dual-layer（拉畫布） |
| PC-Engine LOOM | line 83：`LOOM && PCEngine && JA_JPN` | `pce.cdbios` System Card | 12×12 | ShadowRight |
| SegaCD 猴島1 / Indy4 日版 | line 94 | 遊戲內 charset 資源 | 16×16 | 稍後載入 |

**啟示**：native 16×16 雙位元組 + dual-layer（`_textSurfaceMultiplier=2`）是原廠做法（rulebook 81「拉畫布不縮字」的引擎級前例）。ZH_TWN 的 16×15 走的是一般 framebuffer 2byte 路徑（非 dual-layer），較不侵入。

### 2.3 抽字管線（scummtr 0.6.0，已編、已驗）

- scummtr 原生支援 `monkey2`（偵測檔 `MONKEY2.000`、pattern `MONKEY2.%.3u`）。
- 抽字 `-of` 得 **7945 行 / 495KB** 英文；**round-trip byte-perfect**（dump→import→dump diff 無輸出）。
- 字串型別分佈：

| 型別 | 行數 | 含義 |
|---|---|---|
| LSCR | 4281 | room 內嵌腳本對白/敘述（主體） |
| SCRP | 1736 | 全域腳本字串 |
| VERB | 1144 | 動詞回應 / 招牌文字 |
| OBNA | 716 | 物件名（`@@@` padding） |
| ENCD/EXCD | 68 | 進出場腳本 |

- 含對白控制碼 `\255` 的行：1078。SCUMM 控制碼速查見 Zak SKILL.md（`\255\001`=換行、`\255\003`=等 click、`\255\006/007`=插物件/actor 名）。
- 檔案含 Windows-1252 高位元組 → `grep` 要加 `-a`（同 Big5 譯文）。

---

## 3. 路線決策（繁中：Route A vs B）

| | **Route A：GBK-on-ZH_CHN** | **Route B：patch ZH_TWN 放行 v5**（建議） |
|---|---|---|
| 顯示 | 12×12 GB 字模 | 16×15 Big5 字模 |
| 引擎改動 | patch line 304 GB2312→GBK 線性 index + 擴字型到 23940 | patch line 104 gate 放 v5（或列 GID_MONKEY2）走 ZH_TWN |
| 譯文編碼 | UTF-8→**GBK** + 0x5C escape（繁字撞 `\`）+ CRLF | UTF-8→**Big5** + 0x5C escape + CRLF |
| 字型 | 自烘 GBK 12×12（Zak 已有 `build-zh-font` 系列可複用） | 自烘 Big5 16×15，需符合 line 266-301 的分段 offset 佈局 |
| 前例 | **Zak(v3) 已跑通**（本 kb 有完整 patch 清單） | 需驗證，但 index 公式與 chinese.fnt 格式引擎已定義 |
| 可讀性 | 12×12 繁體筆畫易糊（Zak 實測要挑 WQY Sharp 點陣字） | 16×15 較清晰，繁體適用 |
| 風險 | 小（照抄 Zak） | 中（Big5 字型佈局要對齊引擎 offset 公式；先做 1 字驗證） |

**修訂建議（探勘後翻轉）：先走 Route A，Route B 列為日後升級。**

> **離線探針結論**（`tools/probe_zhtwn_offset.py`，2026-07-16）：把 charset.cpp:266-301 的 ZH_TWN offset 公式移植成 Python，對整個 Big5 範圍檢查——**兩種位元組序都大量越界+碰撞**（`base` 衝到 1,612,530，但字型檔配置僅 408,900 bytes；界內僅 6020/13502、碰撞 5956）。代表這份 `chinese.fnt` 是 The Dig / COMI 的**特製佈局**（半形 ×5、全形 ×30 混合、分段 base），**無法只看 C++ 憑空正確烘出**。要走 Route B，得先取得原版 DIG/COMI 的 `chinese.fnt` 當 oracle 反推真實 geometry ＝ 一個獨立逆向子專案。
>
> 因此 **Route A（GB/GBK 12×12）為主線**：Zak 專案已端到端驗證（字型 generator、GB2312→GBK-linear index patch、0x5C escape、scummtr 命令全都有現成）。繁體透過 GBK 編碼 + patch line 304 成 GBK-linear index + 烘 GBK 全 range 字型（Zak 的 `build-zh-font-gbk.py` / WQY Sharp 點陣可複用）。**Route B（Big5 16×15 較清晰）待日後取得原版 chinese.fnt 再評估。**

> 兩路都會遇到 **scummtr 對 CJK 的 0x5C(`\`) trail byte escape**（Zak 已解：trail 0x5C → `5C 5C`）與 **0xFE/0xFF lead 撞 SCUMM escape**（Zak patch `string.cpp` drawString + scummtr funcLenSafe）。這些 v3 的解法要在 v5 上重驗（v5 的 escape 常數可能不同）。

---

## 4. 工作分解（後續 sprint）

1. **[主 session] 引擎 PoC**：Route B patch（gate + 單字 Big5 字型驗證）→ 實機截圖確認繁體正確顯示。踩坑則轉 Route A。
2. **[主 session] 字型生成器**：Big5 16×15 烘字（對齊 charset.cpp line 266-301 offset 佈局）；字表由譯文 value 決定覆蓋（CLAUED.md ④）。
3. **[sonnet subagent 平行] 翻譯**：7945 行分批 fan-out（`workflows/batch-subagent-localization.md`）；統一譯名表（Guybrush/LeChuck/Elaine 等，對照現代通行譯名）；台式幽默在地化（MI2 對白瘋趣，rulebook 80/90）。
4. **[主 session] 防拷**：確認 ScummVM 預設已略過 Mix 'N' Mojo；必要時 hook。
5. **[主 session] 音樂**：MT-32 預設（CLAUED.md ⑤，ROM 已隨附，full 版附、patch 版不附）。
6. **[sonnet subagent] 打包**：每平台雙軌 patch(→Release)+full(→本機)（CLAUED.md ⑥）；macOS 走 CI。
7. **[已完成] 手冊 markdown**（`docs/手冊-manual.md`）+ 待寫 README（圖文並茂 + 中文手冊要點索引 + 當年中文資料引言，rulebook 80）。
8. **[主 session] 回填修訂 CLAUED.md**：③④⑦ 改寫成 SCUMM 軌（本計畫確定做法後）。

---

## 5. 風險與待確認

- **[開放決策] Route A vs B**：建議 B（繁體 16×15），需使用者拍板。
- **Big5 chinese.fnt 佈局**：line 266-301 的分段 offset 是為 DIG/COMI 的 Big5 字型烘的；自烘要逐字驗證 index→offset 對得上（先單字 PoC）。
- **v5 escape 常數**：Zak 的 `string.cpp` 0xFE 跳過 patch 是 v≤6 條件，v5 適用但要實機驗 emoji/控制碼邊際 case。
- **「畫面放大 640×480」**：SCUMM 是 320×200 內部畫布，640×480 只是輸出 scaler，**不會**給字型更多內部空間（與 AGI 的 forceHires 不同）——16×15 字須塞進 320×200（約 20 字/行，夠用）。CLAUED.md 第 6 條的 forceHires 假設對 SCUMM 不成立，回填時要更正。
- **對外動作**（GitHub push / Release）一律先取得使用者確認（CLAUED.md 邊界）。

---

## 5.5 Route A PoC 結果（2026-07-16，已驗證）

**用現行 baseline binary（零引擎 patch）成功在 MI2 顯示中文。**

- 流程：烘 `chinese_gb16x12.fnt`(GB2312/WQY 12×12) → 放進遊戲夾 → ScummVM 自動偵測 **`(SE/Chinese (Simplified))`** → scummtr `-rwh` 注入防拷畫面病名 GB2312 譯文 → headless 截圖。
- 結果：防拷畫面 `RECIPE FOR 蛔虫:`（WORMS→蛔虫）**中文正確渲染**（12×12，證據 `docs/screenshots/poc_zhcn_copyprotect.png`）。
- 證明：MI2(v5) DOS 走 ScummVM ZH_CHN 2-byte 路徑無礙、字型自動偵測、scummtr+GB2312+WQY 全鏈路打通。**Route A 成立。**
- 待辦（繁體升級）：改 GBK 編碼 + patch charset.cpp:304 GB2312→GBK-linear index + 烘 GBK 全 range 字型（Zak 已有做法），需一次重編。
- 已知限制：**MI2 DOS 防拷 ScummVM 只對 Mac 平台自動略過**（`scumm.cpp:1749`），DOS 版要嘛答題、要嘛自行 hook `_copyProtection`/`o5_pickupObject` 相關流程 → 列入 PoC 後的引擎任務。

## 6. 已建立的環境（本 session 產出）

```
workplace/
├── original/mi2/           遊戲快照（不動）
├── original/manual/        手冊掃描（30 JPG + 補完 txt）
├── working/mi2/            工作副本（scummtr round-trip 驗證用，已還原）
├── tools/
│   ├── scummvm-src/        乾淨 baseline 2026.2.1（含 scummvm binary，容器內編）
│   ├── scummtr-src/        scummtr 0.6.0 已編（build/bin/{scummtr,scummrp,scummfont}）
│   ├── build_scummvm.sh    docker 編 ScummVM（scumm 引擎 + MT-32）
│   └── capture.sh          headless 截圖
├── dumps/                  抽字 dump（待放 mi2_en.txt）
├── docs/
│   ├── 手冊-manual.md      已完成
│   └── 計畫書-plan.md      本檔
└── out/shots/              baseline 截圖
```
