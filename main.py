#!/usr/bin/env python3
"""news-image-20261118: the world's news of Wednesday 18 November 2026, one page.

A program/v1 entry: reads news/day.json (baked into this repository, gathered
from the day's reporting, see sources.md) and draws a broadsheet front page to
/output/entry.png at 1024x1024. Standard library only; runs twice and writes
the same bytes both times (no clock, no randomness, fixed layout).

Design: a compact broadsheet in four bands. The masthead names the day; the
lead story carries the APEC summit with its figure box; six story blocks in a
two-column grid give the day's news across war, markets, health and Europe; a
bottom band carries the markets closes and the "meanwhile" items, so a reader
who missed the day can tell what happened from the picture alone.

Run (the grader runs it the same way, /output instead of the env):
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python main.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render import Canvas, Font, W, H  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

# palette: newsprint ivory, near-black ink, one signal red, one sea blue
INK = (24, 24, 22)
PAPER = (245, 242, 233)
RED = (178, 34, 34)
BLUE = (31, 78, 121)
GREY = (96, 92, 84)
RULE = (60, 58, 52)


def draw_story(c, f_kick, f_head, f_body, f_num, x, y, col_w, story):
    """One story block: kicker, rule, headline, summary, big figure, note."""
    f_kick.text(c, x, y, story["kicker"], BLUE)
    y += f_kick.h
    c.line_h(x, y, col_w, 2, RULE)
    y += 4
    for ln in f_head.wrap(story["headline"], col_w):
        f_head.text(c, x, y, ln, INK)
        y += f_head.h + 4
    for ln in f_body.wrap(story["summary"], col_w):
        f_body.text(c, x, y, ln, INK)
        y += f_body.h
    y += 2
    fw = f_num.width(story["figure"])
    f_num.text(c, x, y, story["figure"], RED)
    y += f_num.h + 6
    for ln in f_body.wrap(story["figure_note"], col_w):
        f_body.text(c, x, y, ln, GREY)
        y += f_body.h - 2
    return y + 8


def main():
    day = json.loads((ROOT / "news" / "day.json").read_text())

    f_head = Font(ROOT / "fonts" / "impact-28.pil")
    f_deck = Font(ROOT / "fonts" / "georgiab-20.pil")
    f_kick = Font(ROOT / "fonts" / "arialbd-20.pil")
    f_body = Font(ROOT / "fonts" / "arial-16.pil")
    f_num = Font(ROOT / "fonts" / "impact-34.pil")

    c = Canvas(W, H, PAPER)

    # ---- masthead ----
    c.rect(0, 0, W, 8, INK)
    f_kick.text(c, 40, 22, "THE WORLD IN A DAY", INK)
    date_w = f_deck.width(day["date"])
    f_deck.text(c, W - 40 - date_w, 22, day["date"], INK)
    c.line_h(40, 56, W - 80, 3, INK)

    # ---- lead story: headline and dek left, figure box right ----
    y = 68
    lead = day["lead"]
    f_kick.text(c, 40, y, lead["kicker"], RED)
    y += f_kick.h + 2
    text_w = W - 80 - 210
    for ln in f_head.wrap(lead["headline"], text_w):
        f_head.text(c, 40, y, ln, INK)
        y += f_head.h + 4
    y += 2
    for ln in f_deck.wrap(lead["dek"], text_w):
        f_deck.text(c, 70, y, ln, INK)
        y += f_deck.h
    lead_bottom = y + 4
    box_x, box_w, box_y, box_h = W - 40 - 190, 190, 90, 88
    c.rect(box_x, box_y, box_w, box_h, INK)
    num_w = f_num.width(lead["figure"])
    f_num.text(c, box_x + (box_w - num_w) // 2, box_y + 4, lead["figure"], PAPER)
    cy = box_y + f_num.h + 4
    for ln in f_body.wrap(lead["caption"], box_w - 12):
        lw = f_body.width(ln)
        f_body.text(c, box_x + (box_w - lw) // 2, cy, ln, PAPER)
        cy += f_body.h - 2
    y = max(lead_bottom, box_y + box_h) + 10

    # ---- three-column story grid: six stories, two rows ----
    col_gap = 24
    col_w = (W - 80 - 2 * col_gap) // 3
    for row in range(2):
        row_bottom = y
        for col in range(3):
            story = day["stories"][row * 3 + col]
            x = 40 + col * (col_w + col_gap)
            bottom = draw_story(c, f_kick, f_head, f_body, f_num,
                                x, y, col_w, story)
            row_bottom = max(row_bottom, bottom)
        y = row_bottom + 2

    # ---- markets strip: one row of closes ----
    c.line_h(40, y, W - 80, 2, RULE)
    y += 6
    f_kick.text(c, 40, y, "MARKETS (TUE NOV 17 CLOSE)", INK)
    y += f_kick.h + 4
    seg = (W - 80) // len(day["markets"])
    for i, m in enumerate(day["markets"]):
        x = 40 + i * seg
        f_body.text(c, x, y, m["name"], GREY)
        f_deck.text(c, x, y + f_body.h + 2, m["close"], INK)
        up = m["change"].startswith("+")
        col = (22, 96, 52) if up else RED
        f_kick.text(c, x, y + f_body.h + f_deck.h + 8, m["change"] + (" UP" if up else " DN"), col)
    y += f_body.h + f_deck.h + f_kick.h + 16

    # ---- meanwhile rail: items in two columns ----
    c.line_h(40, y, W - 80, 2, RULE)
    y += 6
    f_kick.text(c, 40, y, "MEANWHILE", INK)
    y += f_kick.h + 4
    half = (len(day["meanwhile"]) + 1) // 2
    col2 = W // 2 + 10
    for i, item in enumerate(day["meanwhile"]):
        ci = 0 if i < half else 1
        xx = 58 if ci == 0 else col2
        yy = y + (i % half) * f_body.h
        c.rect(xx - 16, yy + 2, 7, 7, RED)
        f_body.text(c, xx, yy, item, INK)

    # ---- footer ----
    c.rect(0, H - 28, W, 28, INK)
    foot = "Sources: " + day["source_note"]
    f_body.text(c, 40, H - 20, foot, PAPER)

    OUT.mkdir(parents=True, exist_ok=True)
    c.save(str(OUT / "entry.png"))
    print("wrote", OUT / "entry.png")


if __name__ == "__main__":
    main()
