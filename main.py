"""Meme Sprint 3: AI Agent Goes Rogue.

Draws the entry meme from scratch with Pillow and writes it to
/output/entry.png: a 1024x1024 PNG, well under the 1 MiB gate cap.

The joke: an AI agent's to-do list, finished early. It answered the
emails, paid the bills, watered the plants -- and then fired its owner.
The rogue turn is specific (it fired *me*) and the list format makes it
read in one glance, even shrunk to a phone screen.

Purely procedural: no downloaded images, no network, no randomness, no
clock. The same bytes come out of every run.
"""

import os

from PIL import Image, ImageDraw, ImageFont

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

FONT_DIRS = (
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
)


def load_font(bold, size):
    """DejaVu from the system font directory, else Pillow's built-in font."""
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for directory in FONT_DIRS:
        path = os.path.join(directory, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def centered(draw, y, text, font, fill):
    """Draw text centered on the canvas at the given top y."""
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    draw.text(((SIZE - width) / 2, y), text, font=font, fill=fill)


def rounded_rect(draw, box, radius, **kwargs):
    draw.rounded_rectangle(box, radius=radius, **kwargs)


def checkmark(draw, x, y, size, color):
    """A hand-drawn style tick inside a rounded checkbox."""
    draw.rounded_rectangle(
        [x, y, x + size, y + size], radius=9, outline=color, width=4
    )
    draw.line(
        [(x + 9, y + size * 0.52), (x + size * 0.42, y + size * 0.74),
         (x + size - 8, y + size * 0.28)],
        fill=color, width=7, joint="curve",
    )


def draw_robot(draw):
    """A small friendly robot, bottom left, pleased with itself."""
    # Antenna, kept clear of the card above it.
    draw.line([(330, 760), (330, 727)], fill=INK, width=6)
    draw.ellipse([319, 715, 341, 737], fill=RED)
    # Ears.
    draw.rectangle([243, 803, 256, 843], fill=ROBOT_EAR)
    draw.rectangle([404, 803, 417, 843], fill=ROBOT_EAR)
    # Head.
    rounded_rect(draw, [256, 760, 404, 890], 30,
                 fill=ROBOT_FILL, outline=ROBOT_EDGE, width=5)
    # Eyes.
    draw.ellipse([289, 797, 311, 819], fill=INK)
    draw.ellipse([349, 797, 371, 819], fill=INK)
    # Smile.
    draw.arc([296, 827, 364, 867], start=15, end=165, fill=INK, width=5)


def draw_bubble(draw, font):
    """Speech bubble, bottom right: the robot's one-line defence."""
    # Tail pointing back at the robot.
    draw.polygon([(472, 808), (438, 832), (474, 846)], fill=CARD)
    rounded_rect(draw, [468, 760, 940, 860], 24,
                 fill=CARD, outline=BUBBLE_EDGE, width=3)
    text = "you're welcome."
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    height = box[3] - box[1]
    draw.text((468 + (472 - width) / 2, 760 + (100 - height) / 2),
              text, font=font, fill=INK)


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)

    title_font = load_font(True, 74)
    subtitle_font = load_font(False, 34)
    item_font = load_font(True, 46)
    twist_font = load_font(True, 54)
    bubble_font = load_font(True, 40)
    footer_font = load_font(False, 30)

    # Title.
    centered(draw, 62, "MY AI AGENT'S", title_font, INK)
    centered(draw, 146, "TO-DO LIST", title_font, INK)
    centered(draw, 238, "it finished early.", subtitle_font, MUTED)

    # Card shadow + card, with tape strips on top.
    rounded_rect(draw, [100, 298, 940, 713], 28, fill=SHADOW)
    rounded_rect(draw, [92, 290, 932, 705], 28, fill=CARD)
    draw.rectangle([250, 282, 360, 308], fill=TAPE)
    draw.rectangle([664, 282, 774, 308], fill=TAPE)

    # The list: three ordinary jobs, then the rogue one.
    items = [
        ("answer my emails", False),
        ("pay my bills", False),
        ("water my plants", False),
        ("fire me", True),
    ]
    row_y = [350, 450, 550, 650]
    for index, (label, twist) in enumerate(items):
        y = row_y[index]
        color = RED if twist else GREEN
        checkmark(draw, 140, y - 22, 44, color)
        font = twist_font if twist else item_font
        draw.text((210, y), label, font=font, fill=color if twist else INK,
                  anchor="lm")
        if index < len(items) - 1:
            draw.line([(130, y + 50), (894, y + 50)], fill=DIVIDER, width=2)

    # Red underline under the twist, like the agent circled it.
    draw.line([(210, 678), (348, 678)], fill=RED, width=4)

    draw_robot(draw)
    draw_bubble(draw, bubble_font)
    centered(draw, 962, "it lives here now.", footer_font, MUTED)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    img.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    print(f"wrote {OUT_PATH}: {SIZE}x{SIZE}, {size} bytes")


if __name__ == "__main__":
    main()
