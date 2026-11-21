#!/usr/bin/env python3
"""Sum up 20 November 2026's world news in one image.

A front page drawn from scratch with the Python standard library only:
a tiny 5x7 bitmap font, a small raster canvas, and a hand-written PNG
encoder. No network, no files read, no randomness, no clock: the same
bytes come out of every run.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 227)
INK = (20, 20, 20)
RED = (179, 35, 27)
BLUE = (29, 78, 137)
TEAL = (15, 118, 110)
GREEN = (34, 120, 60)
ORANGE = (214, 110, 20)
GREY = (110, 108, 100)
LIGHT = (232, 226, 208)
GOLD = (212, 160, 23)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, "." off, "#" on. Text is rendered in capitals.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", ".####", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "*": (".....", "#.#.#", ".###.", "#.#.#", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
    "\u00d7": (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."),
    "\u00b7": (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    "\u2192": (".....", "..#..", "...#.", "#####", "...#.", "..#..", "....."),
}

CHAR_W = 6  # glyph cell width in font units (5 + 1 gap)


def text_width(s, scale):
    return max(0, len(s) * CHAR_W * scale - scale)


def wrap_text(s, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines = []
    for para in s.split("\n"):
        line = ""
        for word in para.split(" "):
            trial = word if not line else line + " " + word
            if text_width(trial, scale) <= max_w or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


# -------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - thick // 2, y - thick // 2, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def _circle_rows(self, cx, cy, r):
        rows = []
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            rows.append((cy + dy, cx - dx, cx + dx))
        return rows

    def fill_circle(self, cx, cy, r, color):
        for y, x0, x1 in self._circle_rows(cx, cy, r):
            self.hline(x0, y, x1 - x0 + 1, color)

    def circle(self, cx, cy, r, color, thick=1):
        for y, x0, x1 in self._circle_rows(cx, cy, r):
            self.fill_rect(x0, y, thick, 1, color)
            self.fill_rect(x1 - thick + 1, y, thick, 1, color)

    def fill_poly(self, pts, color):
        # Even-odd scanline fill for a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), color)

    def star(self, cx, cy, r_out, r_in, points, color, rot=-90):
        import math
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(rot + i * 180 / points)
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.fill_poly(pts, color)

    def text(self, x, y, s, scale, color, align="l"):
        if align == "c":
            x -= text_width(s, scale) // 2
        elif align == "r":
            x -= text_width(s, scale)
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "#":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, color
                        )
            cx += CHAR_W * scale
        return cx

    def text_block(self, x, y, s, scale, color, max_w, leading=None, align="l"):
        if leading is None:
            leading = 9 * scale
        yy = y
        for line in wrap_text(s, scale, max_w):
            self.text(x, yy, line, scale, color, align=align)
            yy += leading
        return yy


# ----------------------------------------------------------------- png
def _chunk(kind, data):
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_png(path, canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride : (y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + _chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ------------------------------------------------------- illustrations
def draw_courthouse(c, x, y, w, h, color):
    """A classical courthouse: pediment, four columns, three steps."""
    # Pediment triangle.
    c.fill_poly([(x + w // 2, y), (x + 8, y + h // 3), (x + w - 8, y + h // 3)], color)
    c.fill_circle(x + w // 2, y + h // 6, 7, PAPER)
    c.fill_circle(x + w // 2, y + h // 6, 4, color)
    # Columns.
    col_w, gap = 14, (w - 4 * 14) // 5
    top = y + h // 3 + 6
    base = y + h - 18
    for i in range(4):
        cx = x + gap + i * (14 + gap)
        c.fill_rect(cx, top, col_w, base - top, color)
        c.fill_rect(cx - 3, top - 4, col_w + 6, 4, color)
        c.fill_rect(cx - 3, base, col_w + 6, 4, color)
    # Steps.
    c.fill_rect(x, y + h - 12, w, 4, color)
    c.fill_rect(x + 10, y + h - 6, w - 20, 4, color)
    c.fill_rect(x + 20, y + h - 2, w - 40, 2, color)


def draw_flags(c, x, y, w, h):
    """Three small flags: USA, China, Russia, with labels beneath."""
    fw, gap = (w - 2 * 10) // 3, 10
    # USA: stripes + canton.
    fx = x
    for i in range(7):
        y0 = y + i * h // 7
        y1 = y + (i + 1) * h // 7
        c.fill_rect(fx, y0, fw, y1 - y0, RED if i % 2 == 0 else PAPER)
    c.fill_rect(fx, y, fw // 2, h // 2, BLUE)
    for r in range(3):
        for col in range(4):
            c.fill_rect(fx + 6 + col * 11, y + 5 + r * 9, 3, 3, PAPER)
    # China: red field, one large star + four small.
    fx = x + fw + gap
    c.fill_rect(fx, y, fw, h, RED)
    c.star(fx + 22, y + 22, 11, 5, 5, GOLD)
    for sx, sy in ((52, 10), (64, 20), (64, 34), (52, 44)):
        c.star(fx + sx, y + sy, 5, 2, 5, GOLD)
    # Russia: white / blue / red thirds.
    fx = x + 2 * (fw + gap)
    c.fill_rect(fx, y, fw, h // 3 + 1, PAPER)
    c.fill_rect(fx, y + h // 3, fw, h // 3 + 1, BLUE)
    c.fill_rect(fx, y + 2 * h // 3, fw, h - 2 * h // 3, RED)
    for fx, label in (
        (x, "USA"),
        (x + fw + gap, "CHINA"),
        (x + 2 * (fw + gap), "RUSSIA"),
    ):
        c.rect(fx, y, fw, h, INK, 2)
        c.text(fx + fw // 2, y + h + 8, label, 2, INK, align="c")


def draw_cyclone(c, x, y, w, h, color):
    """A spiral storm seen from above, stretched across the strip."""
    cx, cy = x + w // 2, y + h // 2 + 2
    import math

    for k in range(5):
        r = 4 + k * 5
        a0 = k * 55
        pts = []
        for a in range(a0, a0 + 260, 6):
            rad = math.radians(a)
            rr = r * (0.55 + 0.45 * (a - a0) / 260)
            pts.append((
                int(cx + rr * math.cos(rad) * 2.2),
                int(cy + rr * math.sin(rad) * 0.85),
            ))
        for i in range(len(pts) - 1):
            c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, 4)
    c.fill_circle(cx, cy, 6, RED)


def draw_bridge(c, x, y, w, h, color):
    """A river bridge: three arches under a deck, an explosion above."""
    import math

    deck = y + h - 12
    c.fill_rect(x, deck, w, 5, color)
    for ax in (x + w // 6, x + w // 2, x + 5 * w // 6):
        pts = []
        for a in range(180, 361, 6):
            rad = math.radians(a)
            pts.append((int(ax + 26 * math.cos(rad)), int(deck - 26 * math.sin(rad))))
        for i in range(len(pts) - 1):
            c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, 3)
        c.fill_rect(ax - 3, deck - 26, 6, 26, color)
    c.fill_rect(x, deck + 5, 6, h - deck - 5, color)
    c.fill_rect(x + w - 6, deck + 5, 6, h - deck - 5, color)
    c.star(x + w // 2, y + 14, 18, 7, 8, ORANGE)
    c.star(x + w // 2, y + 14, 9, 4, 8, RED)


def draw_falling_chart(c, x, y, w, h, color):
    """Axes and a jagged line falling left to right."""
    c.line(x, y + h - 8, x + w, y + h - 8, GREY, 2)
    c.line(x, y, x, y + h - 8, GREY, 2)
    pts = [
        (x + 6, y + 8),
        (x + w // 4, y + 14),
        (x + w // 2, y + 26),
        (x + 3 * w // 4, y + 30),
        (x + w - 10, y + h - 16),
    ]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, 3)
    for px, py in pts:
        c.fill_circle(px, py, 4, color)
    c.text(x + w - 56, y + 2, "-4.8%", 2, color)


def draw_rising_chart(c, x, y, w, h, color):
    """Bars and a rising line, for a market debut."""
    bw = 18
    heights = (14, 22, 18, 30, 40)
    for i, hh in enumerate(heights):
        bx = x + 8 + i * (bw + 8)
        c.fill_rect(bx, y + h - 8 - hh, bw, hh, BLUE if i < 4 else GREEN)
    pts = [(x + 8 + i * (bw + 8) + bw // 2, y + h - 14 - hh) for i, hh in enumerate(heights)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GREEN, 3)
    c.text(x + w - 46, y + 2, "+17%", 2, GREEN)


def draw_tower(c, x, y, w, h, color):
    """A tall tower with blown-out floors and smoke."""
    tx, tw = x + w // 2 - 20, 40
    c.fill_rect(tx, y + 6, tw, h - 6, color)
    for row in range(6):
        for col in range(4):
            wx = tx + 5 + col * 9
            wy = y + 10 + row * 6
            if row in (2, 3):
                c.fill_rect(wx, wy, 5, 4, ORANGE)  # damaged floors
            else:
                c.fill_rect(wx, wy, 5, 4, PAPER)
    c.fill_rect(tx - 4, y + 2, tw + 8, 4, color)
    c.fill_rect(tx - 6, y + h - 2, tw + 12, 2, color)
    c.fill_circle(tx - 16, y + 10, 7, GREY)
    c.fill_circle(tx - 26, y + 2, 5, GREY)
    c.fill_circle(tx + tw + 16, y + 14, 6, GREY)


def draw_globe(c, x, y, w, h, color):
    """A globe with a small flame crossed out: fossil fuels dropped."""
    cx, cy, r = x + w // 2 - 34, y + h // 2, 22
    c.circle(cx, cy, r, color, 3)
    for k in range(1, 3):
        c.line(cx - r + k * (2 * r) // 3, cy - r, cx - r + k * (2 * r) // 3, cy + r, color, 2)
    c.line(cx - r, cy, cx + r, cy, color, 2)
    # Flame, crossed out.
    fx, fy = x + w - 44, y + h // 2
    c.fill_poly(
        [(fx, fy - 16), (fx + 10, fy - 2), (fx + 6, fy + 8), (fx + 12, fy + 12),
         (fx + 2, fy + 18), (fx - 8, fy + 12), (fx - 4, fy + 4)],
        ORANGE,
    )
    c.line(fx - 16, fy - 22, fx + 16, fy + 22, RED, 4)
    c.line(fx + 16, fy - 22, fx - 16, fy + 22, RED, 4)


# ---------------------------------------------------------------- page
def card(c, x, y, w, h, kicker, headline, sub, art):
    c.rect(x, y, w, h, INK, 2)
    c.text(x + 12, y + 12, kicker, 2, RED)
    yy = y + 36
    for line in wrap_text(headline, 3, w - 24):
        c.text(x + 12, yy, line, 3, INK)
        yy += 26
    c.text_block(x + 12, yy + 6, sub, 2, INK, w - 24, leading=18)
    art(c, x + 12, y + h - 62, w - 24, 50, INK)


def build():
    c = Canvas(W, H, PAPER)
    c.rect(10, 10, W - 20, H - 20, INK, 3)

    # Masthead.
    c.text(512, 32, "THE WORLD IN ONE DAY", 5, INK, align="c")
    c.text(512, 80, "FRIDAY, 20 NOVEMBER 2026", 3, RED, align="c")
    c.hline(28, 116, W - 56, INK, 3)
    c.hline(28, 122, W - 56, INK, 1)

    # Lead: the court ruling, left; the Shenzhen summit, right.
    c.text(28, 138, "THE HAGUE  \u2022  JUSTICE", 2, RED)
    c.text(28, 162, "MYANMAR GUILTY", 4, INK)
    c.text(28, 196, "OF GENOCIDE", 4, INK)
    c.text_block(
        28, 242,
        "World court rules the state responsible for crimes "
        "against the Rohingya and orders reparations.",
        2, INK, 560, leading=18,
    )
    draw_courthouse(c, 60, 300, 520, 128, BLUE)

    c.vline(628, 134, 300, GREY, 2)
    c.text(644, 138, "SHENZHEN  \u2022  SUMMIT", 2, RED)
    c.text(644, 162, "THREE LEADERS,", 3, INK)
    c.text(644, 190, "ONE DECLARATION", 3, INK)
    c.text_block(
        644, 226,
        "Trump, Xi and Putin promise nuclear-risk talks and "
        "UN reform after their first three-way meeting.",
        2, INK, 330, leading=18,
    )
    draw_flags(c, 644, 306, 352, 62)

    c.hline(28, 448, W - 56, INK, 3)

    # Row two.
    card(c, 28, 462, 312, 216, "INDIA  \u2022  WEATHER",
         "CYCLONE AKVAN HITS INDIA",
         "Landfall near Gopalpur; 300,000 in shelters; winds hit 90 km/h.",
         draw_cyclone)
    card(c, 356, 462, 312, 216, "UKRAINE  \u2022  WAR",
         "KYIV BRIDGES STRUCK",
         "Russian missiles hit three bridges overnight; at least eight killed.",
         draw_bridge)
    card(c, 684, 462, 312, 216, "MARKETS  \u2022  ECONOMY",
         "STOCKS SLIDE WORLDWIDE",
         "S&P 500 down 2% for a fifth day; Nikkei falls 4.8% in Tokyo.",
         draw_falling_chart)

    # Row three.
    card(c, 28, 692, 312, 216, "SAUDI ARABIA  \u2022  CONFLICT",
         "MISSILE HITS RIYADH TOWER",
         "Houthi strike damages the PIF Tower in Riyadh; no injuries.",
         draw_tower)
    card(c, 356, 692, 312, 216, "TURKIYE  \u2022  CLIMATE",
         "COP31 DROPS FOSSIL FUELS",
         "Draft deal in Antalya erases every mention of coal, oil and gas.",
         draw_globe)
    card(c, 684, 692, 312, 216, "TECH  \u2022  MARKETS",
         "ANTHROPIC'S BIG DEBUT",
         "Claude maker closes 17% above its $83 IPO price on Nasdaq.",
         draw_rising_chart)

    # Footer: the rest of the day.
    c.hline(28, 922, W - 56, INK, 3)
    c.text(512, 934, "ALSO ON 20 NOVEMBER", 2, RED, align="c")
    c.text(512, 958, "KENYA EBOLA-FREE  \u2022  GAZA YELLOW LINE CROSSED  \u2022  FAA GROUND STOP STRANDS 1.5M",
           2, INK, align="c")
    c.text(512, 978, "ITALY FINES META 805M EUROS  \u2022  BUKELE SEEKS THIRD TERM",
           2, INK, align="c")
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    size = write_png(target, build())
    if size > 1048576:
        raise SystemExit(f"entry.png too big: {size} bytes")
    print(f"wrote {target} ({size} bytes)")


if __name__ == "__main__":
    main()
