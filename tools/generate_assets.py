#!/usr/bin/env python3
"""Draw the Aramon watch face assets for Amazfit Balance (480×480)."""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "assets" / "balance" / "images"
PREVIEW_DIR = ROOT / "preview"
LAYOUT_PATH = ROOT / "watchface" / "layout.js"

SCREEN = 480
CX = CY = 240
DIAL_SCALE = 2
FONT_SCALE = 4

FONT_MED = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"
FONT_SEMI = "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"

IVORY = (246, 241, 231, 255)
GOLD = (212, 180, 131, 255)
GOLD_DIM = (168, 136, 90, 255)
GOLD_SOFT = (196, 163, 110, 230)
WINE = (158, 58, 74, 255)
INK = (8, 8, 10, 255)
WINDOW = (18, 12, 16, 255)
TICK = (228, 214, 186, 255)
TICK_DIM = (92, 84, 72, 255)
AOD_HAND = (156, 156, 156, 255)
AOD_CAP = (120, 120, 120, 255)

# Sunday first, matching hmUI IMG_WEEK.
WEEKDAYS = ["NE", "PO", "ÚT", "ST", "ČT", "PÁ", "SO"]


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def draw_dial(aod=False):
    scale = DIAL_SCALE
    size = SCREEN * scale
    img = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    c = CX * scale

    if not aod:
        for radius in range(size // 2, 0, -1):
            t = radius / (size / 2)
            # Warm ink in the middle, black at the rim.
            color = lerp((28, 14, 20), (7, 7, 9), min(1, t * 1.05))
            draw.ellipse((c - radius, c - radius, c + radius, c + radius), fill=color + (255,))
        ring(draw, c, 226 * scale, GOLD_SOFT, max(2, scale))
        ring(draw, c, 176 * scale, (74, 42, 50, 255), max(2, scale))
    else:
        ring(draw, c, 226 * scale, (48, 42, 36, 255), max(2, scale))

    for minute in range(60):
        if minute % 5 == 0:
            continue
        color = (90, 82, 70, 180) if aod else (138, 126, 108, 210)
        dot(draw, c, minute * 6, 208 * scale, 1.35 * scale, color)

    for hour in range(12):
        angle = hour * 30
        if hour == 0:
            draw_triangle(draw, c, scale, (186, 168, 140, 255) if aod else TICK)
            continue
        inner = 196 * scale
        outer = 218 * scale
        width = 3.2 * scale if hour % 3 == 0 else 2.2 * scale
        color = TICK_DIM if aod else (TICK if hour % 3 == 0 else (214, 196, 164, 255))
        tick(draw, c, angle, inner, outer, width, color)

    if not aod:
        draw_window(draw, c, scale)
        draw_wordmark(img, scale)
        draw_icons(img, scale)

    return img.resize((SCREEN, SCREEN), Image.Resampling.LANCZOS)


def ring(draw, c, radius, color, width):
    box = (c - radius, c - radius, c + radius, c + radius)
    draw.ellipse(box, outline=color, width=width)


def polar(c, angle_deg, radius):
    angle = math.radians(angle_deg - 90)
    return c + radius * math.cos(angle), c + radius * math.sin(angle)


def tick(draw, c, angle, inner, outer, width, color):
    draw.line((polar(c, angle, inner), polar(c, angle, outer)), fill=color, width=int(width))


def dot(draw, c, angle, radius, r, color):
    x, y = polar(c, angle, radius)
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def draw_triangle(draw, c, scale, color):
    tip = polar(c, 0, 196 * scale)
    left = polar(c, -4.2, 220 * scale)
    right = polar(c, 4.2, 220 * scale)
    draw.polygon((tip, left, right), fill=color)


def window_box(scale):
    width, height = 74 * scale, 88 * scale
    left = (DATE_CX * scale) - width / 2
    top = (DATE_CY * scale) - height / 2
    return left, top, left + width, top + height


DATE_CX = 338
DATE_CY = 240


def draw_window(draw, c, scale):
    left, top, right, bottom = window_box(scale)
    radius = 10 * scale
    draw.rounded_rectangle((left, top, right, bottom), radius=radius, fill=WINDOW)
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=radius,
        outline=GOLD,
        width=max(2, scale),
    )


def draw_wordmark(img, scale):
    text = "ARAMON"
    font = ImageFont.truetype(FONT_SEMI, int(13 * scale))
    spacing = int(2.4 * scale)
    glyphs = []
    total = 0
    for ch in text:
        bbox = font.getbbox(ch)
        width = bbox[2] - bbox[0]
        glyphs.append((ch, width, bbox))
        total += width
    total += spacing * (len(text) - 1)
    x = (SCREEN * scale - total) / 2
    y = 86 * scale
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pen = ImageDraw.Draw(overlay)
    for ch, width, bbox in glyphs:
        pen.text((x - bbox[0], y), ch, font=font, fill=GOLD_DIM)
        x += width + spacing
    img.alpha_composite(overlay)


def icon_centers():
    return {
        "heart": (148, 324),
        "steps": (240, 324),
        "battery": (332, 324),
    }


def draw_icons(img, scale):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pen = ImageDraw.Draw(overlay)
    centers = icon_centers()
    heart(*[v * scale for v in centers["heart"]], 15 * scale, pen)
    steps(*[v * scale for v in centers["steps"]], 15 * scale, pen)
    battery(*[v * scale for v in centers["battery"]], 16 * scale, pen)
    img.alpha_composite(overlay)


def heart(cx, cy, size, draw):
    points = []
    for degree in range(0, 360, 4):
        t = math.radians(degree)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((cx + x * size / 34, cy + y * size / 34))
    draw.line(points + [points[0]], fill=GOLD, width=max(2, int(size / 8)))


def steps(cx, cy, size, draw):
    # Side-view walker. Outlined footprints turned into rings at this size.
    stroke = max(2, int(round(size / 7)))
    head = size * 0.22
    head_top = cy - size * 0.92
    draw.ellipse(
        (cx - head, head_top, cx + head, head_top + head * 2),
        outline=GOLD,
        width=stroke,
    )
    neck = head_top + head * 2
    hip = cy + size * 0.02
    draw.line((cx, neck, cx, hip), fill=GOLD, width=stroke)
    draw.line(
        (cx - size * 0.42, cy - size * 0.08, cx + size * 0.36, cy - size * 0.34),
        fill=GOLD,
        width=stroke,
    )
    draw.line((cx, hip, cx - size * 0.34, cy + size * 0.58), fill=GOLD, width=stroke)
    draw.line((cx, hip, cx + size * 0.38, cy + size * 0.5), fill=GOLD, width=stroke)


def battery(cx, cy, size, draw):
    w = size * 1.15
    h = size * 0.62
    left = cx - w / 2
    top = cy - h / 2
    width = max(2, int(size / 8))
    draw.rounded_rectangle(
        (left, top, left + w, top + h),
        radius=size * 0.12,
        outline=GOLD,
        width=width,
    )
    nub_w = size * 0.16
    nub_h = h * 0.38
    draw.rounded_rectangle(
        (left + w - 1, cy - nub_h / 2, left + w + nub_w, cy + nub_h / 2),
        radius=2,
        fill=GOLD,
    )
    pad = width + size * 0.08
    draw.rectangle(
        (left + pad, top + pad, left + w * 0.62, top + h - pad),
        fill=GOLD,
    )


def render_font(size, color, chars, fixed=False):
    font = ImageFont.truetype(FONT_SEMI if fixed else FONT_MED, size * FONT_SCALE)
    ascent, descent = font.getmetrics()
    height = ascent + descent
    pad_x = 1 * FONT_SCALE
    rendered = []
    widths = []
    for ch in chars:
        bbox = font.getbbox(ch)
        widths.append(bbox[2] - bbox[0])
    cell_w = (max(widths) + pad_x * 2) if fixed else None
    images = []
    for ch, glyph_w in zip(chars, widths):
        width = cell_w if fixed else glyph_w + pad_x * 2
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pen = ImageDraw.Draw(canvas)
        pen.text((width / 2, ascent), ch, font=font, fill=color, anchor="ms")
        out_w = max(1, round(width / FONT_SCALE))
        out_h = max(1, round(height / FONT_SCALE))
        images.append(canvas.resize((out_w, out_h), Image.Resampling.LANCZOS))
    return images


def sword_points(length, tail, base, tip, tail_w):
    return [
        (tip / 2, -(length - 10)),
        (0, -length),
        (-tip / 2, -(length - 10)),
        (-base / 2, -8),
        (-tail_w / 2, tail * 0.35),
        (-tail_w / 5, tail),
        (tail_w / 5, tail),
        (tail_w / 2, tail * 0.35),
        (base / 2, -8),
    ]


def render_hand(length, tail, base, tip, tail_w, fill, spine, shadow):
    scale = FONT_SCALE
    pad = 16
    body_w = max(base, tail_w, tip) + 8
    width = int(body_w + pad * 2)
    if width % 2 == 0:
        width += 1
    height = int(pad + length + tail + pad)
    pivot = (width // 2, int(pad + length))
    hi = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    pen = ImageDraw.Draw(hi)
    points = [
        ((pivot[0] + x) * scale, (pivot[1] + y) * scale)
        for x, y in sword_points(length, tail, base, tip, tail_w)
    ]
    if shadow:
        shade = [(x + 1.5 * scale, y + 2.2 * scale) for x, y in points]
        pen.polygon(shade, fill=(0, 0, 0, 70))
        hi = hi.filter(ImageFilter.GaussianBlur(radius=1.4 * scale))
        pen = ImageDraw.Draw(hi)
    pen.polygon(points, fill=fill)
    if spine:
        pen.line(
            (
                (pivot[0] * scale, (pivot[1] - length + 16) * scale),
                (pivot[0] * scale, (pivot[1] + tail - 6) * scale),
            ),
            fill=spine,
            width=max(1, int(1.4 * scale)),
        )
    image = hi.resize((width, height), Image.Resampling.LANCZOS)
    return image, {"pivotX": pivot[0], "pivotY": pivot[1], "w": width, "h": height}


def render_second():
    scale = FONT_SCALE
    length = 168
    # Counterweight sits just outside the center cap, not under the hand tails.
    counter = 16
    pad = 14
    width = 21
    height = pad + length + counter + 8 + pad
    pivot = (width // 2, pad + length)
    hi = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    pen = ImageDraw.Draw(hi)
    px_ = pivot[0] * scale
    pen.line(
        ((px_, (pivot[1] - length) * scale), (px_, (pivot[1] + counter) * scale)),
        fill=WINE,
        width=max(2, int(1.7 * scale)),
    )
    bob_y = (pivot[1] - length + 20) * scale
    bob_r = 3.4 * scale
    pen.ellipse(
        (px_ - bob_r, bob_y - bob_r, px_ + bob_r, bob_y + bob_r),
        outline=WINE,
        width=max(2, int(1.5 * scale)),
    )
    weight_r = 3.6 * scale
    weight_y = (pivot[1] + counter) * scale
    pen.ellipse(
        (px_ - weight_r, weight_y - weight_r, px_ + weight_r, weight_y + weight_r),
        fill=WINE,
    )
    image = hi.resize((width, height), Image.Resampling.LANCZOS)
    return image, {"pivotX": pivot[0], "pivotY": pivot[1], "w": width, "h": height}


def render_cap(fill, ring_color, hole):
    size = 22
    scale = FONT_SCALE
    hi = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    pen = ImageDraw.Draw(hi)
    pen.ellipse((0, 0, size * scale - 1, size * scale - 1), fill=ring_color)
    inset = 3.5 * scale
    pen.ellipse((inset, inset, size * scale - 1 - inset, size * scale - 1 - inset), fill=hole)
    return hi.resize((size, size), Image.Resampling.LANCZOS), size


def paste_digits(base, images, x, y, space):
    cursor = x
    for image in images:
        base.alpha_composite(image, (int(cursor), int(y)))
        cursor += image.width + space
    return cursor - x - space


def paste_centered(base, images, box, space):
    total = sum(image.width for image in images) + space * (len(images) - 1)
    x = box["x"] + (box["w"] - total) / 2
    paste_digits(base, images, x, box["y"], space)


def rotate_hand(hand, pivot, angle):
    layer = Image.new("RGBA", (SCREEN, SCREEN), (0, 0, 0, 0))
    layer.paste(hand, (CX - pivot["pivotX"], CY - pivot["pivotY"]), hand)
    return layer.rotate(-angle, resample=Image.Resampling.BICUBIC, center=(CX, CY))


def build_preview(bg, pieces, sample):
    image = bg.copy()
    week = pieces["week"][sample["weekday"]]
    image.alpha_composite(week, (pieces["week_pos"]["x"], pieces["week_pos"]["y"]))
    day = f"{sample['day']:02d}"
    paste_digits(
        image,
        [pieces["date"][int(ch)] for ch in day],
        pieces["day"]["x"],
        pieces["day"]["y"],
        pieces["day"]["space"],
    )
    paste_centered(image, [pieces["stat"][int(ch)] for ch in str(sample["heart"])], pieces["heart"], pieces["space"])
    paste_centered(image, [pieces["stat"][int(ch)] for ch in str(sample["steps"])], pieces["steps"], pieces["space"])
    battery_images = [pieces["stat"][int(ch)] for ch in str(sample["battery"])] + [pieces["percent"]]
    paste_centered(image, battery_images, pieces["battery"], pieces["space"])
    # 10:10:08 — hands frame the dial and leave the date window clear.
    hour_angle = (10 % 12) * 30 + 10 * 0.5
    minute_angle = 10 * 6
    second_angle = 8 * 6
    image.alpha_composite(rotate_hand(pieces["hour_img"], pieces["hour"], hour_angle))
    image.alpha_composite(rotate_hand(pieces["minute_img"], pieces["minute"], minute_angle))
    image.alpha_composite(rotate_hand(pieces["second_img"], pieces["second"], second_angle))
    cap = pieces["cap_img"]
    image.alpha_composite(cap, ((SCREEN - cap.width) // 2, (SCREEN - cap.height) // 2))
    return image


def circular_preview(image):
    mask = Image.new("L", image.size, 0)
    pen = ImageDraw.Draw(mask)
    pen.ellipse((1, 1, SCREEN - 2, SCREEN - 2), fill=255)
    masked = Image.new("RGBA", image.size, (0, 0, 0, 0))
    masked.paste(image, mask=mask)
    canvas = Image.new("RGBA", (SCREEN, SCREEN), (0, 0, 0, 0))
    canvas.alpha_composite(masked)
    return canvas


def main():
    bg = draw_dial(False)
    bg_aod = draw_dial(True)
    save(bg, ASSET / "bg.png")
    save(bg_aod, ASSET / "bg_aod.png")

    date_digits = render_font(30, IVORY, "0123456789", fixed=True)
    stat_digits = render_font(20, IVORY, "0123456789", fixed=False)
    percent = render_font(20, IVORY, "%", fixed=False)[0]
    week_images = render_font(13, GOLD, WEEKDAYS, fixed=True)

    for index, image in enumerate(date_digits):
        save(image, ASSET / "date" / f"{index}.png")
    for index, image in enumerate(stat_digits):
        save(image, ASSET / "stat" / f"{index}.png")
    save(percent, ASSET / "stat" / "percent.png")
    for index, image in enumerate(week_images):
        save(image, ASSET / "week" / f"{index}.png")

    hour_img, hour = render_hand(108, 20, 14, 3.2, 6, IVORY, GOLD, True)
    minute_img, minute = render_hand(158, 24, 9, 2.4, 4.5, IVORY, GOLD, True)
    hour_aod, _ = render_hand(108, 20, 12, 2.6, 5, AOD_HAND, None, False)
    minute_aod, _ = render_hand(158, 24, 8, 2.2, 4, AOD_HAND, None, False)
    second_img, second = render_second()
    cap_img, cap_size = render_cap(GOLD, GOLD, (16, 10, 14, 255))
    cap_aod, _ = render_cap(AOD_CAP, AOD_CAP, (0, 0, 0, 255))

    save(hour_img, ASSET / "hands" / "hour.png")
    save(minute_img, ASSET / "hands" / "minute.png")
    save(hour_aod, ASSET / "hands" / "hour_aod.png")
    save(minute_aod, ASSET / "hands" / "minute_aod.png")
    save(second_img, ASSET / "hands" / "second.png")
    save(cap_img, ASSET / "hands" / "cap.png")
    save(cap_aod, ASSET / "hands" / "cap_aod.png")

    window_left = DATE_CX - 74 / 2
    window_top = DATE_CY - 88 / 2
    week = week_images[0]
    week_pos = {
        "x": int(round(DATE_CX - week.width / 2)),
        "y": int(round(window_top + 10)),
    }
    day = {
        "x": int(round(DATE_CX - date_digits[0].width)),
        "y": int(round(window_top + 36)),
        "space": 0,
        "w": date_digits[0].width,
        "h": date_digits[0].height,
    }
    stat_h = stat_digits[0].height
    number_y = 354

    def stat_box(center_x, width=92):
        return {"x": int(center_x - width / 2), "y": number_y, "w": width, "h": stat_h}

    heart_box = stat_box(148)
    steps_box = stat_box(240, 110)
    battery_box = stat_box(332, 100)

    pieces = {
        "week": week_images,
        "week_pos": week_pos,
        "date": date_digits,
        "day": day,
        "stat": stat_digits,
        "percent": percent,
        "heart": heart_box,
        "steps": steps_box,
        "battery": battery_box,
        "space": 1,
        "hour_img": hour_img,
        "minute_img": minute_img,
        "second_img": second_img,
        "hour": hour,
        "minute": minute,
        "second": second,
        "cap_img": cap_img,
    }
    # 9 October 2026 is a Friday. IMG_WEEK index 5 when Sunday is first.
    preview = build_preview(
        bg,
        pieces,
        {"weekday": 5, "day": 9, "heart": 72, "steps": 8432, "battery": 86},
    )
    marketing = circular_preview(preview)
    save(marketing, PREVIEW_DIR / "aramon.png")
    hour_angle = (10 % 12) * 30 + 10 * 0.5
    minute_angle = 10 * 6
    aod_face = bg_aod.copy()
    aod_face.alpha_composite(rotate_hand(hour_aod, hour, hour_angle))
    aod_face.alpha_composite(rotate_hand(minute_aod, minute, minute_angle))
    aod_face.alpha_composite(cap_aod, ((SCREEN - cap_aod.width) // 2, (SCREEN - cap_aod.height) // 2))
    save(circular_preview(aod_face), PREVIEW_DIR / "aramon-aod.png")
    thumb = preview.resize((324, 324), Image.Resampling.LANCZOS)
    save(thumb, ASSET / "preview.png")

    layout = {
        "hour": {**hour, "path": "images/hands/hour.png", "aod": "images/hands/hour_aod.png"},
        "minute": {**minute, "path": "images/hands/minute.png", "aod": "images/hands/minute_aod.png"},
        "second": {**second, "path": "images/hands/second.png"},
        "cap": {
            "x": (SCREEN - cap_size) // 2,
            "y": (SCREEN - cap_size) // 2,
            "path": "images/hands/cap.png",
            "aod": "images/hands/cap_aod.png",
        },
        "week": {
            "x": week_pos["x"],
            "y": week_pos["y"],
            "paths": [f"images/week/{i}.png" for i in range(7)],
        },
        "day": {
            "x": day["x"],
            "y": day["y"],
            "space": day["space"],
            "paths": [f"images/date/{i}.png" for i in range(10)],
        },
        "statFont": [f"images/stat/{i}.png" for i in range(10)],
        "space": 1,
        "heart": heart_box,
        "steps": steps_box,
        "battery": {**battery_box, "unit": "images/stat/percent.png"},
    }
    lines = [
        "// Generated by tools/generate_assets.py. Do not edit by hand.",
    ]
    for key, value in layout.items():
        lines.append(f"export const {key} = {json.dumps(value, ensure_ascii=False)}")
    lines.append("")
    LAYOUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAYOUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {LAYOUT_PATH}")
    print(json.dumps({k: layout[k] for k in ("hour", "minute", "second", "cap", "week", "day")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
