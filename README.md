# 猴島小英雄 II：里察克的復仇 — 繁體中文化

> Monkey Island 2: LeChuck's Revenge (1991, LucasArts) 繁體中文化專案
> 引擎：**LucasArts SCUMM v5**（ScummVM `monkey2`）。本 repo 為 **patch-only / 純資料**：只放中文譯文、字型工具與文件，**不含遊戲本體、ROM 或版權掃描**。

## 現況

- ScummVM 對 MI2 的 CJK 探勘完成（`GID_MONKEY2` 原生在 ZH_CHN 白名單，放字型即自動偵測）。
- 抽字管線：`scummtr` 支援 `monkey2`，抽出 7945 行、round-trip byte-perfect。
- **全量翻譯（7499 行）+ 第二輪校對完成並實機驗證**：63 批 sonnet 平行翻譯（統一譯名表零漂移）→ 引擎正確渲染繁中。
- **[重要] 採「純資料、零 source patch」方案**：改用全位元組 0xA1–0xFD 的 GB2312 相容碼空間（2430 字），**原版 ScummVM + 原版 scummtr 即可**，不需任何引擎/工具修改（見 [`patches/README.md`](patches/README.md)）。
- 實機：verb 介面全中文、NPC 對白正確渲染（`docs/screenshots/` 的 `playtest_verbs_10.png`、`bug_room5_fixed_after.png`）。
- **選用防拷略過 patch 已完成**：DOS 版 Mix'N'Mojo 防拷可輸入任意兩數字通過；中文化本身仍是零 source patch（見 [`patches/README.md`](patches/README.md)）。
- **一鍵重建管線**：`tools/build_release.sh` 可從本 repo 的譯文與碼表，對使用者自己的 MI2 遊戲夾重建繁中版。

**待辦**：更完整的對白 playtest、CJK 斷行/對話框微調、完全零互動略過防拷畫面（選用）、三平台打包。詳見 [`docs/計畫書-plan.md`](docs/計畫書-plan.md)。

## 做法（純資料）

1. `data/cht_table.json`：2430 個繁體字 → GB2312 相容碼（全位元組 0xA1–0xFD）的映射。
2. `tools/build_cht_font.py`：依碼表烘 `chinese_gb16x12.fnt`（12×12，WQY 點陣）。
3. `tools/apply_cht.py`：從任意 MI2 遊戲夾抽英文 dump，依 `translations/mi2_cht.tsv` 與 TAG 對位產生 scummtr 回填檔。
4. `tools/build_release.sh`：一鍵編排「烘字型 → 套譯文 → scummtr 注入」，對指定遊戲夾重建繁中版。
5. 原版 `scummtr -g monkey2 -rwh -A aov -if` 注入遊戲；`chinese_gb16x12.fnt` 放遊戲夾 → 原版 ScummVM 自動偵測顯示繁中。

### 一鍵重建

```bash
# <遊戲夾> 需是你自己的 Monkey Island 2 DOS/VGA 遊戲資料夾，至少含 MONKEY2.000 / MONKEY2.001。
# <scummtr> 可省略；若不在 PATH，請指定 scummtr binary。
./tools/build_release.sh /path/to/MI2 /path/to/scummtr
```

驗證過的管線輸出會套用 7499/7499 行譯文、產生 196272 bytes 的 `chinese_gb16x12.fnt`，並以 scummtr 回填 `MONKEY2.001`。

## 目錄

```
docs/          計畫書、手冊資料、實機截圖
translations/  mi2_cht.tsv（7499 行繁中譯文，TAG+中文）
data/          cht_table.json（字↔碼映射，字型與編碼的真相）
tools/         cht_codec / build_cht_font / apply_cht / build_release / build_scummvm
patches/       選用 ScummVM patch（中文化本身不依賴）
```

## 版權

原作 © 1991 LucasArts / Lucasfilm Games。本 repo 僅含中文譯文與工具（見 [`NOTICE.md`](NOTICE.md)）。ScummVM 為 GPLv3+。
