# ScummVM 中文化補丁

對 upstream ScummVM（見 `UPSTREAM_COMMIT.txt` 的 pinned commit）套用：

- **0001-scumm-mi2-gbk-traditional-chinese.patch**：讓 MI2(`GID_MONKEY2`, SCUMM v5) 走
  GBK 全 range 繁體路徑——`charset.cpp` numChar 8178→23940、`get2byteCharPtr` GB2312 EUC
  index 改 GBK 線性。搭配 `tools/build_gbk_font.py` 烘的 `chinese_gb16x12.fnt`(GBK 23940 字)。

套用：`cd scummvm-src && git checkout <UPSTREAM_COMMIT> && git apply ../patches/0001-*.patch`
