#!/usr/bin/env python3
"""Generate per-OS UI screenshots and a combined thumbnail in WEBP format."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Iterable, List

from PIL import Image, ImageDraw, ImageFilter, ImageFont


CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720


def _font(size: int) -> Any:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _draw_rounded_box(
    draw: Any,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def generate_os_screenshot(os_name: str, output_file: Path) -> None:
    os_label = os_name.strip().lower()
    if not os_label:
        raise ValueError("OS name cannot be empty")

    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), (26, 28, 33))
    draw = ImageDraw.Draw(image)

    for y in range(CANVAS_HEIGHT):
        ratio = y / max(CANVAS_HEIGHT - 1, 1)
        r = int(20 + ratio * 14)
        g = int(22 + ratio * 12)
        b = int(27 + ratio * 8)
        draw.line([(0, y), (CANVAS_WIDTH, y)], fill=(r, g, b))

    panel = (315, 18, 980, 665)
    _draw_rounded_box(draw, panel, radius=7, fill=(42, 43, 48), outline=(57, 58, 64))

    # Simulate OS-specific title bar accents to keep images distinct by platform.
    if os_label == "macos":
        titlebar = (315, 18, 980, 52)
        _draw_rounded_box(draw, titlebar, radius=7, fill=(52, 53, 60), outline=(67, 68, 74))
        draw.ellipse((332, 30, 344, 42), fill=(255, 95, 87))
        draw.ellipse((350, 30, 362, 42), fill=(254, 189, 46))
        draw.ellipse((368, 30, 380, 42), fill=(40, 201, 64))
    elif os_label == "windows":
        titlebar = (315, 18, 980, 52)
        _draw_rounded_box(draw, titlebar, radius=7, fill=(48, 50, 57), outline=(67, 68, 74))
        draw.text((910, 27), "_   □   X", fill=(190, 196, 204), font=_font(14))
    else:
        titlebar = (315, 18, 980, 52)
        _draw_rounded_box(draw, titlebar, radius=7, fill=(47, 49, 56), outline=(67, 68, 74))
        draw.text((908, 27), "-   []   x", fill=(190, 196, 204), font=_font(14))

    title_font = _font(24)
    text_font = _font(20)
    small_font = _font(16)

    header_text = "0 passwords loaded successfully!"
    draw.text((458, 74), header_text, fill=(240, 245, 250), font=small_font)

    _draw_rounded_box(draw, (380, 110, 564, 146), radius=7, fill=(54, 56, 62), outline=(95, 97, 103))
    draw.text((392, 121), "Search", fill=(180, 185, 195), font=small_font)

    _draw_rounded_box(draw, (685, 110, 938, 146), radius=9, fill=(28, 99, 161), outline=(36, 124, 200))
    draw.text((787, 121), "Search", fill=(232, 240, 250), font=small_font)

    _draw_rounded_box(draw, (332, 178, 962, 535), radius=4, fill=(47, 49, 55), outline=(62, 64, 72))
    _draw_rounded_box(draw, (332, 178, 618, 222), radius=4, fill=(34, 36, 41), outline=(50, 52, 58))

    draw.text((356, 190), "Address", fill=(225, 232, 240), font=text_font)
    draw.text((470, 190), "User", fill=(225, 232, 240), font=text_font)
    draw.text((560, 190), "Password", fill=(225, 232, 240), font=text_font)

    _draw_rounded_box(draw, (948, 208, 955, 510), radius=2, fill=(116, 120, 128))
    _draw_rounded_box(draw, (336, 518, 932, 524), radius=2, fill=(116, 120, 128))

    _draw_rounded_box(draw, (365, 568, 525, 607), radius=9, fill=(28, 99, 161), outline=(36, 124, 200))
    draw.text((425, 579), "Remove", fill=(232, 240, 250), font=small_font)

    _draw_rounded_box(draw, (690, 568, 935, 607), radius=9, fill=(28, 99, 161), outline=(36, 124, 200))
    draw.text((802, 579), "Add", fill=(232, 240, 250), font=small_font)

    _draw_rounded_box(draw, (470, 616, 823, 694), radius=5, fill=(36, 39, 45), outline=(57, 61, 70))
    _draw_rounded_box(draw, (482, 628, 810, 662), radius=8, fill=(28, 99, 161), outline=(36, 124, 200))
    _draw_rounded_box(draw, (482, 668, 810, 692), radius=8, fill=(28, 99, 161), outline=(36, 124, 200))
    draw.text((554, 636), "Generate a Simple Password", fill=(232, 240, 250), font=small_font)
    draw.text((550, 672), "Generate a Complex Password", fill=(232, 240, 250), font=small_font)

    badge_text = os_label.upper()
    badge_w = max(120, len(badge_text) * 14)
    badge = (38, 30, 38 + badge_w, 76)
    _draw_rounded_box(draw, badge, radius=11, fill=(30, 85, 130), outline=(44, 122, 186))
    draw.text((56, 43), badge_text, fill=(235, 244, 255), font=title_font)

    shadow = image.filter(ImageFilter.GaussianBlur(radius=1.2))
    image = Image.blend(shadow, image, alpha=0.88)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_file, format="WEBP", quality=92, method=6)


def compose_thumbnail(input_files: Iterable[Path], output_file: Path) -> None:
    existing_files: List[Path] = [path for path in input_files if path.exists()]
    if not existing_files:
        raise FileNotFoundError("No input screenshots were found to compose thumbnail")

    opened = [Image.open(path).convert("RGB") for path in existing_files]
    try:
        target_height = 320
        spacing = 24
        padding = 28

        resized: List[Image.Image] = []
        for image in opened:
            ratio = target_height / image.height
            new_size = (int(image.width * ratio), target_height)
            resized.append(image.resize(new_size, Image.Resampling.LANCZOS))

        content_width = sum(image.width for image in resized) + spacing * (len(resized) - 1)
        width = content_width + padding * 2
        height = target_height + padding * 2 + 38

        canvas = Image.new("RGB", (width, height), (22, 24, 30))
        draw = ImageDraw.Draw(canvas)

        for y in range(height):
            ratio = y / max(height - 1, 1)
            draw.line([(0, y), (width, y)], fill=(int(18 + ratio * 10), int(21 + ratio * 8), int(29 + ratio * 6)))

        caption_font = _font(22)
        caption = "Passwords Manager - Multi-platform UI"
        draw.text((padding, 8), caption, fill=(230, 236, 245), font=caption_font)

        x = padding
        y = padding + 32
        for image, source in zip(resized, existing_files):
            shadow_box = (x + 6, y + 6, x + image.width + 6, y + image.height + 6)
            draw.rounded_rectangle(shadow_box, radius=10, fill=(0, 0, 0))
            canvas.paste(image, (x, y))

            label = source.stem.capitalize()
            label_y = y + image.height - 30
            draw.rectangle((x + 10, label_y, x + 120, label_y + 24), fill=(20, 20, 20))
            draw.text((x + 16, label_y + 3), label, fill=(245, 245, 245), font=_font(16))
            x += image.width + spacing

        output_file.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_file, format="WEBP", quality=92, method=6)
    finally:
        for image in opened:
            image.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate per-OS screenshots and release thumbnail")
    parser.add_argument("--os", dest="os_name", help="Operating system label for screenshot name/content")
    parser.add_argument("--output", required=True, help="Output WEBP file path")
    parser.add_argument(
        "--compose-thumbnail",
        action="store_true",
        help="Compose a thumbnail from existing images",
    )
    parser.add_argument(
        "--inputs",
        nargs="*",
        default=[],
        help="Input WEBP files used only with --compose-thumbnail",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    output = Path(args.output)

    if args.compose_thumbnail:
        compose_thumbnail((Path(path) for path in args.inputs), output)
        return

    if not args.os_name:
        raise SystemExit("--os is required when not using --compose-thumbnail")

    generate_os_screenshot(args.os_name, output)


if __name__ == "__main__":
    main()
