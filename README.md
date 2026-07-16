# 猴島小英雄 II：里察克的復仇 — 繁體中文化（ScummVM patch）

> Monkey Island 2: LeChuck's Revenge (1991, LucasArts) 繁體中文化專案
> 引擎：**LucasArts SCUMM v5**（ScummVM `monkey2`）。本 repo 為 **patch-only**：只放中文化補丁、字型工具與文件，**不含遊戲本體、ROM 或版權掃描**。

## 現況

本專案處於**探勘＋環境建置**階段。已完成：

- ScummVM 對 MI2 的 CJK 支援探勘（`GID_MONKEY2` 原生在 ZH_CHN 白名單；繁體 ZH_TWN 被 gate 在 v7+ 需 patch）。
- 抽字管線驗證：`scummtr` 支援 `monkey2`，抽出 7945 行、round-trip byte-perfect。
- **PoC：零引擎 patch 顯示中文**——放 `chinese_gb16x12.fnt` 即自動偵測 ZH_CHN，簡體中文正確渲染（見 `docs/screenshots/poc_zhcn_copyprotect.png`）。

詳見 [`docs/計畫書-plan.md`](docs/計畫書-plan.md)。

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
