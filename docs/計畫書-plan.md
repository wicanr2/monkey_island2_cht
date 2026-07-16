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

### Route A 繁體(GBK) 驗證（2026-07-16，已完成 ✅）

- **patch**（`patches/0001-scumm-mi2-gbk-traditional-chinese.patch`，gate 於 `GID_MONKEY2`）：`charset.cpp` numChar 8178→**23940**、`get2byteCharPtr` GB2312 EUC index→**GBK 線性**（`(idx%256-0x81)*190 + adj(idx/256)`，與字型 generator `build_gbk_font.py` 同構）。
- 字型：`build_gbk_font.py` 烘 GBK 23940 字 12×12（574560 bytes）。注入用 `inject_cp_gbk.py`（GBK 編碼 + trail 0x5C 雙寫 + `\255` 控制碼保留 + CRLF）。
- 結果：`RECIPE FOR 義肢腐病:`（PEG LEG ROT）**繁體正確渲染**（義/腐 為繁體字形，證據 `docs/screenshots/poc_zhtwn_traditional_gbk.png`）。**Route A 繁體全鏈路成立。**
- 尚未驗：0xFE lead 撞 SCUMM v≤6 escape（罕見繁字）、CJK auto-wrap 長句斷行、對話框高度——待實機走進遊戲對白時驗（rulebook 60 迭代）。
- 已知限制：**MI2 DOS 防拷 ScummVM 只對 Mac 平台自動略過**（`scumm.cpp:1749`），DOS 版要嘛答題、要嘛自行 hook `_copyProtection`/`o5_pickupObject` 相關流程 → 列入 PoC 後的引擎任務。

## 5.6 全量翻譯（2026-07-16，已完成端到端 ✅）

- **切批**：`prep_batches.py` → 7499 可譯行 / 63 批（跳過 446 純控制碼/短字串）。共用指令+統一譯名表 `dumps/INSTRUCTIONS.md`。
- **fan-out**：Workflow 編排 62 批 + 試作 1 批，sonnet subagent 平行（62/62 成功）。風格＝適度台式瘋趣、現代通行+經典混合譯名、全中文化（含介面動詞/物件名）。
- **驗證**（`merge_and_build.py`）：逐行核對 TAG 一致 + 控制碼數不變 + GBK 可編。攔到並修正：batch_042 整批誤存 GBK（轉 UTF-8）、batch_004 一行掉控制碼。**全域譯名掃描零漂移**（里察克 99、蓋布拉許 136 等只有正規譯法）。
- **[HARD] CJK-SCUMM escape 碰撞根因與修法**：GBK 中文的 **trail byte 0xFE** 撞 SCUMM v≤6 的 0xFE escape（0xFF 零筆、lead=0xFE 零筆）。**引擎端無需 patch**（CJK 字 lead 0x81–0xFD 走 charset.cpp:881 分支會一起吃掉 trail 0xFE；真 `\254` escape 由 865 處理）。**只需 patch scummtr**（`patches/0002`）：`funcLen` 未知 id 回 −1、偵測點「0xFE 只有後接合法 function id(1–14) 才當 escape，否則是 trail byte」——真 `\254` 一定接合法 id，CJK trail 後面接 lead(0x81+)/ASCII 絕不是 1–14，精準消歧且 byte-exact。
- **端到端**：全量注入成功（MONKEY2.001 9080329→9142845），防拷畫面整段繁中乾淨渲染（`疣 的配方`/`幾滴木腿亮光劑 混合`/`搖勻`，證據 `docs/screenshots/poc_full_translation_ingame.png`）。**7499 行全量譯文在引擎正確顯示。**
- 尚未驗：走進遊戲的真實 NPC 對白（防拷擋住 headless）、CJK auto-wrap 長句斷行、對話框高度、字距美感——列為 playtest 里程碑。

## 5.7 Playtest / 防拷 / 第二輪校對（2026-07-16）

- **[實機 playtest]** `--boot-param=<房號>` 直接進遊戲房間跳過防拷（room 4=夜晚岩岸）。實測：**verb 介面全中文渲染完美**（給予/拿起/使用/打開/查看/推/關閉/交談/拉/走到，清晰對齊無殘影，`docs/screenshots/playtest_verbs_10.png`）；多行訊息框 CJK 斷行由防拷畫面驗證（3 行置中正確）。**未完成**：in-game NPC 疊字對白（盲座標點擊難穩定觸發，game tester subagent 亦卡此）→ 建議真人玩或更精準的自動化補驗。
- **[#2 防拷自動略過]** 現況：**ScummVM 已停用防拷「檢查」**（`scumm.cpp:4287`），但實測輸入部分答案（"99"）**未過關** → DOS 版仍需完整/正確答案，非「隨便填即過」。Mac 靠 size-keyed boot-script patch 跳過（`resource.cpp`），DOS 無對應。**正解＝反組譯 room 108 防拷腳本（`SCRP_0128–0136`，boot script `SCRP_0001` 6916 bytes）後 patch**，需 descumm 反組譯器，屬**聚焦深水 RE follow-up**，非快速 win（未動手，避免 rulebook 41 硬鑽）。互動可先用 `--boot-param` 跳過。
- **[第二輪校對]** 63 批 sonnet 審修（Workflow），**176 行修訂（2%）**，逐行驗證 0 問題（TAG/控制碼/GBK）。改善例：臭鼬鼠→黃鼠狼、炸成碎片→粉身碎骨、黃色笑話→黃色歌曲（語境）、修好掉字的 `^` 控制碼。已升為定稿、重注入（MONKEY2.001 9142282）。

## 5.8 [重大] 渲染損毀根治 → 改「純資料、零 source patch」方案（2026-07-16）

**Bug**（game tester 揪出、逐字核實）：房 5 篝火 NPC 對白出現**字元級損毀**——「這倒提醒我了」顯示成「叩因嵼盐伊軌」，同行後半正確。

**根因**（逐位元組追出）：注入 byte-exact，問題在引擎。GBK 的 **trail byte 落在 0x40–0x7E**（如「這」=`df40`，trail `0x40`='@'）：① `0x40`='@' 撞 scummtr padding、`0x5C`='\' 撞 escape；② 更關鍵——ScummVM 的 SCUMM CJK 組雙位元組字**假設 trail ≥ 0x80**（upstream 只跑 GB2312，trail 都 0xA1–0xFE），trail<0x80 的字組不出來 → 錯位損毀。逐站 patch 引擎會沒完沒了（rulebook 41）。

**乾淨修法**：改用**全位元組 0xA1–0xFD 的 GB2312 相容自訂碼空間**——譯文只有 2430 個不重複中文字，映射進 0xA1–0xFD×0xA1–0xFD（`tools/cht_codec.py` 碼表），字型依 `idx=(lead-0xa1)*94+(trail-0xa1)` 烘（`tools/build_cht_font.py`），**直接用 upstream GB2312 公式**。一舉消除 0x40/0x5C/0xFE/低 trail 全部碰撞。

**結果 = 純資料方案，零 source patch**：
- **charset.cpp 完全回 upstream**（`git diff` 空）——原版 ScummVM 就能跑（`GID_MONKEY2` 本在 ZH_CHN 白名單）。**撤除 patch 0001（GBK 引擎）與 GBK index 公式。**
- **scummtr 也回 pristine**——未 patch 版成功注入（全 0xA1–0xFD 無 escape 碰撞）。**撤除 patch 0002。**
- 交付物 = 自訂 `chinese_gb16x12.fnt`（2430 字，`cht_table.json` 為映射真相）+ 編碼譯文。
- 驗證：房 5 對白「這倒提醒我了,我們還有沒有剩熱狗?」**完全正確**（`docs/screenshots/bug_room5_fixed_after.png` vs `bug_room5_corrupt_before.png`）。無回歸（原本正確的高-trail 字重映射後仍高位元組）。

> 教訓：CJK-in-SCUMM 別直接套 GBK（低 trail 撞引擎/工具的 ASCII 假設）；用 GB2312 結構的高位元組碼空間 + 自訂字型，反而零改動最穩。

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
