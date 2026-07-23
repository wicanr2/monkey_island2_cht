#!/bin/bash
# 在 GitHub Actions macos-14 runner 上編 MI2 hi-res ScummVM universal binary(arm64+x86_64)。
# 依 mac-app-cross-pack 知識:SDL2 source per-arch(brew 是 sdl2-compat shim,雷)、
#   ScummVM configure flags 走環境變數前綴(非 autoconf)、per-arch 各編 + lipo(單次雙弧會炸)、
#   x86_64 弧走 arch -x86_64 Rosetta、手動 bundle SDL2(per-arch+lipo 下 dylibbundler 會退化成單弧)。
# 輸出:dist/ScummVM.app(universal, Frameworks 內 SDL2 也 universal)。
set -euxo pipefail
MIN=13.4
SDLVER=2.30.9
ROOT="$PWD"
SVM="$ROOT/scummvm"          # clone + patched 的 ScummVM source
WORK="$ROOT/_macbuild"; mkdir -p "$WORK"

# ---- 1. SDL2 per-arch from source(pinned 真 SDL2,非 brew shim)----
curl -fsSL -o "$WORK/SDL2.tar.gz" "https://github.com/libsdl-org/SDL/releases/download/release-${SDLVER}/SDL2-${SDLVER}.tar.gz"
for arch in arm64 x86_64; do
  rm -rf "$WORK/sdl-src-$arch"; mkdir -p "$WORK/sdl-src-$arch"
  tar xf "$WORK/SDL2.tar.gz" -C "$WORK/sdl-src-$arch" --strip-components=1
  P="$WORK/sdl-$arch"
  runner=""; [ "$arch" = x86_64 ] && runner="arch -x86_64"
  ( cd "$WORK/sdl-src-$arch"
    $runner env CFLAGS="-arch $arch -mmacosx-version-min=$MIN" \
                LDFLAGS="-arch $arch -mmacosx-version-min=$MIN" \
      ./configure --prefix="$P" --disable-shared --enable-static \
        --host="$( [ "$arch" = x86_64 ] && echo x86_64-apple-darwin || echo aarch64-apple-darwin )" \
        >/dev/null
    $runner make -j"$(sysctl -n hw.ncpu)" >/dev/null
    make install >/dev/null )
done
# SDL2 靜態連進 ScummVM(--disable-shared),故不需 bundle dylib;binary 自足。

# ---- 2. ScummVM per-arch(SCUMM + mt32emu,最小依賴)----
for arch in arm64 x86_64; do
  P="$WORK/sdl-$arch"
  runner=""; [ "$arch" = x86_64 ] && runner="arch -x86_64"
  ( cd "$SVM"
    make distclean >/dev/null 2>&1 || true
    find . -name '*.o' -delete 2>/dev/null || true
    # [HARD] ScummVM configure 非 autoconf:CXXFLAGS/LDFLAGS 只能環境變數前綴,不能位置參數。
    $runner env \
      CXXFLAGS="-arch $arch -mmacosx-version-min=$MIN" \
      CFLAGS="-arch $arch -mmacosx-version-min=$MIN" \
      LDFLAGS="-arch $arch -mmacosx-version-min=$MIN" \
      ./configure --disable-all-engines --enable-engine=scumm --enable-release \
        --enable-mt32emu \
        --with-sdl-prefix="$P/bin" \
        --disable-fluidsynth --disable-flac --disable-png --disable-freetype2 \
        --disable-jpeg --disable-gif --disable-mpeg2 --disable-vpx --disable-tremor \
        --disable-mikmod --disable-openmpt --disable-fribidi --disable-retrowave \
        --disable-vorbis --disable-mad --disable-faad --disable-theoradec --disable-a52 \
        --disable-libcurl --disable-sndio --disable-timidity --disable-sparkle \
        --disable-eventrecorder
    # 守門:scumm engine 沒被剔除
    grep -qiE "Disabling engine SCUMM" config.log && { echo "### SCUMM 被剔除"; exit 13; } || true
    $runner make -j"$(sysctl -n hw.ncpu)"
    cp scummvm "$WORK/scummvm-$arch" )
done

# ---- 3. lipo 合併 universal binary ----
lipo -create "$WORK/scummvm-arm64" "$WORK/scummvm-x86_64" -output "$WORK/scummvm-universal"
lipo -info "$WORK/scummvm-universal"
lipo -info "$WORK/scummvm-universal" | grep -q arm64 && lipo -info "$WORK/scummvm-universal" | grep -q x86_64 || { echo "### 非雙弧"; exit 20; }

# ---- 4. 組 .app(themes + binary),ad-hoc 簽 ----
APP="$ROOT/dist/ScummVM.app"; rm -rf "$APP"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$WORK/scummvm-universal" "$APP/Contents/MacOS/scummvm"
cp "$SVM"/gui/themes/*.zip "$APP/Contents/Resources/" 2>/dev/null || true
cp "$SVM"/dists/engine-data/*.dat "$APP/Contents/Resources/" 2>/dev/null || true
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>scummvm</string>
<key>CFBundleIdentifier</key><string>org.scummvm.mi2hires</string>
<key>CFBundleName</key><string>ScummVM MI2 HiRes</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>hires</string>
<key>LSMinimumSystemVersion</key><string>$MIN</string>
</dict></plist>
PLIST
codesign --force --deep --sign - "$APP"
lipo -info "$APP/Contents/MacOS/scummvm"

# ---- 5. 打包(tar.gz 保 perm,繞 APFS DMG)----
mkdir -p "$ROOT/dist"
tar czf "$ROOT/dist/mi2-cht-hires-macos-app.tar.gz" -C "$ROOT/dist" ScummVM.app
echo "=== BUILD_OK:dist/mi2-cht-hires-macos-app.tar.gz ==="
ls -la "$ROOT/dist"
