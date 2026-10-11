"""Build Genresi logo variants from the supplied transparent logo artwork."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    """Parse the asset builder arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("docs/logo.png"),
        help="Full logo source; docs/logobaked.png is the local fallback.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("addons/genresi_base/static/src/img"),
    )
    return parser.parse_args()


def resolve_source(source: Path) -> Path:
    """Return the requested source or the checked-in local logo fallback."""
    if source.exists():
        return source
    fallback = Path("docs/logobaked.png")
    if fallback.exists():
        print(f"Source {source} tidak ditemukan; memakai {fallback}.")
        return fallback
    raise FileNotFoundError(f"Logo source tidak ditemukan: {source} atau {fallback}")


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


def build_assets(source: Path, output_dir: Path) -> None:
    """Write the full logo, transparent icon, and favicon."""
    output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(resolve_source(source)) as opened:
        logo = opened.convert("RGBA")
    alpha_box = logo.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError("Logo source tidak memiliki piksel opaque.")
    full_logo = logo.crop(alpha_box)
    icon = square_icon(logo)
    full_logo.save(output_dir / "genresi_logo.png", optimize=True)
    icon.save(output_dir / "genresi_icon.png", optimize=True)
    icon.resize((64, 64), Image.Resampling.LANCZOS).save(output_dir / "genresi_favicon.ico")
    print(f"Logo dibuat di {output_dir.resolve()}")


if __name__ == "__main__":
    arguments = parse_args()
    build_assets(arguments.source, arguments.output_dir)
