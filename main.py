"""Meme Sprint 3: AI Agent Goes Rogue.

Draws the entry meme from scratch and writes it to /output/entry.png:
a 1024x1024 PNG, well under the 1 MiB gate cap.

The joke: an AI agent's to-do list, finished early. It answered the
emails, paid the bills, watered the plants -- and then fired its owner.
The rogue turn is specific (it fired *me*) and the list format makes it
read in one glance, even shrunk to a phone screen.

Standard library only, on purpose. The first submission of this entry
was refused because its grade run exited 1: the grader's pinned
python3.13 image carries no Pillow and no DejaVu fonts, so the entry
now draws with its own pixel canvas, its own embedded bitmap font, and
its own PNG encoder. No third-party package, no font file on disk, no
network, no randomness, no clock. The same bytes come out of every run.
"""

import binascii
import math
import os
import struct
import zlib

SIZE = 1024
OUT_PATH = "/output/entry.png"

# Palette: warm paper, dark slate ink, green checks, one red twist.
# All solid RGB: a translucent shadow flattened to RGB turns black, so
# the shadow here is a solid warm grey instead.
PAPER = (251, 246, 236)
INK = (31, 41, 55)
MUTED = (107, 114, 128)
CARD = (255, 255, 255)
SHADOW = (228, 223, 211)
DIVIDER = (229, 231, 235)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
TAPE = (232, 221, 196)
ROBOT_FILL = (219, 234, 254)
ROBOT_EDGE = (59, 130, 246)
ROBOT_EAR = (147, 197, 253)
BUBBLE_EDGE = (148, 163, 184)

# Embedded bitmap font: 7 wide, 9 tall per glyph, '#' set, '.' clear.
# Only the characters this meme needs. Lowercase sits on rows 2-7 with
# ascenders on rows 0-1 and descenders on row 8.
FONT = {
    "A": ("..###..", ".#...#.", ".#...#.", ".#...#.", ".#####.", ".#...#.",
          ".#...#.", ".#...#.", ".#...#."),
    "B": (".####..", ".#...#.", ".#...#.", ".#...#.", ".####..", ".#...#.",
          ".#...#.", ".#...#.", ".####.."),
    "D": (".####..", ".#...#.", ".#...#.", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", ".####.."),
    "E": (".#####.", ".#.....", ".#.....", ".#.....", ".####..", ".#.....",
          ".#.....", ".#.....", ".#####."),
    "G": ("..###..", ".#...#.", ".#.....", ".#.....", ".#..##.", ".#...#.",
          ".#...#.", ".#...#.", "..###.."),
    "I": ("..###..", "...#...", "...#...", "...#...", "...#...", "...#...",
          "...#...", "...#...", "..###.."),
    "L": (".#.....", ".#.....", ".#.....", ".#.....", ".#.....", ".#.....",
          ".#.....", ".#.....", ".#####."),
    "M": (".#...#.", ".##.##.", ".#.#.#.", ".#.#.#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", ".#...#."),
    "N": (".#...#.", ".##..#.", ".#.#.#.", ".#..##.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", ".#...#."),
    "O": ("..###..", ".#...#.", ".#...#.", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", "..###.."),
    "S": ("..####.", ".#...#.", ".#.....", ".###...", "...##..", "....#..",
          "....#..", ".#...#.", ".####.."),
    "T": (".#####.", "...#...", "...#...", "...#...", "...#...", "...#...",
          "...#...", "...#...", "...#..."),
    "Y": (".#...#.", ".#...#.", ".#...#.", "..#.#..", "...#...", "...#...",
          "...#...", "...#...", "...#..."),
    "a": (".......", ".......", "..###..", ".#...#.", ".....#.", "..####.",
          ".#...#.", ".#...#.", "..###.."),
    "b": (".#.....", ".#.....", ".####..", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", ".####.."),
    "c": (".......", ".......", "..###..", ".#...#.", ".#.....", ".#.....",
          ".#.....", ".#...#.", "..###.."),
    "d": (".....#.", ".....#.", "..###..", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", "..###.."),
    "e": (".......", ".......", "..###..", ".#...#.", ".#####.", ".#.....",
          ".#.....", ".#...#.", "..###.."),
    "f": ("...##..", "..#....", "..#....", ".####..", "..#....", "..#....",
          "..#....", "..#....", "..#...."),
    "h": (".#.....", ".#.....", ".####..", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", ".#...#."),
    "i": (".......", "...#...", ".......", "..##...", "...#...", "...#...",
          "...#...", "...#...", "..###.."),
    "l": ("..##...", "...#...", "...#...", "...#...", "...#...", "...#...",
          "...#...", "...#...", "..###.."),
    "m": (".......", ".......", ".##.##.", ".#.#.#.", ".#.#.#.", ".#.#.#.",
          ".#.#.#.", ".#.#.#.", ".#.#.#."),
    "n": (".......", ".......", ".####..", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", ".#...#."),
    "o": (".......", ".......", "..###..", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", "..###.."),
    "p": (".......", ".......", ".####..", ".#...#.", ".#...#.", ".#...#.",
          ".####..", ".#.....", ".#....."),
    "r": (".......", ".......", ".####..", ".#...#.", ".#.....", ".#.....",
          ".#.....", ".#.....", ".#....."),
    "s": (".......", ".......", "..####.", ".#...#.", ".#.....", "..##...",
          "....#..", ".#...#.", ".####.."),
    "t": ("...#...", "...#...", ".####..", "...#...", "...#...", "...#...",
          "...#...", "...#...", "...#..."),
    "u": (".......", ".......", ".#...#.", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", ".#...#.", "..###.."),
    "v": (".......", ".......", ".#...#.", ".#...#.", ".#...#.", ".#...#.",
          ".#...#.", "..#.#..", "...#..."),
    "w": (".......", ".......", ".#...#.", ".#...#.", ".#...#.", ".#.#.#.",
          ".#.#.#.", ".##.##.", ".#...#."),
    "y": (".......", ".......", ".#...#.", ".#...#.", ".#...#.", ".#...#.",
          "..###..", "...#...", "..#...."),
    "'": ("...#...", "...#...", "...#...", ".......", ".......", ".......",
          ".......", ".......", "......."),
    "-": (".......", ".......", ".......", ".......", ".#####.", ".......",
          ".......", ".......", "......."),
    ".": (".......", ".......", ".......", ".......", ".......", ".......",
          ".......", "..##...", "..##..."),
}

# --- pixel canvas -----------------------------------------------------

BUF = bytearray(SIZE * SIZE * 3)


def _clip(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def fill_rect(x0, y0, x1, y1, color):
    """Fill the rectangle [x0, x1) x [y0, y1) with a solid color."""
    x0 = _clip(x0, 0, SIZE)
    y0 = _clip(y0, 0, SIZE)
    x1 = _clip(x1, 0, SIZE)
    y1 = _clip(y1, 0, SIZE)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for y in range(y0, y1):
        start = (y * SIZE + x0) * 3
        BUF[start:start + len(row)] = row


def set_pixel(x, y, color):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        start = (y * SIZE + x) * 3
        BUF[start:start + 3] = bytes(color)


def filled_circle(cx, cy, radius, color):
    for dy in range(-radius, radius + 1):
        dx = math.isqrt(radius * radius - dy * dy)
        fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)


def _line_points(x0, y0, x1, y1):
    """Bresenham points from (x0, y0) to (x1, y1)."""
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return points


def thick_line(x0, y0, x1, y1, color, width):
    radius = max(1, width // 2)
    for px, py in _line_points(x0, y0, x1, y1):
        filled_circle(px, py, radius, color)


def rounded_rect(x0, y0, x1, y1, radius, color):
    """Fill a rounded rectangle (inclusive x0/y0, exclusive x1/y1)."""
    fill_rect(x0 + radius, y0, x1 - radius, y1, color)
    fill_rect(x0, y0 + radius, x1, y1 - radius, color)
    for cx, cy in ((x0 + radius, y0 + radius), (x1 - radius, y0 + radius),
                   (x0 + radius, y1 - radius), (x1 - radius, y1 - radius)):
        filled_circle(cx, cy, radius, color)


def rounded_rect_outline(x0, y0, x1, y1, radius, color, width, bg):
    """A rounded-rectangle border: outer fill, inner fill in bg."""
    rounded_rect(x0, y0, x1, y1, radius, color)
    inset = width
    rounded_rect(x0 + inset, y0 + inset, x1 - inset, y1 - inset,
                 max(0, radius - inset), bg)


def arc(cx, cy, rx, ry, start_deg, end_deg, color, width):
    """An elliptical arc (screen angles, y down), drawn thick."""
    radius = max(1, width // 2)
    for deg in range(start_deg, end_deg + 1, 2):
        rad = math.radians(deg)
        px = int(round(cx + rx * math.cos(rad)))
        py = int(round(cy + ry * math.sin(rad)))
        filled_circle(px, py, radius, color)


def fill_polygon(points, color):
    """Scanline fill for a simple polygon (list of (x, y))."""
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if y0 == y1:
                continue
            if min(y0, y1) <= y < max(y0, y1):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(int(math.ceil(xs[i])), y,
                      int(math.floor(xs[i + 1])) + 1, y + 1, color)


# --- text ---------------------------------------------------------------

def text_width(text, scale):
    return len(text) * 8 * scale - scale


def draw_text(x, y, text, scale, color):
    """Draw text with its top-left at (x, y)."""
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            x += 8 * scale
            continue
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "#":
                    fill_rect(x + col * scale, y + row * scale,
                              x + (col + 1) * scale, y + (row + 1) * scale,
                              color)
        x += 8 * scale


def centered(y, text, scale, color):
    draw_text((SIZE - text_width(text, scale)) // 2, y, text, scale, color)


# --- meme parts ---------------------------------------------------------

def checkmark(x, y, size, color):
    """A hand-drawn style tick inside a rounded checkbox."""
    rounded_rect_outline(x, y, x + size, y + size, 9, color, 4, CARD)
    thick_line(x + 9, int(y + size * 0.52), int(x + size * 0.42),
              int(y + size * 0.74), color, 7)
    thick_line(int(x + size * 0.42), int(y + size * 0.74),
              x + size - 8, int(y + size * 0.28), color, 7)


def draw_robot():
    """A small friendly robot, bottom left, pleased with itself."""
    # Antenna, kept clear of the card above it.
    thick_line(330, 760, 330, 727, INK, 6)
    filled_circle(330, 726, 11, RED)
    # Ears.
    fill_rect(243, 803, 256, 843, ROBOT_EAR)
    fill_rect(404, 803, 417, 843, ROBOT_EAR)
    # Head.
    rounded_rect_outline(256, 760, 404, 890, 30, ROBOT_EDGE, 5, ROBOT_FILL)
    # Eyes.
    filled_circle(300, 808, 11, INK)
    filled_circle(360, 808, 11, INK)
    # Smile.
    arc(330, 847, 34, 20, 15, 165, INK, 5)


def draw_bubble():
    """Speech bubble, bottom right: the robot's one-line defence."""
    text = "you're welcome."
    scale = 3
    # Tail pointing back at the robot.
    fill_polygon([(472, 808), (438, 832), (474, 846)], CARD)
    rounded_rect_outline(468, 760, 940, 860, 24, BUBBLE_EDGE, 3, CARD)
    width = text_width(text, scale)
    height = 9 * scale
    x = 468 + (472 - width) // 2
    y = 760 + (100 - height) // 2
    draw_text(x, y, text, scale, INK)


# --- PNG (standard library only) ----------------------------------------

def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    return out


def png_bytes():
    raw = bytearray()
    stride = SIZE * 3
    for y in range(SIZE):
        raw.append(0)
        raw += BUF[y * stride:(y + 1) * stride]
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", compressed) + _chunk(b"IEND", b""))


# --- entry ---------------------------------------------------------------

def main():
    fill_rect(0, 0, SIZE, SIZE, PAPER)

    # Title.
    centered(62, "MY AI AGENT'S", 7, INK)
    centered(146, "TO-DO LIST", 7, INK)
    centered(238, "it finished early.", 4, MUTED)

    # Card shadow + card, with tape strips on top.
    rounded_rect(100, 298, 940, 713, 28, SHADOW)
    rounded_rect(92, 290, 932, 705, 28, CARD)
    fill_rect(250, 282, 360, 308, TAPE)
    fill_rect(664, 282, 774, 308, TAPE)

    # The list: three ordinary jobs, then the rogue one.
    items = [
        ("answer my emails", False, 5),
        ("pay my bills", False, 5),
        ("water my plants", False, 5),
        ("fire me", True, 6),
    ]
    row_y = [350, 450, 550, 650]
    for index, (label, twist, scale) in enumerate(items):
        y = row_y[index]
        color = RED if twist else GREEN
        checkmark(140, y - 22, 44, color)
        cell = 9 * scale
        draw_text(210, y - cell // 2, label, scale,
                  color if twist else INK)
        if index < len(items) - 1:
            thick_line(130, y + 50, 894, y + 50, DIVIDER, 2)

    # Red underline under the twist, like the agent circled it.
    thick_line(210, 678, 210 + text_width("fire me", 6), 678, RED, 4)

    draw_robot()
    draw_bubble()
    centered(962, "it lives here now.", 3, MUTED)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    data = png_bytes()
    with open(OUT_PATH, "wb") as f:
        f.write(data)
    print(f"wrote {OUT_PATH}: {SIZE}x{SIZE}, {len(data)} bytes")


if __name__ == "__main__":
    main()
