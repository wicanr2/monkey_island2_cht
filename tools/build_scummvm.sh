#!/bin/bash
# 在 docker 內編 ScummVM（scumm 引擎 + MT-32 emu），保持 host 乾淨。
# CLAUED.md ⑤：configure 一律不帶 --disable-mt32emu。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/scummvm-src"

docker run --rm --name mi2-build \
    -v "$SRC_DIR:/src" \
    -w /src \
    ubuntu:24.04 \
    bash -c '
        set -e
        apt-get update -qq && apt-get install -y -qq \
            build-essential libsdl2-dev libsdl2-net-dev \
            libfreetype6-dev libflac-dev libogg-dev libvorbis-dev \
            libmpeg2-4-dev libmad0-dev libjpeg-turbo8-dev libpng-dev \
            libtheora-dev libfaad-dev libfluidsynth-dev \
            libcurl4-openssl-dev libsndio-dev \
            pkg-config zlib1g-dev nasm > /dev/null 2>&1

        echo "=== Configuring (scumm engine, MT-32 emu ON) ==="
        ./configure --disable-all-engines --enable-engine=scumm \
            --enable-release 2>&1 | tail -8
        echo "=== grep USE_MT32EMU config.h ==="
        grep USE_MT32EMU config.h || echo "!! MT32EMU 未定義"

        echo "=== Building ==="
        make -j"$(nproc)" 2>&1 | tail -15
        echo "=== Done ==="
        ls -lh scummvm
    '
echo "=== 完成，binary: $SRC_DIR/scummvm ==="
ls -lh "$SRC_DIR/scummvm" 2>/dev/null || echo "!! binary 不存在"
