"""Generate high-quality application icons for SysInfo."""

from pathlib import Path
import math

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow required: pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "gui" / "src-tauri" / "icons"
ICON_DIR.mkdir(parents=True, exist_ok=True)

BG = (12, 11, 10, 255)
BG2 = (22, 20, 18, 255)
GOLD = (201, 162, 39, 255)
GOLD_LIGHT = (232, 196, 90, 255)
COPPER = (168, 98, 52, 255)


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = size // 10
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=size // 5,
        fill=BG,
    )

    inset = pad + size // 28
    draw.rounded_rectangle(
        [inset, inset, size - inset, size - inset],
        radius=size // 6,
        outline=GOLD,
        width=max(2, size // 64),
    )

    cx, cy = size // 2, size // 2
    chip = size // 3
    half = chip // 2

    draw.rounded_rectangle(
        [cx - half, cy - half, cx + half, cy + half],
        radius=size // 40,
        fill=BG2,
        outline=COPPER,
        width=max(2, size // 80),
    )

    inner = half - size // 16
    draw.rectangle(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        fill=(28, 26, 24, 255),
        outline=GOLD,
        width=max(1, size // 128),
    )

    pin_len = size // 14
    pin_w = max(2, size // 64)
    for i in range(8):
        angle = (math.pi * 2 * i) / 8
        px = cx + math.cos(angle) * (half + pin_len * 0.3)
        py = cy + math.sin(angle) * (half + pin_len * 0.3)
        dx = math.cos(angle) * pin_len
        dy = math.sin(angle) * pin_len
        draw.line(
            [(px - dx * 0.4, py - dy * 0.4), (px + dx * 0.6, py + dy * 0.6)],
            fill=GOLD_LIGHT,
            width=pin_w,
        )

    bar_w = max(3, size // 48)
    for i, h_ratio in enumerate([0.35, 0.55, 0.75, 0.5]):
        bx = cx - inner + (i + 1) * (inner * 2 // 5)
        bh = int(inner * 1.6 * h_ratio)
        by = cy + inner - bh
        color = GOLD if i % 2 == 0 else COPPER
        draw.rectangle([bx - bar_w, by, bx + bar_w, cy + inner], fill=color)

    core = size // 14
    draw.ellipse([cx - core, cy - core, cx + core, cy + core], fill=GOLD_LIGHT)

    return img


def save_png(img: Image.Image, path: Path, size: int):
    img.resize((size, size), Image.Resampling.LANCZOS).save(path, "PNG", optimize=True)


def save_ico(source: Image.Image, path: Path):
    sizes = [16, 20, 24, 32, 40, 48, 64, 128, 256]
    icons = [source.resize((s, s), Image.Resampling.LANCZOS) for s in sizes]
    icons[0].save(
        path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=icons[1:],
    )


def main():
    base = draw_icon(1024)
    save_png(base, ICON_DIR / "icon.png", 512)
    save_png(base, ICON_DIR / "32x32.png", 32)
    save_png(base, ICON_DIR / "128x128.png", 128)
    save_png(base, ICON_DIR / "128x128@2x.png", 256)
    save_ico(base, ICON_DIR / "icon.ico")
    print(f"High-quality icons generated in {ICON_DIR}")


if __name__ == "__main__":
    main()
