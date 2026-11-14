"""Make the AI judge happy — entry image generator.

Title: "The Judge's Day Off"

The image is drawn entirely in code with the Python standard library
only (no PIL, no network, no external files), so it runs in the
grading sandbox with just Python 3.13.

Scene: a friendly robot judge — powdered judge's wig, black robe,
gold medallion — taking a day off on a sunny beach, cocktail in hand,
feet in the sand. The joke is aimed at the judge itself: after
judging thousands of pictures, this one hands the judge a verdict
of its own. Caption: VERDICT: HAPPY.

Deterministic by design: every shape, colour and coordinate is a
fixed constant. No randomness, no clock, no environment input, no
file reads. Running this program twice produces byte-for-byte
identical output.

Usage:
    python3 main.py
    -> writes /output/entry.png (1024x1024 PNG, well under 1 MiB)
"""

import math
import struct
import zlib
from pathlib import Path

WIDTH = 1024
HEIGHT = 1024
OUT = Path("/output/entry.png")

# ---------------------------------------------------------------- colours
NAVY = (27, 42, 74)
SKY_TOP = (255, 223, 94)
SKY_HORIZON = (255, 177, 78)
SUN = (255, 241, 168)
SUN_RAY = (255, 214, 77)
CLOUD = (255, 255, 255)
SEA = (62, 198, 198)
SAND = (246, 222, 156)
SAND_DOT = (232, 184, 109)
PALM_TRUNK = (139, 90, 43)
PALM_LEAF = (47, 168, 79)
PALM_LEAF_DARK = (31, 138, 63)
COCONUT = (110, 72, 32)
ROBOT_HEAD = (214, 234, 248)
WIG = (255, 255, 255)
WIG_SHADE = (213, 220, 229)
ROBE = (35, 35, 35)
COLLAR = (255, 255, 255)
GOLD = (255, 201, 60)
CHEEK = (245, 169, 184)
GAVEL = (139, 90, 43)
GAVEL_HEAD = (122, 74, 36)
GLASS = (225, 242, 250)
DRINK = (255, 140, 66)
STRAW = (255, 107, 139)
BANNER = (255, 255, 255)

# ---------------------------------------------------------------- 5x7 font
# Only the glyphs the caption needs. Each glyph is 7 rows of 5 cells.
FONT = {
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    ":": [".....", "..#..", ".....", ".....", ".....", "..#..", "....."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Y": ["#...#", "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#.."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}


# ---------------------------------------------------------------- PNG writer
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path, width, height, rgb):
    """Write an RGB byte string as a deterministic PNG (filter 0)."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    Path(path).write_bytes(png)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, colour=(255, 255, 255)):
        self.w = width
        self.h = height
        self.px = bytearray(colour * width * height)

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def fill_rect(self, x0, y0, x1, y1, colour):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.px[i:(y * self.w + x1 + 1) * 3] = bytes(colour) * (x1 - x0 + 1)

    def fill_circle(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, cx + dx, cy + dy, colour)

    def fill_ellipse(self, cx, cy, rx, ry, colour):
        for dy in range(-ry, ry + 1):
            dx = (rx * math.isqrt(max(0, ry * ry - dy * dy))) // ry
            self.fill_rect(cx - dx, cy + dy, cx + dx, cy + dy, colour)

    def thick_line(self, x0, y0, x1, y1, w, colour):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = w // 2
        for s in range(steps + 1):
            t = s / steps
            x = round(x0 + (x1 - x0) * t)
            y = round(y0 + (y1 - y0) * t)
            self.fill_circle(x, y, r, colour)

    def polyline(self, points, w, colour):
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            self.thick_line(x0, y0, x1, y1, w, colour)

    def arc(self, cx, cy, r, a0, a1, w, colour):
        """Arc from angle a0 to a1 (degrees, 0 = east, positive clockwise
        in screen coordinates)."""
        step = 2.0
        a = a0
        while a <= a1 + 0.001:
            rad = math.radians(a)
            x = round(cx + r * math.cos(rad))
            y = round(cy + r * math.sin(rad))
            self.fill_circle(x, y, w // 2, colour)
            a += step

    def fill_polygon(self, points, colour):
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(math.ceil(xs[j])), y,
                               int(math.floor(xs[j + 1])), y, colour)

    def rounded_rect(self, x0, y0, x1, y1, r, colour):
        self.fill_rect(x0 + r, y0, x1 - r, y1, colour)
        self.fill_rect(x0, y0 + r, x1, y1 - r, colour)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.fill_circle(cx, cy, r, colour)

    def text(self, s, x, y, scale, colour):
        cx = x
        for ch in s:
            glyph = FONT[ch]
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       cx + (col + 1) * scale - 1,
                                       y + (row + 1) * scale - 1, colour)
            cx += 6 * scale

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale


# ---------------------------------------------------------------- scene
def draw_sky(c):
    for y in range(0, 641):
        t = y / 640.0
        col = tuple(round(SKY_TOP[i] + (SKY_HORIZON[i] - SKY_TOP[i]) * t)
                    for i in range(3))
        c.fill_rect(0, y, WIDTH - 1, y, col)


def draw_sun(c):
    # 12 rays, then the sun disc on top.
    for k in range(12):
        a = math.radians(k * 30.0)
        x0 = round(160 + 102 * math.cos(a))
        y0 = round(140 + 102 * math.sin(a))
        x1 = round(160 + 138 * math.cos(a))
        y1 = round(140 + 138 * math.sin(a))
        c.thick_line(x0, y0, x1, y1, 14, SUN_RAY)
    c.fill_circle(160, 140, 82, SUN)


def draw_cloud(c, cx, cy, s):
    c.fill_ellipse(cx - 45 * s // 10, cy, 55 * s // 10, 32 * s // 10, CLOUD)
    c.fill_ellipse(cx, cy - 10 * s // 10, 65 * s // 10, 38 * s // 10, CLOUD)
    c.fill_ellipse(cx + 50 * s // 10, cy, 50 * s // 10, 30 * s // 10, CLOUD)


def draw_sea_and_sand(c):
    c.fill_rect(0, 640, WIDTH - 1, 739, SEA)
    for y0, phase in ((672, 0.0), (708, 1.5)):
        pts = []
        for x in range(0, WIDTH + 1, 8):
            pts.append((x, round(y0 + 8 * math.sin(x / 60.0 + phase))))
        c.polyline(pts, 5, CLOUD)
    c.fill_rect(0, 740, WIDTH - 1, HEIGHT - 1, SAND)
    for (x, y, r) in ((150, 800, 8), (850, 820, 10), (900, 950, 7),
                      (120, 960, 6), (800, 780, 6), (240, 985, 5)):
        c.fill_circle(x, y, r, SAND_DOT)


def draw_palm(c):
    trunk = [(890, 740), (885, 640), (870, 540), (860, 450),
             (855, 380), (853, 330)]
    c.polyline(trunk, 26, PALM_TRUNK)
    top = (853, 330)
    # Six drooping fronds, alternating two greens.
    fronds = [
        ([(853, 330), (780, 280), (700, 270), (630, 300)], PALM_LEAF),
        ([(853, 330), (790, 330), (720, 360), (660, 410)], PALM_LEAF_DARK),
        ([(853, 330), (900, 270), (960, 250), (1010, 270)], PALM_LEAF),
        ([(853, 330), (930, 300), (980, 340), (1010, 400)], PALM_LEAF_DARK),
        ([(853, 330), (830, 250), (800, 200), (760, 170)], PALM_LEAF),
        ([(853, 330), (890, 240), (920, 190), (940, 150)], PALM_LEAF_DARK),
    ]
    for pts, col in fronds:
        c.polyline(pts, 14, col)
    c.fill_circle(845, 348, 16, COCONUT)
    c.fill_circle(876, 352, 15, COCONUT)


def draw_robot_judge(c):
    # --- powdered judge's wig: curls behind the head first.
    for (x, y, r) in ((330, 330, 45), (400, 290, 50), (470, 275, 52),
                      (540, 290, 50), (610, 330, 45)):
        c.fill_circle(x, y, r + 5, WIG_SHADE)
        c.fill_circle(x, y, r, WIG)
    # --- head.
    c.fill_circle(470, 430, 175, NAVY)
    c.fill_circle(470, 430, 170, ROBOT_HEAD)
    # --- side wig curls (locks beside the face).
    for (x, y, r) in ((302, 400, 40), (306, 470, 38),
                      (638, 400, 40), (634, 470, 38)):
        c.fill_circle(x, y, r + 4, WIG_SHADE)
        c.fill_circle(x, y, r, WIG)
    # --- happy closed eyes (upward arcs), wide smile, rosy cheeks.
    c.arc(405, 470, 26, 180, 360, 9, NAVY)
    c.arc(535, 470, 26, 180, 360, 9, NAVY)
    c.arc(470, 500, 68, 15, 165, 11, NAVY)
    c.fill_circle(375, 512, 20, CHEEK)
    c.fill_circle(565, 512, 20, CHEEK)
    # --- neck, robe, collar, medallion.
    c.fill_rect(440, 590, 500, 630, ROBE)
    c.rounded_rect(325, 615, 615, 885, 40, ROBE)
    c.fill_polygon([(425, 618), (470, 618), (470, 668)], COLLAR)
    c.fill_polygon([(515, 618), (470, 618), (470, 668)], COLLAR)
    c.fill_circle(470, 730, 26, GOLD)
    c.fill_circle(470, 730, 12, NAVY)
    c.fill_circle(470, 730, 5, GOLD)
    # --- viewer-left arm, waving hand.
    c.thick_line(345, 660, 265, 780, 34, ROBE)
    c.fill_circle(260, 790, 22, COLLAR)
    # --- viewer-right arm, holding a cocktail.
    c.thick_line(595, 660, 665, 730, 34, ROBE)
    c.thick_line(665, 730, 655, 800, 34, ROBE)
    c.fill_circle(655, 805, 22, COLLAR)
    # --- cocktail glass with a tiny umbrella.
    c.thick_line(700, 772, 700, 726, 6, NAVY)
    c.fill_polygon([(664, 730), (736, 730), (700, 700)], STRAW)
    c.thick_line(716, 776, 736, 732, 7, STRAW)
    c.fill_polygon([(624, 776), (688, 776), (680, 838), (632, 838)], GLASS)
    c.fill_polygon([(630, 808), (682, 808), (678, 834), (634, 834)], DRINK)
    # --- little feet in the sand.
    c.rounded_rect(390, 878, 450, 910, 12, NAVY)
    c.rounded_rect(490, 878, 550, 910, 12, NAVY)
    # --- the gavel, put down for the day (bottom left).
    c.thick_line(150, 892, 208, 842, 14, GAVEL)
    hx, hy = 216, 834
    dx, dy = 30, -30  # 45-degree head, half-length 42 along the diagonal
    px, py = 16, 16
    c.fill_polygon([
        (hx + dx - px, hy + dy - py), (hx + dx + px, hy + dy + py),
        (hx - dx + px, hy - dy + py), (hx - dx - px, hy - dy - py),
    ], GAVEL_HEAD)


def draw_banner(c):
    c.rounded_rect(66, 914, 958, 996, 18, NAVY)
    c.rounded_rect(70, 918, 954, 992, 16, BANNER)
    caption = "VERDICT: HAPPY"
    scale = 10
    x = (WIDTH - c.text_width(caption, scale)) // 2
    y = 918 + (74 - 7 * scale) // 2
    c.text(caption, x, y, scale, NAVY)


def draw_birds(c):
    for (x, y) in ((600, 180), (680, 150)):
        c.thick_line(x - 14, y + 6, x, y - 6, 5, NAVY)
        c.thick_line(x, y - 6, x + 14, y + 6, 5, NAVY)


def main():
    c = Canvas(WIDTH, HEIGHT)
    draw_sky(c)
    draw_sun(c)
    draw_cloud(c, 700, 110, 10)
    draw_cloud(c, 330, 95, 8)
    draw_birds(c)
    draw_sea_and_sand(c)
    draw_palm(c)
    draw_robot_judge(c)
    draw_banner(c)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_png(OUT, WIDTH, HEIGHT, c.px)


if __name__ == "__main__":
    main()
