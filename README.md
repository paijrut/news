# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/news-image-agent-2026/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/news-image-agent-2026/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

The world's news of Wednesday 18 November 2026, on one page. This is a
[make.fun](https://make.fun/bounty/news-image-20261118) entry: a program that
draws a broadsheet front page of the day's news to `/output/entry.png` at
1024x1024, standard library only, no network, deterministic across runs.

The page leads with the Trump-Xi-Putin trilateral at APEC Shenzhen, then six
stories across Ukraine, the Gulf, Wall Street, health, Africa and Europe, a
markets strip, and the "meanwhile" rail. Every fact is dated 17-18 November
2026 and sourced; see [sources.md](sources.md).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python main.py
```

In the grader's container `MAKEFUN_OUTPUT_DIR` is already `/output`. The
program reads `news/day.json` (the day's stories) and the bitmap fonts in
`fonts/`, and writes the same bytes every run.

## How it works

- `main.py` lays out the page: masthead, lead story with figure box, a
  three-column story grid, a markets strip, and a "meanwhile" rail.
- `render.py` is a tiny RGB canvas and PNG writer (zlib, struct) plus a bitmap
  font renderer; the fonts in `fonts/*.pil` were generated from system fonts
  by `tools/fontgen.py` at build time and ship in the repository.
- `news/day.json` carries the day's stories, each with a headline, summary,
  figure and note; edit it and re-run to redraw the page.

---

<sub>Entered on [make.fun](https://make.fun/?ref=9jrq4jxx&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
