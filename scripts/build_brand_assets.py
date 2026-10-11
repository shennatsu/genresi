"""Build Genresi logo variants from docs/logo.png."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw


def parse_args() -> argparse.Namespace:
    """Parse the asset builder arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("docs/logo.png"),
        help="Full logo source.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("addons/genresi_base/static/src/img"),
    )
    return parser.parse_args()


def square_icon(image: Image.Image) -> Image.Image:
    """Crop the bread mark and center it on a transparent square canvas."""
    alpha_box = image.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError("Logo source tidak memiliki piksel opaque.")
    content = image.crop(alpha_box)
    icon_width = round(content.width * 0.265)
    icon = content.crop((0, 0, icon_width, content.height))
    icon_box = icon.getchannel("A").getbbox()
    if icon_box is None:
        raise ValueError("Varian ikon tidak memiliki piksel opaque.")
    icon = icon.crop(icon_box)
    padding = round(max(icon.size) * 0.08)
    size = max(icon.size) + padding * 2
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(icon, ((size - icon.width) // 2, (size - icon.height) // 2))
    return canvas


def menu_icon(symbol: str, size: int = 96) -> Image.Image:
    """Build a small Genresi app icon from simple Pillow geometry."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    orange = (214, 124, 37, 255)
    white = (255, 255, 255, 255)
    radius = round(size * 0.2)
    draw.rounded_rectangle((2, 2, size - 3, size - 3), radius=radius, fill=orange)
    margin = round(size * 0.27)
    mid = size // 2
    if symbol == "dashboard":
        for box in (
            (margin, margin, margin + 20, margin + 20),
            (mid + 4, margin, mid + 24, margin + 20),
            (margin, mid + 4, margin + 20, mid + 24),
            (mid + 4, mid + 4, mid + 24, mid + 24),
        ):
            draw.rounded_rectangle(box, radius=4, fill=white)
    elif symbol == "transaction":
        draw.line((margin, mid - 10, size - margin, mid - 10), fill=white, width=7)
        draw.polygon(
            (
                (size - margin, mid - 10),
                (size - margin - 14, mid - 22),
                (size - margin - 14, mid + 2),
            ),
            fill=white,
        )
        draw.line((size - margin, mid + 10, margin, mid + 10), fill=white, width=7)
        draw.polygon(
            ((margin, mid + 10), (margin + 14, mid - 2), (margin + 14, mid + 22)),
            fill=white,
        )
    elif symbol == "partners":
        draw.ellipse((margin + 3, margin, margin + 23, margin + 20), fill=white)
        draw.ellipse((mid + 5, margin, mid + 25, margin + 20), fill=white)
        draw.rounded_rectangle(
            (margin - 2, mid + 4, margin + 27, size - margin), radius=7, fill=white
        )
        draw.rounded_rectangle((mid, mid + 4, mid + 29, size - margin), radius=7, fill=white)
    elif symbol == "stock":
        draw.rectangle((margin, mid - 12, size - margin, size - margin), outline=white, width=6)
        draw.line((margin, mid - 12, mid, margin - 2, size - margin, mid - 12), fill=white, width=6)
        draw.line((mid, margin - 2, mid, size - margin), fill=white, width=6)
    elif symbol == "cash":
        draw.rounded_rectangle(
            (margin, mid - 15, size - margin, mid + 15),
            radius=6,
            outline=white,
            width=6,
        )
        draw.ellipse((mid - 10, mid - 10, mid + 10, mid + 10), outline=white, width=5)
    elif symbol == "report":
        draw.rectangle((margin, margin, size - margin, size - margin), outline=white, width=6)
        draw.line((margin + 10, size - margin - 12, margin + 10, mid + 8), fill=white, width=7)
        draw.line((mid, size - margin - 12, mid, margin + 18), fill=white, width=7)
        draw.line(
            (size - margin - 10, size - margin - 12, size - margin - 10, mid - 4),
            fill=white,
            width=7,
        )
    elif symbol == "settings":
        draw.ellipse((margin, margin, size - margin, size - margin), outline=white, width=8)
        draw.ellipse((mid - 9, mid - 9, mid + 9, mid + 9), fill=white)
        draw_settings_teeth(draw, mid, white)
    else:
        draw.ellipse((mid - 20, mid - 20, mid + 20, mid + 20), fill=white)
    return image


def draw_settings_teeth(draw: ImageDraw.ImageDraw, mid: int, white: tuple) -> None:
    """Draw the eight simple rays used by the configuration icon."""
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        x1 = mid + round(math.cos(radians) * 29)
        y1 = mid + round(math.sin(radians) * 29)
        x2 = mid + round(math.cos(radians) * 39)
        y2 = mid + round(math.sin(radians) * 39)
        draw.line((x1, y1, x2, y2), fill=white, width=7)


def build_sidebar_logo(full_logo: Image.Image) -> Image.Image:
    """Put the proportional full logo on a white, padded canvas."""
    canvas_width = 320
    margin = 16
    content_width = canvas_width - (margin * 2)
    content_height = round(full_logo.height * content_width / full_logo.width)
    resized = full_logo.resize((content_width, content_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (canvas_width, content_height + (margin * 2)), (255, 255, 255, 255))
    canvas.alpha_composite(resized, (margin, margin))
    return canvas


def build_menu_icons(output_dir: Path) -> None:
    """Write the simple icons used by the Genresi root menus."""
    symbols = {
        "root": "dashboard",
        "dashboard": "dashboard",
        "transaction": "transaction",
        "receivable_payable": "partners",
        "stock": "stock",
        "closing": "cash",
        "report": "report",
        "configuration": "settings",
    }
    for name, symbol in symbols.items():
        menu_icon(symbol).save(output_dir / f"genresi_menu_{name}.png", optimize=True)


def build_assets(source: Path, output_dir: Path) -> None:
    """Write logo variants and the Genresi root-menu icons."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        raise FileNotFoundError(f"Logo source tidak ditemukan: {source}")
    with Image.open(source) as opened:
        logo = opened.convert("RGBA")
    alpha_box = logo.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError("Logo source tidak memiliki piksel opaque.")
    full_logo = logo.crop(alpha_box)
    icon = square_icon(logo)
    full_logo.save(output_dir / "genresi_logo.png", optimize=True)
    build_sidebar_logo(full_logo).save(output_dir / "genresi_sidebar_logo.png", optimize=True)
    icon.save(output_dir / "genresi_icon.png", optimize=True)
    icon.resize((64, 64), Image.Resampling.LANCZOS).save(output_dir / "genresi_favicon.ico")
    build_menu_icons(output_dir)
    print(f"Logo dibuat di {output_dir.resolve()}")


if __name__ == "__main__":
    arguments = parse_args()
    build_assets(arguments.source, arguments.output_dir)
