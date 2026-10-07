"""
Generates high-resolution multi-size Windows .ico files for:
1. VirtualDesktopWorkspaceManager.ico (Main app icon)
2. VirtualDesktopWorkspaceManager_Configure.ico (Configure GUI - blue accent with gear/layout)
3. VirtualDesktopWorkspaceManager_Run.ico (Run Workspace - green accent with launch arrow)
"""

from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]


def create_base_canvas(size: int = 256) -> Image.Image:
    # RGBA transparent canvas
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def generate_main_icon() -> Image.Image:
    img = create_base_canvas(256)
    draw = ImageDraw.Draw(img)

    # Background rounded square with dark slate blue gradient
    draw.rounded_rectangle([16, 16, 240, 240], radius=48, fill=(24, 30, 42, 255), outline=(0, 120, 212, 255), width=6)

    # Four virtual desktop rectangles (2x2 grid)
    # Top-Left (Desktop 1 - Blue)
    draw.rounded_rectangle([40, 40, 118, 118], radius=16, fill=(0, 120, 212, 220), outline=(96, 180, 255, 255), width=3)
    # Top-Right (Desktop 2 - Purple)
    draw.rounded_rectangle([138, 40, 216, 118], radius=16, fill=(136, 23, 152, 220), outline=(200, 120, 240, 255), width=3)
    # Bottom-Left (Desktop 3 - Cyan)
    draw.rounded_rectangle([40, 138, 118, 216], radius=16, fill=(0, 153, 188, 220), outline=(80, 220, 240, 255), width=3)
    # Bottom-Right (Desktop 4 - Green)
    draw.rounded_rectangle([138, 138, 216, 216], radius=16, fill=(16, 124, 65, 220), outline=(100, 220, 140, 255), width=3)

    return img


def generate_configure_icon() -> Image.Image:
    img = create_base_canvas(256)
    draw = ImageDraw.Draw(img)

    # Background rounded square (Deep Blue)
    draw.rounded_rectangle([16, 16, 240, 240], radius=48, fill=(15, 23, 42, 255), outline=(0, 120, 215, 255), width=6)

    # Virtual desktop tiles
    draw.rounded_rectangle([36, 36, 120, 120], radius=14, fill=(30, 58, 138, 200), outline=(59, 130, 246, 255), width=3)
    draw.rounded_rectangle([136, 36, 220, 120], radius=14, fill=(30, 58, 138, 200), outline=(59, 130, 246, 255), width=3)
    draw.rounded_rectangle([36, 136, 120, 220], radius=14, fill=(30, 58, 138, 200), outline=(59, 130, 246, 255), width=3)

    # Gear / Settings accent badge on bottom right
    center_x, center_y = 178, 178
    # Outer circle for gear
    draw.ellipse([center_x - 48, center_y - 48, center_x + 48, center_y + 48], fill=(0, 120, 215, 255), outline=(255, 255, 255, 255), width=4)
    # Gear teeth simulation (crosses)
    draw.rounded_rectangle([center_x - 14, center_y - 56, center_x + 14, center_y + 56], radius=4, fill=(0, 120, 215, 255))
    draw.rounded_rectangle([center_x - 56, center_y - 14, center_x + 56, center_y + 14], radius=4, fill=(0, 120, 215, 255))
    # Gear center hole
    draw.ellipse([center_x - 18, center_y - 18, center_x + 18, center_y + 18], fill=(15, 23, 42, 255), outline=(255, 255, 255, 255), width=3)

    # Slider/controls lines inside top-left desktop tile
    draw.line([52, 60, 104, 60], fill=(147, 197, 253, 255), width=4)
    draw.ellipse([64, 54, 76, 66], fill=(255, 255, 255, 255))
    draw.line([52, 80, 104, 80], fill=(147, 197, 253, 255), width=4)
    draw.ellipse([84, 74, 96, 86], fill=(255, 255, 255, 255))
    draw.line([52, 100, 104, 100], fill=(147, 197, 253, 255), width=4)
    draw.ellipse([60, 94, 72, 106], fill=(255, 255, 255, 255))

    return img


def generate_run_icon() -> Image.Image:
    img = create_base_canvas(256)
    draw = ImageDraw.Draw(img)

    # Background rounded square (Deep Emerald Dark)
    draw.rounded_rectangle([16, 16, 240, 240], radius=48, fill=(10, 35, 24, 255), outline=(16, 185, 129, 255), width=6)

    # Virtual desktop tiles
    draw.rounded_rectangle([36, 36, 120, 120], radius=14, fill=(6, 78, 59, 200), outline=(16, 185, 129, 255), width=3)
    draw.rounded_rectangle([136, 36, 220, 120], radius=14, fill=(6, 78, 59, 200), outline=(16, 185, 129, 255), width=3)
    draw.rounded_rectangle([36, 136, 120, 220], radius=14, fill=(6, 78, 59, 200), outline=(16, 185, 129, 255), width=3)

    # Play/Rocket Launch Triangle Badge on bottom right
    badge_x, badge_y = 178, 178
    # Outer circle for play badge
    draw.ellipse([badge_x - 48, badge_y - 48, badge_x + 48, badge_y + 48], fill=(16, 185, 129, 255), outline=(255, 255, 255, 255), width=4)

    # Play triangle pointing right
    triangle_pts = [
        (badge_x - 16, badge_y - 26),
        (badge_x + 28, badge_y),
        (badge_x - 16, badge_y + 26)
    ]
    draw.polygon(triangle_pts, fill=(255, 255, 255, 255))

    # Fast forward ticks in top tiles
    draw.line([54, 78, 86, 78], fill=(167, 243, 208, 255), width=5)
    draw.polygon([(86, 70), (102, 78), (86, 86)], fill=(167, 243, 208, 255))

    return img


def save_icon(img: Image.Image, output_path: Path):
    img.save(output_path, format="ICO", sizes=SIZES)
    print(f"Generated icon: {output_path}")


def main():
    main_ico = generate_main_icon()
    config_ico = generate_configure_icon()
    run_ico = generate_run_icon()

    save_icon(main_ico, ASSETS_DIR / "VirtualDesktopWorkspaceManager.ico")
    save_icon(config_ico, ASSETS_DIR / "VirtualDesktopWorkspaceManager_Configure.ico")
    save_icon(run_ico, ASSETS_DIR / "VirtualDesktopWorkspaceManager_Run.ico")


if __name__ == "__main__":
    main()
