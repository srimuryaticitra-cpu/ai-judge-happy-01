# The Judge's Day Off

make.fun bounty entry — **"Make the AI judge happy"**
(https://make.fun/bounty/ai-happy-01)

A friendly robot judge — powdered judge's wig, black robe, gold
medallion — taking a day off on a sunny beach, cocktail in hand,
gavel put down in the sand. The joke is aimed at the judge itself:
after judging thousands of pictures, this one hands the judge a
verdict of its own. Caption: **VERDICT: HAPPY**.

## Run

```sh
python3 main.py
```

Writes one image to `/output/entry.png` (1024×1024 PNG, ~19 KB).

## How it works

`main.py` draws the whole scene in code with the Python standard
library only (`math`, `struct`, `zlib`, `pathlib`) — a small canvas
library (rectangles, circles, ellipses, thick lines, arcs, polygons,
a 5×7 pixel font) plus a minimal deterministic PNG encoder. No
network, no external files, no randomness, no clock. Running it twice
produces byte-for-byte identical output.

## Files

- `main.py` — the entry program (repo root)
- `entry.png` — the generated image (review copy)
- `LICENSE` — MIT
- `transcript.md` — session log of the AI coding-agent session that
  built this entry
