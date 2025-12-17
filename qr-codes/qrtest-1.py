"""Generate a fullscreen demo of QR codes in black/white and custom colors."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_H


LINK = "https://neoclassical.ai"
OUTPUT_PATH = Path(__file__).parent / "qrtest-1-output.png"
CANVAS_SIZE = (1920, 1080)


def make_qr(size: int, *, fill_color: str, back_color: str) -> Image.Image:
    """Create a single QR code pre-sized by resizing after generation."""
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=2)
    qr.add_data(LINK)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    return img.resize((size, size), Image.NEAREST)


def draw_section_annotation(draw: ImageDraw.Draw, text: str, position: tuple[int, int]) -> None:
    """Draw a small white header for each section."""
    font = ImageFont.load_default()
    draw.text(position, text, font=font, fill=(255, 255, 255))


def compose_canvas() -> Image.Image:
    """Build the full-screen composition with the requested QR variants."""
    canvas = Image.new("RGB", CANVAS_SIZE, (12, 12, 12))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    draw_section_annotation(draw, "Black & White QR variations", (60, 40))

    bw_sizes = [380, 260, 200]
    x_offset = 60
    y_offset = 100
    for size in bw_sizes:
        qr_img = make_qr(size, fill_color="black", back_color="white")
        canvas.paste(qr_img, (x_offset, y_offset))
        label = f"{size}px classic"
        draw.text(
            (x_offset, y_offset + size + 8),
            label,
            font=font,
            fill=(230, 230, 230),
        )
        x_offset += size + 60

    draw_section_annotation(draw, "Color & styled QR variations", (60, 520))
    style_defs = [
        ("#ff2d55", "#fefcd7", 320, "Warm gradient"),
        ("#0a84ff", "#0b0b2b", 240, "Neon on deep space"),
        ("#3ddc84", "#0a1f0d", 180, "Emerald halo"),
    ]
    color_x = 60
    color_y = 580
    for fill_color, back_color, size, caption in style_defs:
        qr_img = make_qr(size, fill_color=fill_color, back_color=back_color)
        canvas.paste(qr_img, (color_x, color_y))
        draw.text((color_x, color_y + size + 8), caption, font=font, fill=(255, 255, 255))
        color_x += size + 80

    # Add footer text describing the payload.
    footer_text = f"Payload: {LINK} · Error correction: High"
    text_bbox = draw.textbbox((0, 0), footer_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.rectangle(
        (60, CANVAS_SIZE[1] - text_height - 30, 60 + text_width + 16, CANVAS_SIZE[1] - 20),
        fill=(255, 255, 255, 25),
    )
    draw.text((68, CANVAS_SIZE[1] - text_height - 24), footer_text, font=font, fill=(16, 16, 16))

    return canvas


def main() -> None:
    """Entrypoint to render and store the QR collage."""
    output = compose_canvas()
    output.save(OUTPUT_PATH)
    print(f"Saved QR collage to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
