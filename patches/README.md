# patches/

**本專案不需要任何 ScummVM 或 scummtr 原始碼補丁。**

猴島 2（`GID_MONKEY2`, SCUMM v5）在**原版 ScummVM** 就內建繁體可用的 CJK 路徑：只要遊戲夾放 `chinese_gb16x12.fnt`，ScummVM 會自動偵測為 Chinese 並走 GB2312 渲染路徑（`GID_MONKEY2` 已在 upstream 白名單）。

中文化用「**全位元組 0xA1–0xFD 的 GB2312 相容自訂碼空間**」把 2430 個繁體字映射進 GB2312 結構（見 `data/cht_table.json`），字型與譯文編碼都據此產生（`tools/cht_codec.py`、`tools/build_cht_font.py`）。因所有位元組 ≥ 0xA1，不會撞到 SCUMM/scummtr 的 ASCII 特殊字元（`@`=0x40、`\`=0x5C、escape 0xFE/0xFF），也符合引擎「雙位元組字 trail ≥ 0x80」的假設 → **零原始碼修改**。

> 早期曾試 GBK 全 range（需 patch charset.cpp 的 index 公式 + scummtr escape 容錯），但 GBK 的 trail byte 落在 0x40–0x7E 會撞上述假設，造成字元級渲染損毀（見 `docs/計畫書-plan.md` 5.8）。改用高位元組碼空間後全部消除，故不再需要 patch。
