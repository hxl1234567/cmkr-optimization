#!/usr/bin/env python3
"""Generate cmkr.ico (gear + C, #0EA5E9). Pure stdlib: SVG-style vector raster
+ box-downscale + zlib PNG + ICO container. No third-party deps."""
import math
import struct
import zlib
import os

# ---- canvas ----
N = 1024  # supersample resolution
CX = CY = N / 2.0

# gear geometry
TEETH = 12
R_TIP = 500.0      # tooth outer tip
R_VAL = 430.0      # tooth valley
R_BODY = 410.0     # inner body radius (solid disk under teeth)
# C glyph
C_OUT = 360.0      # outer radius of C ring
C_IN = 215.0       # inner radius of C ring
C_GAP = math.radians(72)  # opening angular width (right side)

# colors
CY_TOP = (0x38, 0xBD, 0xF8)   # lighter cyan (top)
CY_BOT = (0x02, 0x84, 0xC7)   # darker cyan (bottom)
WHITE = (0xFF, 0xFF, 0xFF)
EDGE = (0x03, 0x69, 0xA8)     # subtle darker edge line


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gear_radius(theta):
    """Toothed profile radius as function of angle."""
    seg = (theta % (2 * math.pi / TEETH)) / (2 * math.pi / TEETH)
    # 0..0.5 rising/plateau tip, 0.5..1 valley — trapezoidal-ish
    if seg < 0.30:
        return R_TIP
    elif seg < 0.45:
        f = (seg - 0.30) / 0.15
        return R_TIP + (R_VAL - R_TIP) * f
    elif seg < 0.70:
        return R_VAL
    elif seg < 0.85:
        f = (seg - 0.70) / 0.15
        return R_VAL + (R_TIP - R_VAL) * f
    else:
        return R_TIP


def render(size):
    """RGBA bytearray for given output size (vector-rasterized from N)."""
    px = bytearray(size * size * 4)
    # supersample grid: per output pixel, sample SS x SS points
    SS = N // size if N >= size else 1
    if SS < 1:
        SS = 1
    inv = 1.0 / (SS * SS)
    scale = N / size  # output->super coordinate
    for oy in range(size):
        for ox in range(size):
            r_acc = g_acc = b_acc = a_acc = 0
            for sy in range(SS):
                for sx in range(SS):
                    # super-space coord center of subsample
                    fx = (ox + (sx + 0.5) / SS) * scale
                    fy = (oy + (sy + 0.5) / SS) * scale
                    dx = fx - CX
                    dy = fy - CY
                    r = math.hypot(dx, dy)
                    theta = math.atan2(dy, dx)  # [-pi,pi]
                    col = (0, 0, 0, 0)  # transparent default
                    # gear body
                    gr = gear_radius(theta)
                    if r <= gr:
                        # vertical gradient cyan
                        t = (fy) / N  # 0 top .. 1 bottom
                        t = max(0.0, min(1.0, t))
                        rgb = lerp(CY_TOP, CY_BOT, t)
                        # edge darken at outer rim
                        if r > gr - 6:
                            rgb = lerp(rgb, EDGE, (r - (gr - 6)) / 6.0)
                        col = (rgb[0], rgb[1], rgb[2], 255)
                        # C glyph: white ring with gap on +x side
                        if C_IN <= r <= C_OUT:
                            # opening centered at theta=0
                            at = abs(theta)  # distance from +x axis
                            if at > C_GAP / 2:
                                col = (WHITE[0], WHITE[1], WHITE[2], 255)
                            else:
                                # taper ends of C for a clean break
                                edge_t = (C_GAP / 2 - at) / 6.0
                                if edge_t > 0:
                                    col = (rgb[0], rgb[1], rgb[2], 255)
                        # subtle inner shadow ring at C_OUT boundary
                        if abs(r - C_OUT) < 2 and abs(theta) > C_GAP / 2:
                            col = (EDGE[0], EDGE[1], EDGE[2], 255)
                    r_acc += col[0]
                    g_acc += col[1]
                    b_acc += col[2]
                    a_acc += col[3]
            i = (oy * size + ox) * 4
            px[i] = int(r_acc * inv)
            px[i + 1] = int(g_acc * inv)
            px[i + 2] = int(b_acc * inv)
            px[i + 3] = int(a_acc * inv)
    return px


# ---- minimal PNG encoder (RGBA 8-bit) ----
def png_encode(size, rgba):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return c + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8-bit, RGBA
    raw = bytearray()
    stride = size * 4
    for y in range(size):
        raw.append(0)  # filter: None
        raw += rgba[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def write_ico(path, sizes):
    # sizes: list of (size, png_bytes)
    count = len(sizes)
    header = struct.pack("<HHH", 0, 1, count)  # reserved, type=icon, count
    entries = b""
    offset = 6 + count * 16
    imgs = b""
    for size, png in sizes:
        w = 0 if size >= 256 else size
        h = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), offset)
        imgs += png
        offset += len(png)
    with open(path, "wb") as f:
        f.write(header)
        f.write(entries)
        f.write(imgs)


def main():
    out_sizes = [256, 128, 64, 48, 32, 16]
    built = []
    for s in out_sizes:
        rgba = render(s)
        png = png_encode(s, rgba)
        built.append((s, png))
        print("rendered", s)
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "cmkr.ico")
    write_ico(out, built)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
