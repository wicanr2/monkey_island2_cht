# ScummVM 中文化補丁

對 upstream ScummVM（見 `UPSTREAM_COMMIT.txt` 的 pinned commit）套用：

- **0001-scumm-mi2-gbk-traditional-chinese.patch**：讓 MI2(`GID_MONKEY2`, SCUMM v5) 走
  GBK 全 range 繁體路徑——`charset.cpp` numChar 8178→23940、`get2byteCharPtr` GB2312 EUC
  index 改 GBK 線性。搭配 `tools/build_gbk_font.py` 烘的 `chinese_gb16x12.fnt`(GBK 23940 字)。

套用：`cd scummvm-src && git checkout <UPSTREAM_COMMIT> && git apply ../patches/0001-*.patch`

- **0002-scummtr-cjk-escape-tolerant.patch**：讓 scummtr(dwatteau, 見 SCUMMTR_UPSTREAM.txt) 正確處理
  CJK trail byte 0xFE——`funcLen` 未知 id 回 −1、偵測點改「0xFE 僅後接合法 function id 才當 escape」。
  無此 patch 全量中文注入會 `Unknown function id` / `Truncated function` 中止。
套用：`cd scummtr && git apply ../patches/0002-*.patch && cmake --build build`
