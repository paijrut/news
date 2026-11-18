"""Generate bitmap PIL fonts from Windows system fonts (Windows-only, build time).

Not shipped logic that runs in the grader; run once here to create fonts/*.pil.
"""
import json
import struct
import zlib
import sys
from pathlib import Path

# Minimal TTF glyf parser is overkill; instead use PIL if available locally.
try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    print("PIL not available; pip install pillow", file=sys.stderr)
    sys.exit(1)


def extract(font_path, sizes, out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(exist_ok=True)
    for size in sizes:
        f = ImageFont.truetype(str(font_path), size)
        # ASCII + common punctuation
        chars = [chr(c) for c in range(32, 127)] + list("€£¥•–—…""''")
        glyphs = {}
        asc, desc = f.getmetrics()
        height = asc + desc
        for ch in chars:
            try:
                bbox = f.getbbox(ch)
            except Exception:
                continue
            if bbox is None:
                continue
            w = bbox[2] - bbox[0]
            if w <= 0:
                glyphs[ch] = [1, ["00"] * height]
                continue
            img = Image.new("1", (w, height), 0)
            d = ImageDraw.Draw(img)
            d.text((0, 0), ch, font=f, fill=1)
            rows = []
            for y in range(height):
                byte = 0
                packed = []
                for x in range(w):
                    if img.getpixel((x, y)):
                        byte |= 0x80 >> (x & 7)
                    if (x & 7) == 7:
                        packed.append(byte); byte = 0
                if w % 8:
                    packed.append(byte)
                rows.append(bytes(packed).hex())
            glyphs[ch] = [w, rows]
        out = {"height": height, "glyphs": {ch: g for ch, g in glyphs.items()}}
        name = Path(font_path).stem.lower()
        (out_dir / f"{name}-{size}.pil").write_text(json.dumps(out))
        print("wrote", name, size, "height", height, "glyphs", len(glyphs))


if __name__ == "__main__":
    import os
    fonts = sys.argv[1:] or [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    sizes = [int(s) for s in os.environ.get("FONT_SIZES", "24,34,48").split(",")]
    for f in fonts:
        extract(f, sizes, "fonts")
