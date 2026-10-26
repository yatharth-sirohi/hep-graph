#!/usr/bin/env python3
"""Build static/atlas/vendor/earth-dark-4096.webp from Natural Earth's
"Gray Earth with Shaded Relief, Hypsography, and Ocean Bottom" (1:50m).

The source is a 10,800 x 5,400, 8-bit grey GeoTIFF, public domain. Ocean pixels
sit in grey 72-110 and land in 120-235 (a clean valley between them), so the
land/ocean mask is a soft threshold on the image itself and the grid agrees with
the raster's own coastline. Land is mapped to a desaturated slate ramp and the
ocean floor to a navy ramp whose contrast is stretched, so shelves, ridges and
trenches stay faintly visible. Land is deliberately capped dark (relative
luminance <= ~0.065): the facility markers must keep >= 3:1 against it.

Needs numpy, plus macOS `sips` (resize / TIFF and PNG conversion) and `cwebp`
(brew install webp). Usage:

    python3 scripts/atlas_earth_texture.py GRAY_50M_SR_OB.tif out.webp [work-dir]
"""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

WIDTH, HEIGHT = 4096, 2048
WEBP_QUALITY = '74'
DITHER = 0.0  # LSBs of triangular noise; the lossy coder smooths it, so it only costs bytes

# (r, g, b) ramps, low -> high. Colours are sRGB 0-255.
OCEAN_DEEP = (5, 15, 23)
OCEAN_SHELF = (17, 47, 66)
LAND_LOW = (34, 47, 57)
LAND_HIGH = (54, 68, 79)


def read_bmp(path: Path) -> np.ndarray:
    data = path.read_bytes()
    offset = struct.unpack_from('<I', data, 10)[0]
    width, height = struct.unpack_from('<ii', data, 18)
    bits = struct.unpack_from('<H', data, 28)[0]
    channels = bits // 8
    rows = abs(height)
    stride = ((width * bits + 31) // 32) * 4
    flat = np.frombuffer(data, dtype=np.uint8, count=stride * rows, offset=offset)
    image = flat.reshape(rows, stride)[:, : width * channels].reshape(rows, width, channels)
    return image[::-1] if height > 0 else image


def write_bmp(path: Path, rgb: np.ndarray) -> None:
    rows, width, _ = rgb.shape
    stride = ((width * 24 + 31) // 32) * 4
    body = np.zeros((rows, stride), np.uint8)
    body[:, : width * 3] = rgb[::-1, :, ::-1].reshape(rows, width * 3)
    header = b'BM' + struct.pack('<IHHI', 54 + stride * rows, 0, 0, 54)
    header += struct.pack('<IiiHHIIiiII', 40, width, rows, 1, 24, 0, stride * rows, 2835, 2835, 0, 0)
    path.write_bytes(header + body.tobytes())


def box_blur(image: np.ndarray, radius: int) -> np.ndarray:
    """A separable box blur (wrapping in longitude, clamped at the poles)."""
    width = 2 * radius + 1
    padded = np.concatenate([image[:, -radius:], image, image[:, :radius]], axis=1)
    csum = np.cumsum(np.pad(padded, ((0, 0), (1, 0))), axis=1)
    horizontal = (csum[:, width:] - csum[:, :-width]) / width
    padded = np.pad(horizontal, ((radius, radius), (0, 0)), mode='edge')
    csum = np.cumsum(np.pad(padded, ((1, 0), (0, 0))), axis=0)
    return (csum[width:] - csum[:-width]) / width


def smoothstep(lo: float, hi: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ramp(t: np.ndarray, low: tuple[int, int, int], high: tuple[int, int, int]) -> np.ndarray:
    a, b = np.array(low, np.float32), np.array(high, np.float32)
    return a + (b - a) * t[..., None]


def main() -> None:
    source, out = Path(sys.argv[1]), Path(sys.argv[2])
    work = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(tempfile.mkdtemp(prefix='earth-'))
    work.mkdir(parents=True, exist_ok=True)
    small = work / 'gray.bmp'
    subprocess.run(['sips', '-z', str(HEIGHT), str(WIDTH), '-s', 'format', 'bmp', str(source), '--out', str(small)],
                   check=True, capture_output=True)
    grey = read_bmp(small)[..., 0].astype(np.float32)

    land = smoothstep(112.0, 128.0, grey)
    # Local contrast: the grey carries hillshading as well as height; adding back its
    # high-pass component makes ridges and ocean-floor fractures read at globe scale.
    detail = grey - box_blur(grey, 9)
    ocean_t = np.clip((grey + 2.2 * detail - 78.0) / (108.0 - 78.0), 0.0, 1.0) ** 0.85
    land_t = np.clip((grey + 1.4 * detail - 128.0) / (226.0 - 128.0), 0.0, 1.0) ** 1.1
    rgb = ramp(ocean_t, OCEAN_DEEP, OCEAN_SHELF) * (1 - land[..., None]) + ramp(land_t, LAND_LOW, LAND_HIGH) * land[..., None]
    rng = np.random.default_rng(7)
    rgb += (rng.random(rgb.shape, dtype=np.float32) - rng.random(rgb.shape, dtype=np.float32)) * DITHER
    final = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)

    bmp, png = work / 'earth.bmp', work / 'earth.png'
    write_bmp(bmp, final)
    subprocess.run(['sips', '-s', 'format', 'png', str(bmp), '--out', str(png)], check=True, capture_output=True)
    subprocess.run(['cwebp', '-q', WEBP_QUALITY, '-m', '6', '-sharp_yuv', str(png), '-o', str(out)],
                   check=True, capture_output=True)
    print(f'{out}: {out.stat().st_size} bytes')


if __name__ == '__main__':
    main()
