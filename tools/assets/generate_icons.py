from __future__ import annotations

import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw


def crop_to_circle(img: Image.Image) -> Image.Image:
    """Crops an image into a circle with transparency."""
    # Convert image to RGBA if not already
    img = img.convert("RGBA")
    
    # Create circular mask
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    
    # Paste circular cropped image onto a transparent canvas
    round_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    round_img.paste(img, (0, 0), mask=mask)
    return round_img


def main() -> None:
    # 1. Establish paths relative to the repository root
    root = Path(__file__).resolve().parents[2]
    src_png = root / "assets" / "icon.png"
    dest_ico = root / "assets" / "icon.ico"
    app_ico = root / "phonecam" / "assets" / "icon.ico"
    android_res = root / "android" / "phonecam-companion" / "app" / "src" / "main" / "res"

    if not src_png.exists():
        raise FileNotFoundError(f"Source icon not found at: {src_png}")

    print(f"Loading source icon: {src_png}")
    src_image = Image.open(src_png)

    # 2. Generate multi-resolution Windows ICO
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    print(f"Generating Windows ICO file at: {dest_ico}")
    # Pillow can save multi-size ICO directly
    src_image.save(dest_ico, format="ICO", sizes=ico_sizes)
    
    # Copy to phonecam/assets/icon.ico for PyInstaller bundling
    app_ico.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dest_ico, app_ico)
    print(f"Copied ICO to PyInstaller assets: {app_ico}")

    # 3. Generate Android Mipmaps
    # Standard mipmap configurations: (folder_suffix, square/round size)
    mipmap_configs = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    # Generate round source image
    round_source = crop_to_circle(src_image)

    for folder_name, size in mipmap_configs.items():
        folder_path = android_res / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        # Standard Square Icon
        sq_path = folder_path / "ic_launcher.png"
        sq_img = src_image.resize((size, size), Image.Resampling.LANCZOS)
        sq_img.save(sq_path, "PNG")
        print(f"Generated Android Square Launcher: {sq_path} ({size}x{size})")

        # Circular Icon
        rd_path = folder_path / "ic_launcher_round.png"
        rd_img = round_source.resize((size, size), Image.Resampling.LANCZOS)
        rd_img.save(rd_path, "PNG")
        print(f"Generated Android Round Launcher: {rd_path} ({size}x{size})")

    print("Icon generation completed successfully!")


if __name__ == "__main__":
    main()
