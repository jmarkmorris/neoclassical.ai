import math
import os

try:
    import tkinter as tk
except Exception:
    tk = None


WINDOW_BG = "#0b0e1a"
STROKE = "#f5f7ff"
LINE_WIDTH = 2


def draw_gear(canvas, cx, cy, size):
    outer_r = size * 0.30
    inner_r = size * 0.14
    tooth_len = size * 0.08
    tooth_w = size * 0.10
    teeth = 8
    for i in range(teeth):
        angle = i * 2 * math.pi / teeth
        ux = math.cos(angle)
        uy = math.sin(angle)
        px = -uy
        py = ux
        tx = cx + ux * (outer_r + tooth_len / 2)
        ty = cy + uy * (outer_r + tooth_len / 2)
        half_w = tooth_w / 2
        half_l = tooth_len / 2
        points = [
            tx + px * half_w + ux * half_l,
            ty + py * half_w + uy * half_l,
            tx - px * half_w + ux * half_l,
            ty - py * half_w + uy * half_l,
            tx - px * half_w - ux * half_l,
            ty - py * half_w - uy * half_l,
            tx + px * half_w - ux * half_l,
            ty + py * half_w - uy * half_l,
        ]
        canvas.create_polygon(
            points,
            outline=STROKE,
            fill="",
            width=LINE_WIDTH,
            joinstyle=tk.ROUND,
        )
    canvas.create_oval(
        cx - outer_r,
        cy - outer_r,
        cx + outer_r,
        cy + outer_r,
        outline=STROKE,
        width=LINE_WIDTH,
    )
    canvas.create_oval(
        cx - inner_r,
        cy - inner_r,
        cx + inner_r,
        cy + inner_r,
        outline=STROKE,
        width=LINE_WIDTH,
    )


def draw_sliders(canvas, cx, cy, size):
    length = size * 0.6
    offsets = [-size * 0.16, 0, size * 0.16]
    knob_positions = [-size * 0.12, size * 0.18, -size * 0.02]
    for offset, knob in zip(offsets, knob_positions):
        y = cy + offset
        canvas.create_line(
            cx - length / 2,
            y,
            cx + length / 2,
            y,
            fill=STROKE,
            width=LINE_WIDTH,
            capstyle=tk.ROUND,
        )
        canvas.create_oval(
            cx + knob - size * 0.06,
            y - size * 0.06,
            cx + knob + size * 0.06,
            y + size * 0.06,
            outline=STROKE,
            width=LINE_WIDTH,
        )


def draw_orbit_ring(canvas, cx, cy, size):
    ring_r = size * 0.34
    node_r = size * 0.06
    canvas.create_oval(
        cx - ring_r,
        cy - ring_r,
        cx + ring_r,
        cy + ring_r,
        outline=STROKE,
        width=LINE_WIDTH,
    )
    for angle in (math.pi / 2, math.pi * 1.25, math.pi * 1.75):
        nx = cx + math.cos(angle) * ring_r
        ny = cy + math.sin(angle) * ring_r
        canvas.create_oval(
            nx - node_r,
            ny - node_r,
            nx + node_r,
            ny + node_r,
            fill=STROKE,
            outline=STROKE,
            width=0,
        )


def draw_concentric(canvas, cx, cy, size):
    outer_r = size * 0.34
    inner_r = size * 0.18
    dot_r = size * 0.04
    canvas.create_oval(
        cx - outer_r,
        cy - outer_r,
        cx + outer_r,
        cy + outer_r,
        outline=STROKE,
        width=LINE_WIDTH,
    )
    canvas.create_oval(
        cx - inner_r,
        cy - inner_r,
        cx + inner_r,
        cy + inner_r,
        outline=STROKE,
        width=LINE_WIDTH,
    )
    canvas.create_oval(
        cx - dot_r,
        cy - dot_r,
        cx + dot_r,
        cy + dot_r,
        fill=STROKE,
        outline=STROKE,
        width=0,
    )


def draw_grid(canvas, cx, cy, size):
    gap = size * 0.12
    dot = size * 0.08
    start_x = cx - gap
    start_y = cy - gap
    for row in range(3):
        for col in range(3):
            x = start_x + col * gap
            y = start_y + row * gap
            canvas.create_rectangle(
                x - dot / 2,
                y - dot / 2,
                x + dot / 2,
                y + dot / 2,
                outline=STROKE,
                width=LINE_WIDTH,
            )


def draw_compass(canvas, cx, cy, size):
    outer_r = size * 0.34
    needle_len = size * 0.22
    needle_w = size * 0.08
    canvas.create_oval(
        cx - outer_r,
        cy - outer_r,
        cx + outer_r,
        cy + outer_r,
        outline=STROKE,
        width=LINE_WIDTH,
    )
    points = [
        cx,
        cy - needle_len,
        cx - needle_w / 2,
        cy,
        cx,
        cy + needle_len * 0.2,
        cx + needle_w / 2,
        cy,
    ]
    canvas.create_polygon(
        points,
        outline=STROKE,
        fill="",
        width=LINE_WIDTH,
        joinstyle=tk.ROUND,
    )


def draw_icon_grid(canvas, icons, cols, cell_w, cell_h, icon_size):
    for idx, (label, painter) in enumerate(icons):
        col = idx % cols
        row = idx // cols
        cx = col * cell_w + cell_w / 2
        cy = row * cell_h + cell_h / 2 - 10
        painter(canvas, cx, cy, icon_size)
        canvas.create_text(
            cx,
            cy + icon_size * 0.42,
            text=label,
            fill=STROKE,
            font=("Helvetica", 12),
        )


def svg_circle(cx, cy, r, stroke=STROKE, fill="none", width=LINE_WIDTH):
    return (
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
        f'stroke="{stroke}" stroke-width="{width}" fill="{fill}" '
        'stroke-linecap="round" stroke-linejoin="round" />'
    )


def svg_line(x1, y1, x2, y2, stroke=STROKE, width=LINE_WIDTH):
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" />'
    )


def svg_rect(x, y, w, h, stroke=STROKE, fill="none", width=LINE_WIDTH):
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'stroke="{stroke}" stroke-width="{width}" fill="{fill}" />'
    )


def svg_polygon(points, stroke=STROKE, fill="none", width=LINE_WIDTH):
    points_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return (
        f'<polygon points="{points_str}" stroke="{stroke}" '
        f'stroke-width="{width}" fill="{fill}" '
        'stroke-linejoin="round" />'
    )


def svg_text(x, y, text, fill=STROKE):
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" fill="{fill}" '
        'font-family="Helvetica, Arial, sans-serif" font-size="12" '
        'text-anchor="middle">'
        f"{text}</text>"
    )


def draw_gear_svg(shapes, cx, cy, size):
    outer_r = size * 0.30
    inner_r = size * 0.14
    tooth_len = size * 0.08
    tooth_w = size * 0.10
    teeth = 8
    for i in range(teeth):
        angle = i * 2 * math.pi / teeth
        ux = math.cos(angle)
        uy = math.sin(angle)
        px = -uy
        py = ux
        tx = cx + ux * (outer_r + tooth_len / 2)
        ty = cy + uy * (outer_r + tooth_len / 2)
        half_w = tooth_w / 2
        half_l = tooth_len / 2
        points = [
            (tx + px * half_w + ux * half_l, ty + py * half_w + uy * half_l),
            (tx - px * half_w + ux * half_l, ty - py * half_w + uy * half_l),
            (tx - px * half_w - ux * half_l, ty - py * half_w - uy * half_l),
            (tx + px * half_w - ux * half_l, ty + py * half_w - uy * half_l),
        ]
        shapes.append(svg_polygon(points))
    shapes.append(svg_circle(cx, cy, outer_r))
    shapes.append(svg_circle(cx, cy, inner_r))


def draw_sliders_svg(shapes, cx, cy, size):
    length = size * 0.6
    offsets = [-size * 0.16, 0, size * 0.16]
    knob_positions = [-size * 0.12, size * 0.18, -size * 0.02]
    for offset, knob in zip(offsets, knob_positions):
        y = cy + offset
        shapes.append(
            svg_line(cx - length / 2, y, cx + length / 2, y)
        )
        knob_r = size * 0.06
        shapes.append(svg_circle(cx + knob, y, knob_r))


def draw_orbit_ring_svg(shapes, cx, cy, size):
    ring_r = size * 0.34
    node_r = size * 0.06
    shapes.append(svg_circle(cx, cy, ring_r))
    for angle in (math.pi / 2, math.pi * 1.25, math.pi * 1.75):
        nx = cx + math.cos(angle) * ring_r
        ny = cy + math.sin(angle) * ring_r
        shapes.append(svg_circle(nx, ny, node_r, fill=STROKE, width=0))


def draw_concentric_svg(shapes, cx, cy, size):
    outer_r = size * 0.34
    inner_r = size * 0.18
    dot_r = size * 0.04
    shapes.append(svg_circle(cx, cy, outer_r))
    shapes.append(svg_circle(cx, cy, inner_r))
    shapes.append(svg_circle(cx, cy, dot_r, fill=STROKE, width=0))


def draw_grid_svg(shapes, cx, cy, size):
    gap = size * 0.12
    dot = size * 0.08
    start_x = cx - gap
    start_y = cy - gap
    for row in range(3):
        for col in range(3):
            x = start_x + col * gap - dot / 2
            y = start_y + row * gap - dot / 2
            shapes.append(svg_rect(x, y, dot, dot))


def draw_compass_svg(shapes, cx, cy, size):
    outer_r = size * 0.34
    needle_len = size * 0.22
    needle_w = size * 0.08
    shapes.append(svg_circle(cx, cy, outer_r))
    points = [
        (cx, cy - needle_len),
        (cx - needle_w / 2, cy),
        (cx, cy + needle_len * 0.2),
        (cx + needle_w / 2, cy),
    ]
    shapes.append(svg_polygon(points))


def build_svg(icons, cols, cell_w, cell_h, icon_size):
    width = cols * cell_w
    rows = (len(icons) + cols - 1) // cols
    height = rows * cell_h
    shapes = [
        f'<rect width="100%" height="100%" fill="{WINDOW_BG}" />'
    ]
    svg_painters = {
        "Gear": draw_gear_svg,
        "Sliders": draw_sliders_svg,
        "Orbit ring": draw_orbit_ring_svg,
        "Concentric": draw_concentric_svg,
        "Grid": draw_grid_svg,
        "Compass": draw_compass_svg,
    }
    for idx, (label, _painter) in enumerate(icons):
        col = idx % cols
        row = idx // cols
        cx = col * cell_w + cell_w / 2
        cy = row * cell_h + cell_h / 2 - 10
        painter = svg_painters[label]
        painter(shapes, cx, cy, icon_size)
        shapes.append(svg_text(cx, cy + icon_size * 0.42, label))
    svg_body = "\n  ".join(shapes)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">\n  '
        f"{svg_body}\n</svg>\n"
    )


def main():
    icons = [
        ("Gear", draw_gear),
        ("Sliders", draw_sliders),
        ("Orbit ring", draw_orbit_ring),
        ("Concentric", draw_concentric),
        ("Grid", draw_grid),
        ("Compass", draw_compass),
    ]
    cols = 3
    cell_w = 220
    cell_h = 200
    rows = (len(icons) + cols - 1) // cols
    width = cols * cell_w
    height = rows * cell_h
    icon_size = 96

    if tk is None:
        svg_path = os.path.join(
            os.path.dirname(__file__),
            "icon_options_preview.svg",
        )
        svg_markup = build_svg(icons, cols, cell_w, cell_h, icon_size)
        with open(svg_path, "w", encoding="utf-8") as handle:
            handle.write(svg_markup)
        print("Tkinter not available. Wrote SVG preview to:")
        print(svg_path)
        return

    root = tk.Tk()
    root.title("Meta Icon Options")
    root.configure(bg=WINDOW_BG)
    canvas = tk.Canvas(root, width=width, height=height, bg=WINDOW_BG, highlightthickness=0)
    canvas.pack()
    draw_icon_grid(canvas, icons, cols, cell_w, cell_h, icon_size)
    root.mainloop()


if __name__ == "__main__":
    main()
