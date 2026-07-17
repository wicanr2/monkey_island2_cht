# patches/

**本專案不需要任何 ScummVM 或 scummtr 原始碼補丁——中文化與防拷略過在原版即可運作。**

## 中文化：零補丁

猴島 2（`GID_MONKEY2`, SCUMM v5）在**原版 ScummVM** 就內建繁體可用的 CJK 路徑：只要遊戲夾放 `chinese_gb16x12.fnt`，ScummVM 自動偵測為 Chinese 並走 GB2312 渲染路徑（`GID_MONKEY2` 已在 upstream 白名單）。中文化用「**全位元組 0xA1–0xFD 的 GB2312 相容自訂碼空間**」（見 `data/cht_table.json`、`tools/cht_codec.py`），所有位元組 ≥ 0xA1，不撞 SCUMM/scummtr 的 ASCII 特殊字元，也符合引擎「雙位元組字 trail ≥ 0x80」假設 → **零原始碼修改**。原版 scummtr 即可注入。

## 防拷：原版 ScummVM 已內建略過（不需補丁）

DOS 版 Mix'N'Mojo 密碼轉盤防拷，**原版 ScummVM 就會放行**：ScummVM 的「Enable copy protection」選項預設關閉，此時引擎的 `readVar` 會把防拷腳本讀取的「正確答案」重定向成「玩家輸入」本身，使驗證式恆為真——玩家**輸入任意完整答案（4 位數字）即通過**，不必對照密碼轉盤。

> 我們用 `descumm` 反組譯 room 108 的 `SCRP_0130` 找到驗證式 `if (Var[518] != Var[490])`，並在 pristine（未改動）ScummVM 上以 headless 實測「輸入 5555（錯）→ 直接進入遊戲開場」確認此行為。早期一度自行加了鏡射 patch，實測發現 upstream（Scott Percival, 2026-06）已內建同等機制，故該 patch 屬多餘、已移除。
>
> 想照當年方法對照密碼盤解謎的人，密碼表整理在 `docs/copyprotection-answer.md`。
