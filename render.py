"""Render the front page to PNG from pure-Python primitives (no dependencies).

Only what the Python 3.13 sandbox needs: zlib (PNG), freetype-py substitute is
NOT available, so we draw text with a bundled bitmap font rasterizer we wrote
for this entry: fonts/*.pil are ours, generated offline by tools/fontgen.py.

Everything here is deterministic: same input -> same bytes, twice.
"""

import json
import struct
import zlib
from pathlib import Path

W = H = 1024

# ---------- PNG writing ----------
def write_png(path, width, height, rgba_rows):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + row for row in rgba_rows)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    Path(path).write_bytes(png)

# ---------- canvas ----------
class Canvas:
    def __init__(self, w=W, h=H, bg=(245, 242, 233)):
        self.w, self.h = w, h
        self.px = [bytearray(bytes(bg) * w) for _ in range(h)]

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color[:3]
        for yy in range(y0, y1):
            row = self.px[yy]
            for xx in range(x0, x1):
                row[xx*3] = r; row[xx*3+1] = g; row[xx*3+2] = b

    def line_h(self, x, y, w, t, color):
        self.rect(x, y, w, t, color)
    def line_v(self, x, y, h, t, color):
        self.rect(x, y, t, h, color)

    def save(self, path):
        # canvas stores RGB triples; convert to RGBA rows
        rows = []
        for row in self.px:
            out = bytearray()
            for i in range(0, len(row), 3):
                out += row[i:i+3] + b"\xff"
            rows.append(out)
        write_png(path, self.w, self.h, rows)

# ---------- bitmap text ----------
class Font:
    """A .pil file: JSON {height, glyphs: {ch: [width, rows...]}} rows are hex strings, MSB left."""
    def __init__(self, path):
        d = json.loads(Path(path).read_text())
        self.h = d["height"]
        self.glyphs = {}
        self.rows = {}
        for ch, g in d["glyphs"].items():
            w, rows = g[0], g[1]
            self.glyphs[ch] = (w, b"".join(bytes.fromhex(r) for r in rows))
            # each row is ceil(w/8) bytes
            stride = (w + 7) // 8
            self.rows[ch] = [self.glyphs[ch][1][i*stride:(i+1)*stride] for i in range(self.h)]

    def text(self, canvas, x, y, s, color, spacing=1):
        cx = x
        for ch in s:
            g = self.glyphs.get(ch)
            if g is None:
                cx += 8 + spacing
                continue
            gw, _ = g
            rows = self.rows[ch]
            for ry in range(self.h):
                bits = rows[ry]
                for bx in range(gw):
                    byte = bits[bx >> 3]
                    if byte & (0x80 >> (bx & 7)):
                        px = cx + bx
                        if 0 <= px < canvas.w and 0 <= y + ry < canvas.h:
                            i = px * 3
                            canvas.px[y + ry][i:i+3] = bytes(color)
            cx += gw + spacing
        return cx

    def width(self, s, spacing=1):
        w = 0
        for ch in s:
            g = self.glyphs.get(ch)
            w += (g[0] if g else 8) + spacing
        return w

    def wrap(self, text, max_w, spacing=1):
        lines, cur = [], ""
        for word in text.split(" "):
            trial = (cur + " " + word).strip()
            if self.width(trial, spacing) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur); cur = word
        if cur:
            lines.append(cur)
        return lines
