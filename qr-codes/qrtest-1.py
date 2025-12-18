"""Generate a fullscreen demo of high-contrast QR codes using vivid palettes."""

from pathlib import Path

import argparse
from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_H


LINK = "https://neoclassical.ai"
OUTPUT_PATH = Path(__file__).parent / "qrtest-1-output.png"
CANVAS_SIZE = (1920, 1080)

PURE_RED = "#ff0000"
PURE_BLUE = "#0000ff"
PURE_PURPLE = "#ff00ff"

TOP_BLOCK_DEFS = [
    ((PURE_RED, PURE_BLUE, PURE_PURPLE), "white", 600, 48, "Large block mix (R→B→P)"),
    ((PURE_BLUE, PURE_PURPLE, PURE_RED), "white", 420, 40, "Large block mix (B→P→R)"),
    ((PURE_PURPLE, PURE_RED, PURE_BLUE), "white", 320, 32, "Large block mix (P→R→B)"),
]

BOTTOM_BLOCK_DEFS = [
    ((PURE_RED, PURE_BLUE, PURE_PURPLE), "white", 240, 32, "Block mix (R→B→P)"),
    ((PURE_BLUE, PURE_PURPLE, PURE_RED), "white", 180, 24, "Block mix (B→P→R)"),
    ((PURE_PURPLE, PURE_RED, PURE_BLUE), "white", 120, 16, "Block mix (P→R→B)"),
]


def make_qr(size: int, *, fill_color: str, back_color: str, data: str) -> Image.Image:
    """Create a single QR code pre-sized by resizing after generation."""
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    return img.resize((size, size), Image.NEAREST)


def make_block_pattern(size: int, palette: tuple[str, ...], block_size: int) -> Image.Image:
    """Draw a tiled pattern of solid palette colors."""
    pattern = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(pattern)
    palette_rgb = [ImageColor.getrgb(color) for color in palette]
    rows = cols = (size + block_size - 1) // block_size
    for row in range(rows):
        y0 = row * block_size
        y1 = min(y0 + block_size, size)
        for col in range(cols):
            x0 = col * block_size
            x1 = min(x0 + block_size, size)
            color = palette_rgb[(row + col) % len(palette_rgb)]
            draw.rectangle(
                (x0, y0, x1 - 1, y1 - 1),
                fill=color,
            )
    return pattern


def make_block_qr(
    size: int,
    *,
    palette: tuple[str, ...],
    back_color: str,
    block_size: int,
    payload: str,
) -> Image.Image:
    """Composite a tiled color pattern into the QR modules."""
    base = make_qr(size, fill_color="black", back_color="white", data=payload)
    mask = ImageChops.invert(base.convert("L"))
    pattern = make_block_pattern(size, palette, block_size)
    background = Image.new("RGB", (size, size), back_color)
    return Image.composite(pattern, background, mask)


def slugify(text: str) -> str:
    """Produce a filesystem-friendly identifier from a caption."""
    cleaned: list[str] = []
    last_was_dash = False
    for char in text.lower():
        if char.isalnum():
            cleaned.append(char)
            last_was_dash = False
        else:
            if not last_was_dash:
                cleaned.append("-")
                last_was_dash = True
    slug = "".join(cleaned).strip("-")
    return slug or "qr"


def save_block_variant(image: Image.Image, size: int, caption: str) -> None:
    """Save the QR image to disk with the size and caption encoded in the filename."""
    filename = f"qrtest-1-block-{size}px-{slugify(caption)}.png"
    output_path = Path(__file__).parent / filename
    image.save(output_path)


def draw_label(draw: ImageDraw.Draw, text: str, position: tuple[int, int], font: ImageFont.ImageFont) -> None:
    """Render legible text above QR codes with a low-contrast background."""
    padding = 6
    text_bbox = draw.textbbox(position, text, font=font)
    rect = (
        text_bbox[0] - padding,
        text_bbox[1] - padding,
        text_bbox[2] + padding,
        text_bbox[3] + padding,
    )
    draw.rectangle(rect, fill=(0, 0, 0, 190))
    draw.text(position, text, font=font, fill=(255, 255, 255))


def draw_section_annotation(draw: ImageDraw.Draw, text: str, position: tuple[int, int]) -> None:
    """Draw a small white header for each section."""
    font = ImageFont.load_default()
    draw.text(position, text, font=font, fill=(255, 255, 255))


def compose_canvas(payload: str) -> Image.Image:
    """Build the full-screen composition with the requested QR variants."""
    canvas = Image.new("RGB", CANVAS_SIZE, (12, 12, 12))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    draw_section_annotation(draw, "Large block QR variations", (60, 40))
    top_y_offset = 120
    max_top_size = max(size for (_, _, size, _, _) in TOP_BLOCK_DEFS)
    top_x_offset = 60
    for palette, back_color, size, block_size, caption in TOP_BLOCK_DEFS:
        qr_img = make_block_qr(
            size,
            palette=palette,
            back_color=back_color,
            block_size=block_size,
            payload=payload,
        )
        canvas.paste(qr_img, (top_x_offset, top_y_offset))
        label_text = f"{size} pix"
        draw_label(draw, label_text, (top_x_offset, top_y_offset + size + 8), font)
        save_block_variant(qr_img, size, caption)
        top_x_offset += size + 60

    style_defs = BOTTOM_BLOCK_DEFS
    bottom_block_height = max(size for (_, _, size, _, _) in style_defs)
    min_bottom_start = top_y_offset + max_top_size + 60
    color_y = max(CANVAS_SIZE[1] - bottom_block_height - 80, min_bottom_start)
    bottom_header_y = color_y - 60
    draw_section_annotation(draw, "Color & styled QR variations", (60, bottom_header_y))
    color_x = 60
    for palette, back_color, size, block_size, caption in style_defs:
        qr_img = make_block_qr(
            size,
            palette=palette,
            back_color=back_color,
            block_size=block_size,
            payload=payload,
        )
        canvas.paste(qr_img, (color_x, color_y))
        draw_label(draw, f"{size} pix", (color_x, color_y + size + 8), font)
        save_block_variant(qr_img, size, caption)
        color_x += size + 80

    # Add footer text describing the payload.
    footer_text = f"Payload: {payload} · Error correction: High"
    text_bbox = draw.textbbox((0, 0), footer_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.rectangle(
        (60, CANVAS_SIZE[1] - text_height - 30, 60 + text_width + 16, CANVAS_SIZE[1] - 20),
        fill=(255, 255, 255, 25),
    )
    draw.text((68, CANVAS_SIZE[1] - text_height - 24), footer_text, font=font, fill=(16, 16, 16))

    return canvas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument(
        "--payload",
        "-p",
        default=LINK,
        help="Data (URL or text) to encode in all QR variants.",
    )
    return parser.parse_args()


def main() -> None:
    """Entrypoint to render and store the QR collage."""
    args = parse_args()
    output = compose_canvas(args.payload)
    output.save(OUTPUT_PATH)
    print(f"Saved QR collage to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
