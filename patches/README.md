# patches/

## 中文化本身：不需任何補丁

猴島 2（`GID_MONKEY2`, SCUMM v5）在**原版 ScummVM** 就內建繁體可用的 CJK 路徑：只要遊戲夾放 `chinese_gb16x12.fnt`，ScummVM 自動偵測為 Chinese 並走 GB2312 渲染路徑（`GID_MONKEY2` 已在 upstream 白名單）。中文化用「**全位元組 0xA1–0xFD 的 GB2312 相容自訂碼空間**」（見 `data/cht_table.json`、`tools/cht_codec.py`），所有位元組 ≥ 0xA1，不撞 SCUMM/scummtr 的 ASCII 特殊字元，也符合引擎「雙位元組字 trail ≥ 0x80」假設 → **零原始碼修改**。原版 scummtr 即可注入。

## 選用補丁：防拷自動略過

- **0001-mi2-dos-copyprotection-bypass.patch**（對 upstream ScummVM，pinned commit 見 `UPSTREAM_COMMIT.txt`）
  DOS 版猴島 2 的 Mix'N'Mojo 密碼轉盤防拷 ScummVM 不會自動略過（只有 Mac 版有）。
  反組譯 room 108 的 `SCRP_0130` 找到驗證點 `if (Var[518] != Var[490])`（玩家答案 vs 正確答案）；
  patch 在 `script.cpp writeVar`：當 `copy_protection=false` 且在 room 108，寫正確答案 Var[490] 時
  同步鏡射 Var[518] → 比對永遠相等 → **輸入任意兩個數字即通過**（不必查密碼轉盤）。
  套用：`cd scummvm-src && git checkout <UPSTREAM_COMMIT> && git apply ../patches/0001-*.patch`。
  **此 patch 為選用**（中文化不依賴它）；不套的話玩家需對照 `docs/copyprotection-answer.md` 的密碼表輸入正解。
