"""Generate a 256x256 RGBA PNG icon (no external deps)."""
import struct
import zlib
import math
import sys

W = H = 256


def mk_png(path, pixels):
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xffffffff
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        for x in range(W):
            r, g, b, a = pixels[y * W + x]
            raw += bytes((r, g, b, a))
    idat = zlib.compress(bytes(raw), 9)

    with open(path, "wb") as f:
        f.write(sig)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", idat))
        f.write(chunk(b"IEND", b""))


def main(path, theme):
    if theme == "morning":
        bg = (26, 22, 18)
        ring_outer = (74, 62, 42)
        accent = (212, 166, 74)
        accent_glow = (236, 196, 110)
    else:
        bg = (20, 24, 34)
        ring_outer = (50, 68, 100)
        accent = (91, 143, 196)
        accent_glow = (140, 180, 220)

    cx = cy = W / 2.0
    r_outer = 116
    r_inner = 80

    pixels = [bg] * (W * H)
    pixels = [(*bg, 255)] * (W * H)
    for y in range(H):
        for x in range(W):
            dx = x - cx + 0.5
            dy = y - cy + 0.5
            d = math.sqrt(dx * dx + dy * dy)
            if d > r_outer + 2:
                continue
            if d > r_outer:
                t = (r_outer + 2 - d) / 2.0
                r = int(bg[0] * (1 - t) + ring_outer[0] * t)
                g = int(bg[1] * (1 - t) + ring_outer[1] * t)
                b = int(bg[2] * (1 - t) + ring_outer[2] * t)
                pixels[y * W + x] = (r, g, b, 255)
            elif d > r_outer - 3:
                pixels[y * W + x] = (*ring_outer, 255)
            elif d > r_inner:
                t = (d - r_inner) / (r_outer - 3 - r_inner)
                t = max(0.0, min(1.0, t))
                r = int(bg[0] * (1 - t * 0.4) + ring_outer[0] * t * 0.4)
                g = int(bg[1] * (1 - t * 0.4) + ring_outer[1] * t * 0.4)
                b = int(bg[2] * (1 - t * 0.4) + ring_outer[2] * t * 0.4)
                pixels[y * W + x] = (r, g, b, 255)
            else:
                t = d / r_inner
                glow = (1 - t) ** 1.4
                r = int(accent[0] * (1 - glow) + accent_glow[0] * glow)
                g = int(accent[1] * (1 - glow) + accent_glow[1] * glow)
                b = int(accent[2] * (1 - glow) + accent_glow[2] * glow)
                pixels[y * W + x] = (r, g, b, 255)

    mk_png(path, pixels)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "morning")
    print(f"wrote {sys.argv[1]}")
