# 猴島小英雄 II：里察克的復仇 — 繁體中文化（ScummVM patch）

> Monkey Island 2: LeChuck's Revenge (1991, LucasArts) 繁體中文化專案
> 引擎：**LucasArts SCUMM v5**（ScummVM `monkey2`）。本 repo 為 **patch-only**：只放中文化補丁、字型工具與文件，**不含遊戲本體、ROM 或版權掃描**。

## 現況

已完成：

- ScummVM 對 MI2 的 CJK 支援探勘（`GID_MONKEY2` 原生在 ZH_CHN 白名單；繁體 ZH_TWN 被 gate 在 v7+ 需 patch）。
- 抽字管線：`scummtr` 支援 `monkey2`，抽出 7945 行、round-trip byte-perfect。
- 繁體引擎路徑（`patches/0001`）：GBK 線性 index + numChar 23940 + GBK 字型 → 繁體上屏。
- **全量翻譯（7499 行）已完成並端到端驗證**：63 批 sonnet 平行翻譯（統一譯名表零漂移）→ CJK-aware scummtr 注入（`patches/0002`）→ 引擎正確渲染繁中（見 `docs/screenshots/poc_full_translation_ingame.png`）。譯文在 [`translations/mi2_cht.tsv`](translations/mi2_cht.tsv)。

**待辦**：走進遊戲的 NPC 對白 playtest、CJK 斷行/對話框/字距微調、防拷處理、三平台打包。詳見 [`docs/計畫書-plan.md`](docs/計畫書-plan.md)。

## 路線

- **Route A（主線）**：GBK 編碼 + patch `charset.cpp` GBK 線性 index + 烘 GBK 全 range 12×12 字型 → 繁體上屏。
- **Route B（升級）**：patch 放行 v5 走 ZH_TWN Big5 16×15，需原版 The Dig/COMI `chinese.fnt` 當 oracle 反推佈局。

## 目錄

```
docs/          計畫書、手冊資料、PoC 截圖
tools/         字型 generator、scummtr 注入、headless 截圖、offset 探針、ScummVM build
patches/       ScummVM 中文化補丁（Route A GBK patch 完成後放入）
```

## 玩家使用（規劃中）

patch 版：下載引擎 + 中文資料，自備遊戲檔（`--path` 指向你的 MI2 安裝夾）。MT-32 ROM 玩家自備。

## 版權

原作 © 1991 LucasArts / Lucasfilm Games。本 repo 僅含中文化補丁與工具（見 [`NOTICE.md`](NOTICE.md)）。ScummVM 為 GPLv3+。
