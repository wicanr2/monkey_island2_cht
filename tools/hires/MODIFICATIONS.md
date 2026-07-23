# ScummVM 修改說明(GPLv3+ 合規)

本專案的「高清文字版」(hi-res text edition)使用**修改過的 ScummVM**。依 GPLv3+「accompanying source」要求,此處說明改動內容;完整改動見同目錄 `scummvm-mi2-hires.patch`。

- **上游基底**:ScummVM,commit `cb8802d6f9e8d9453dd6b8e5c7987278a882b6e2`(版本 2026.2.1git)。
- **上游來源**:<https://github.com/scummvm/scummvm>(GPLv3+)。
- **授權**:本修改同樣以 **GPLv3+** 釋出。

## 改動檔案與目的

只動兩個檔,且全部以 `_game.id == GID_MONKEY2` 條件包住,**不影響其他遊戲**。目的是讓 Monkey Island 2 的繁體中文(ZH_CHN 路徑)以高解析度渲染,解決 320×200 下 12×12 點陣中文過糊的問題。

### `engines/scumm/charset.cpp`
- `loadCJKFont()`:MONKEY2 + ZH_CHN 時 `_2byteWidth = _2byteHeight = 24`(原 12),並設 `_textSurfaceMultiplier = 2`(啟用 ScummVM 既有的 640×400 text surface)。
- `CharsetRendererClassic::printChar()`:2-byte 字的游標推進/裁切改用「邏輯寬」(`_origWidth / _textSurfaceMultiplier`),使 24×24 高解析字模在不改變排版邏輯下顯示(解耦繪製尺寸與排版寬度)。
- `CharsetRendererClassic::printCharIntern()`:CJK 畫到 2× text surface 時座標 `× _textSurfaceMultiplier`。

### `engines/scumm/gfx.cpp`
- `drawStripToScreen()`:`_useCJKMode && m == 2` 時,先把 1× 遊戲底圖以 nearest-neighbor 放大到 2× 暫存 buffer,再與 2× text surface 合成(既有 CPU 合成迴圈假設兩者同解析度)。
- `restoreBackground()`:非 FM-Towns/Mac 路徑清除 text mask 時座標補 `× _textSurfaceMultiplier`(與清除範圍對齊,避免舊字殘留)。

字型檔以 WenQuanYi Micro Hei(GPL)烘製 24×24 點陣,依本專案 `cht_codec` 自訂碼表對齊碼位。
