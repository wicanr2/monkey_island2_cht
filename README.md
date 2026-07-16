# 猴島小英雄 II：里察克的復仇 — 繁體中文化

> Monkey Island 2: LeChuck's Revenge (1991, LucasArts) 繁體中文化專案
> 引擎：**LucasArts SCUMM v5**（ScummVM `monkey2`）。本 repo 為 **patch-only / 純資料**：只放中文譯文、字型工具與文件，**不含遊戲本體、ROM 或版權掃描**。

## 現況

- ScummVM 對 MI2 的 CJK 探勘完成（`GID_MONKEY2` 原生在 ZH_CHN 白名單，放字型即自動偵測）。
- 抽字管線：`scummtr` 支援 `monkey2`，抽出 7945 行、round-trip byte-perfect。
- **全量翻譯（7499 行）+ 第二輪校對完成並實機驗證**：63 批 sonnet 平行翻譯（統一譯名表零漂移）→ 引擎正確渲染繁中。
- **[重要] 採「純資料、零 source patch」方案**：改用全位元組 0xA1–0xFD 的 GB2312 相容碼空間（2430 字），**原版 ScummVM + 原版 scummtr 即可**，不需任何引擎/工具修改（見 [`patches/README.md`](patches/README.md)）。
- 實機：verb 介面全中文、NPC 對白正確渲染（`docs/screenshots/` 的 `playtest_verbs_10.png`、`bug_room5_fixed_after.png`）。

**待辦**：更完整的對白 playtest、CJK 斷行/對話框微調、防拷自動略過（需反組譯 room 108 腳本）、三平台打包。詳見 [`docs/計畫書-plan.md`](docs/計畫書-plan.md)。

## 做法（純資料）

1. `data/cht_table.json`：2430 個繁體字 → GB2312 相容碼（全位元組 0xA1–0xFD）的映射。
2. `tools/build_cht_font.py`：依碼表烘 `chinese_gb16x12.fnt`（12×12，WQY 點陣）。
3. `tools/cht_codec.py` + `tools/merge_and_build.py`：把 `translations/mi2_cht.tsv` 編碼成 scummtr 回填檔。
4. 原版 `scummtr -g monkey2 -rwh -A aov -if` 注入遊戲；`chinese_gb16x12.fnt` 放遊戲夾 → 原版 ScummVM 自動偵測顯示繁中。

## 目錄

```
docs/          計畫書、手冊資料、實機截圖
translations/  mi2_cht.tsv（7499 行繁中譯文，TAG+中文）
data/          cht_table.json（字↔碼映射，字型與編碼的真相）
tools/         cht_codec / build_cht_font / prep_batches / merge_and_build / build_scummvm
patches/       （空）本專案不需任何原始碼補丁
```

## 版權

原作 © 1991 LucasArts / Lucasfilm Games。本 repo 僅含中文譯文與工具（見 [`NOTICE.md`](NOTICE.md)）。ScummVM 為 GPLv3+。
