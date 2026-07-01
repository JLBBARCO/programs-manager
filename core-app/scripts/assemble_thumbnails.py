#!/usr/bin/env python3
"""Normalize screenshots and assemble the website/platform thumbnail."""

import argparse
import os
from pathlib import Path

from PIL import Image, ImageOps


def load_image(path: str | None) -> Image.Image | None:
    if not path or not os.path.exists(path):
        return None
    try:
        return Image.open(path).convert("RGB")
    except Exception as error:
        print(f"Failed to open {path}: {error}")
        return None


def fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)


def save_if_source(source: str | None, destination: str, size: tuple[int, int]) -> None:
    image = load_image(source)
    if image is None:
        return
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    fit_image(image, size).save(destination, "WEBP", quality=86)


def compose_grid(paths: list[str], output: str, cell_size: tuple[int, int], spacing: int = 14) -> None:
    images: list[Image.Image] = []
    for path in paths:
        image = load_image(path)
        if image is None:
            image = Image.new("RGB", cell_size, (246, 247, 249))
        images.append(fit_image(image, cell_size))

    width = cell_size[0] * 2 + spacing
    height = cell_size[1] * 2 + spacing
    canvas = Image.new("RGB", (width, height), (255, 255, 255))

    positions = [(0, 0), (cell_size[0] + spacing, 0), (0, cell_size[1] + spacing), (cell_size[0] + spacing, cell_size[1] + spacing)]
    for image, position in zip(images, positions):
        canvas.paste(image, position)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "WEBP", quality=86)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows")
    parser.add_argument("--linux")
    parser.add_argument("--site")
    parser.add_argument("--out-windows", default="src/assets/img/windows.webp")
    parser.add_argument("--out-linux", default="src/assets/img/linux.webp")
    parser.add_argument("--out-site", default="src/assets/img/site.webp")
    parser.add_argument("--output", default="src/assets/img/thumbnail.webp")
    args = parser.parse_args()

    cell_size = (960, 540)
    save_if_source(args.windows, args.out_windows, cell_size)
    save_if_source(args.linux, args.out_linux, cell_size)
    save_if_source(args.site, args.out_site, cell_size)

    compose_grid(
        [args.out_windows, args.out_linux, args.out_site],
        args.output,
        cell_size,
    )


if __name__ == "__main__":
    main()
