# generate_fonts.py
import os
import numpy as np
from fontTools import ttLib
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._c_m_a_p import cmap_format_4, table__c_m_a_p
from fontTools.ttLib.tables._g_l_y_f import Glyph, table__g_l_y_f
from fontTools.ttLib.tables._h_m_t_x import table__h_m_t_x
from fontTools.ttLib.tables._h_e_a_d import table__h_e_a_d
from fontTools.ttLib.tables._h_h_e_a import table__h_h_e_a
from fontTools.ttLib.tables.O_S_2f_2 import table_O_S_2f_2, Panose
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from fontTools.ttLib.tables._p_o_s_t import table__p_o_s_t
from fontTools.ttLib.tables._m_a_x_p import table__m_a_x_p
from fontTools.ttLib.tables._l_o_c_a import table__l_o_c_a

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
# UNITS_PER_EM_VALUES = [1000, 2048]
UNITS_PER_EM_VALUES = [1024]
CIRCLE_RADII = [64, 128, 256, 512]  # In font units
FONT_SIZES_PT = [12, 24, 48, 72]  # For HTML report

# --- Helper Functions ---

def circle_to_glyph(cx, cy, r, glyph_set, num_segments=64):
    """Creates a hollow circle glyph (a ring) using polygonal approximation."""
    pen = TTGlyphPen(glyph_set)

    # Outer circle (clockwise)
    outer_points = arc_poly(cx, cy, r, r, 0, 2 * np.pi, num_segments=num_segments)
    pen.moveTo(outer_points[0])
    for point in outer_points[1:]:
        pen.lineTo(point)
    pen.closePath()

    # Inner circle (counter-clockwise to create a hole)
    thickness = 16  # Fixed thickness of 16 font units
    inner_r = r - thickness
    if inner_r > 0:
        # Generate points in reverse for opposite winding direction
        inner_points = arc_poly(cx, cy, inner_r, inner_r, 2 * np.pi, 0, num_segments=num_segments)
        pen.moveTo(inner_points[0])
        for point in inner_points[1:]:
            pen.lineTo(point)
        pen.closePath()

    return pen.glyph()

def polygon_to_glyph(points, glyph_set):
    """Creates a glyph from a list of polygon points."""
    pen = TTGlyphPen(glyph_set)
    if not points:
        return pen.glyph()

    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()
    return pen.glyph()

def square_to_glyph(x, y, width, height, thickness, glyph_set):
    """Creates a hollow square glyph."""
    pen = TTGlyphPen(glyph_set)

    # Outer square (clockwise)
    outer_points = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height)
    ]
    pen.moveTo(outer_points[0])
    for point in outer_points[1:]:
        pen.lineTo(point)
    pen.closePath()

    # Inner square (counter-clockwise)
    inner_x = x + thickness
    inner_y = y + thickness
    inner_width = width - 2 * thickness
    inner_height = height - 2 * thickness
    if inner_width > 0 and inner_height > 0:
        inner_points = [
            (inner_x, inner_y),
            (inner_x, inner_y + inner_height),
            (inner_x + inner_width, inner_y + inner_height),
            (inner_x + inner_width, inner_y)
        ]
        pen.moveTo(inner_points[0])
        for point in inner_points[1:]:
            pen.lineTo(point)
        pen.closePath()

    return pen.glyph()

def concentric_circles_to_glyph(cx, cy, radii, thickness, glyph_set, num_segments=64):
    """Creates a glyph with multiple concentric hollow circles."""
    pen = TTGlyphPen(glyph_set)

    for r in sorted(radii, reverse=True):
        # Outer circle (clockwise)
        outer_points = arc_poly(cx, cy, r, r, 0, 2 * np.pi, num_segments=num_segments)
        pen.moveTo(outer_points[0])
        for point in outer_points[1:]:
            pen.lineTo(point)
        pen.closePath()

        # Inner circle (counter-clockwise)
        inner_r = r - thickness
        if inner_r > 0:
            inner_points = arc_poly(cx, cy, inner_r, inner_r, 2 * np.pi, 0, num_segments=num_segments)
            pen.moveTo(inner_points[0])
            for point in inner_points[1:]:
                pen.lineTo(point)
            pen.closePath()
    return pen.glyph()

def hexagon_circles_to_glyph(cx, cy, hex_radius, circle_radius, thickness, glyph_set, num_segments=32):
    """Creates a glyph with six small circles in a hexagon layout."""
    pen = TTGlyphPen(glyph_set)

    for i in range(6):
        angle = i * np.pi / 3
        ccx = cx + hex_radius * np.cos(angle)
        ccy = cy + hex_radius * np.sin(angle)

        # Outer circle
        outer_points = arc_poly(ccx, ccy, circle_radius, circle_radius, 0, 2 * np.pi, num_segments=num_segments)
        pen.moveTo(outer_points[0])
        for point in outer_points[1:]:
            pen.lineTo(point)
        pen.closePath()

        # Inner circle
        inner_r = circle_radius - thickness
        if inner_r > 0:
            inner_points = arc_poly(ccx, ccy, inner_r, inner_r, 2 * np.pi, 0, num_segments=num_segments)
            pen.moveTo(inner_points[0])
            for point in inner_points[1:]:
                pen.lineTo(point)
            pen.closePath()
    return pen.glyph()

def square_and_hexagon_circles_to_glyph(
    cx, cy, square_width, square_height, thickness,
    hex_radius, circle_radius, glyph_set, num_segments_hex_circles=32
):
    """Creates a composite glyph of a square and a hexagon of circles."""
    pen = TTGlyphPen(glyph_set)

    # --- Draw Square ---
    x = cx - square_width / 2
    y = cy - square_height / 2
    outer_points = [(x, y), (x + square_width, y), (x + square_width, y + square_height), (x, y + square_height)]
    pen.moveTo(outer_points[0])
    for point in outer_points[1:]: pen.lineTo(point)
    pen.closePath()
    inner_x, inner_y = x + thickness, y + thickness
    inner_width, inner_height = square_width - 2 * thickness, square_height - 2 * thickness
    if inner_width > 0 and inner_height > 0:
        inner_points = [(inner_x, inner_y), (inner_x, inner_y + inner_height), (inner_x + inner_width, inner_y + inner_height), (inner_x + inner_width, inner_y)]
        pen.moveTo(inner_points[0])
        for point in inner_points[1:]: pen.lineTo(point)
        pen.closePath()

    # --- Draw Hexagon of Circles ---
    for i in range(6):
        angle = i * np.pi / 3
        ccx, ccy = cx + hex_radius * np.cos(angle), cy + hex_radius * np.sin(angle)
        outer_points = arc_poly(ccx, ccy, circle_radius, circle_radius, 0, 2 * np.pi, num_segments=num_segments_hex_circles)
        pen.moveTo(outer_points[0])
        for point in outer_points[1:]: pen.lineTo(point)
        pen.closePath()
        inner_r = circle_radius - thickness
        if inner_r > 0:
            inner_points = arc_poly(ccx, ccy, inner_r, inner_r, 2 * np.pi, 0, num_segments=num_segments_hex_circles)
            pen.moveTo(inner_points[0])
            for point in inner_points[1:]: pen.lineTo(point)
            pen.closePath()

    return pen.glyph()

def concentric_and_hexagon_circles_to_glyph(
    cx, cy, radii, thickness, hex_radius, circle_radius, glyph_set,
    num_segments_concentric=64, num_segments_hex_circles=32
):
    """Creates a composite glyph of concentric circles and a hexagon of circles."""
    pen = TTGlyphPen(glyph_set)

    # --- Draw Concentric Circles ---
    for r in sorted(radii, reverse=True):
        outer_points = arc_poly(cx, cy, r, r, 0, 2 * np.pi, num_segments=num_segments_concentric)
        pen.moveTo(outer_points[0])
        for point in outer_points[1:]: pen.lineTo(point)
        pen.closePath()
        inner_r = r - thickness
        if inner_r > 0:
            inner_points = arc_poly(cx, cy, inner_r, inner_r, 2 * np.pi, 0, num_segments=num_segments_concentric)
            pen.moveTo(inner_points[0])
            for point in inner_points[1:]: pen.lineTo(point)
            pen.closePath()

    # --- Draw Hexagon of Circles ---
    for i in range(6):
        angle = i * np.pi / 3
        ccx, ccy = cx + hex_radius * np.cos(angle), cy + hex_radius * np.sin(angle)
        outer_points = arc_poly(ccx, ccy, circle_radius, circle_radius, 0, 2 * np.pi, num_segments=num_segments_hex_circles)
        pen.moveTo(outer_points[0])
        for point in outer_points[1:]: pen.lineTo(point)
        pen.closePath()
        inner_r = circle_radius - thickness
        if inner_r > 0:
            inner_points = arc_poly(ccx, ccy, inner_r, inner_r, 2 * np.pi, 0, num_segments=num_segments_hex_circles)
            pen.moveTo(inner_points[0])
            for point in inner_points[1:]: pen.lineTo(point)
            pen.closePath()

    return pen.glyph()

def arc_poly(cx, cy, rx, ry, start_angle, end_angle, num_segments=16):
    """Generates points for a polygonal approximation of an elliptical arc."""
    theta = np.linspace(start_angle, end_angle, num_segments + 1)
    points = [(cx + rx * np.cos(angle), cy + ry * np.sin(angle)) for angle in theta]
    return points

def shift_points(points, y_shift):
    """Shifts the y-coordinate of all points in a list."""
    return [(x, y + y_shift) for x, y in points]

# --- Core Font Generation ---

def create_font(font_name, units_per_em, glyphs_data, output_path):
    """Creates and saves a TTF font file from provided glyph data."""
    font = TTFont()
    glyph_order = ['.notdef'] + sorted(glyphs_data.keys())
    font.setGlyphOrder(glyph_order)

    # --- Glyf and Hmtx Tables ---
    font['glyf'] = glyf_table = table__g_l_y_f()
    glyf_table.glyphs = {}
    font['hmtx'] = hmtx_table = table__h_m_t_x()
    hmtx_table.metrics = {}

    glyf_table.glyphs['.notdef'] = Glyph()
    hmtx_table.metrics['.notdef'] = (int(units_per_em / 2), 0)

    for char, data in glyphs_data.items():
        if data.get('type') == 'circle':
            glyph = circle_to_glyph(data['cx'], data['cy'], data['radius'], glyf_table.glyphs)
        elif data.get('type') == 'polygon':
            glyph = polygon_to_glyph(data['points'], glyf_table.glyphs)
        elif data.get('type') == 'square':
            glyph = square_to_glyph(data['x'], data['y'], data['square_width'], data['square_height'], data['thickness'], glyf_table.glyphs)
        elif data.get('type') == 'concentric_circles':
            glyph = concentric_circles_to_glyph(data['cx'], data['cy'], data['radii'], data['thickness'], glyf_table.glyphs)
        elif data.get('type') == 'hexagon_circles':
            glyph = hexagon_circles_to_glyph(data['cx'], data['cy'], data['hex_radius'], data['circle_radius'], data['thickness'], glyf_table.glyphs)
        elif data.get('type') == 'square_and_hexagon_circles':
            glyph = square_and_hexagon_circles_to_glyph(
                data['cx'], data['cy'], data['square_width'], data['square_height'], data['thickness'],
                data['hex_radius'], data['circle_radius'], glyf_table.glyphs
            )
        elif data.get('type') == 'concentric_and_hexagon_circles':
            glyph = concentric_and_hexagon_circles_to_glyph(
                data['cx'], data['cy'], data['radii'], data['thickness'],
                data['hex_radius'], data['circle_radius'], glyf_table.glyphs
            )
        else:
            continue  # Skip unknown glyph types

        glyph.recalcBounds(glyf_table)

        glyf_table.glyphs[char] = glyph
        lsb = glyph.xMin if hasattr(glyph, 'xMin') else 0
        hmtx_table.metrics[char] = (data['width'], lsb)

    # --- Cmap Table ---
    cmap = cmap_format_4(4)
    cmap.platformID = 3
    cmap.platEncID = 1
    cmap.language = 0
    cmap.cmap = {ord(c): c for c in glyphs_data.keys()}
    cmap_table = table__c_m_a_p()
    cmap_table.tableVersion = 0
    cmap_table.tables = [cmap]
    font['cmap'] = cmap_table

    # --- Font Header Tables ---
    font['head'] = head = table__h_e_a_d()
    head.tableVersion = 1.0
    head.fontRevision = 1.0
    head.checkSumAdjustment = 0
    head.magicNumber = 0x5F0F3CF5
    head.flags = 3  # Set default flags
    head.unitsPerEm = units_per_em
    head.created = 0
    head.modified = 0

    # Calculate font bounding box from all glyphs
    all_glyphs = [glyf_table.glyphs[name] for name in glyphs_data.keys()]

    xMins = [g.xMin for g in all_glyphs if hasattr(g, 'xMin')]
    yMins = [g.yMin for g in all_glyphs if hasattr(g, 'yMin')]
    xMaxs = [g.xMax for g in all_glyphs if hasattr(g, 'xMax')]
    yMaxs = [g.yMax for g in all_glyphs if hasattr(g, 'yMax')]

    if xMins:
        head.xMin = min(xMins)
        head.yMin = min(yMins)
        head.xMax = max(xMaxs)
        head.yMax = max(yMaxs)
    else:
        head.xMin, head.yMin, head.xMax, head.yMax = (0, 0, 0, 0)

    head.macStyle = 0
    head.lowestRecPPEM = 0
    head.fontDirectionHint = 2
    head.indexToLocFormat = 0
    head.glyphDataFormat = 0

    font['hhea'] = hhea = table__h_h_e_a()
    hhea.tableVersion = 0x00010000
    # Use an 80/20 split for ascent/descent for better vertical alignment
    hhea.ascent = int(units_per_em * 0.8)
    hhea.descent = -(units_per_em - hhea.ascent)
    hhea.lineGap = 0
    hhea.advanceWidthMax = 0  # Will be recalculated
    hhea.minLeftSideBearing = 0  # Will be recalculated
    hhea.minRightSideBearing = 0  # Will be recalculated
    hhea.xMaxExtent = 0  # Will be recalculated
    hhea.caretSlopeRise = 1
    hhea.caretSlopeRun = 0
    hhea.caretOffset = 0
    hhea.reserved0 = 0
    hhea.reserved1 = 0
    hhea.reserved2 = 0
    hhea.reserved3 = 0
    hhea.metricDataFormat = 0
    hhea.numberOfHMetrics = len(hmtx_table.metrics)

    font['OS/2'] = os2 = table_O_S_2f_2()
    os2.version = 4
    os2.xAvgCharWidth = units_per_em
    os2.usWeightClass = 400
    os2.usWidthClass = 5
    os2.fsType = 0
    os2.ySubscriptXSize, os2.ySubscriptYSize, os2.ySubscriptXOffset, os2.ySubscriptYOffset = (650, 700, 0, 140)
    os2.ySuperscriptXSize, os2.ySuperscriptYSize, os2.ySuperscriptXOffset, os2.ySuperscriptYOffset = (650, 700, 0, 480)
    os2.yStrikeoutSize, os2.yStrikeoutPosition = (50, 258)
    os2.sFamilyClass = 0
    os2.panose = Panose()
    os2.ulUnicodeRange1, os2.ulCodePageRange1 = (1, 1)
    os2.ulUnicodeRange2 = 0
    os2.ulUnicodeRange3 = 0
    os2.ulUnicodeRange4 = 0
    os2.ulCodePageRange2 = 0
    os2.achVendID = 'TEST'
    os2.fsSelection = 1 << 6
    os2.usFirstCharIndex = min(ord(c) for c in glyphs_data.keys())
    os2.usLastCharIndex = max(ord(c) for c in glyphs_data.keys())
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = (hhea.ascent, hhea.descent, 0)
    os2.usWinAscent, os2.usWinDescent = (hhea.ascent, abs(hhea.descent))
    os2.sxHeight = int(units_per_em * 0.7)
    os2.sCapHeight = int(units_per_em * 0.7)
    os2.usDefaultChar = 0
    os2.usBreakChar = 0
    os2.usMaxContext = 0

    font['name'] = name = table__n_a_m_e()
    name.setName(font_name, 1, 3, 1, 0x409)
    name.setName("Regular", 2, 3, 1, 0x409)
    name.setName(font_name, 4, 3, 1, 0x409)
    name.setName(font_name.replace(" ", ""), 6, 3, 1, 0x409)

    font['post'] = post = table__p_o_s_t()
    post.formatType = 2.0
    post.italicAngle = 0.0
    post.underlinePosition = -100
    post.underlineThickness = 50
    post.isFixedPitch = 0
    post.minMemType42 = 0
    post.maxMemType42 = 0
    post.minMemType1 = 0
    post.maxMemType1 = 0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order

    # fontTools will compute maxp and loca tables on save
    font['maxp'] = maxp = table__m_a_x_p()
    maxp.tableVersion = 0x00010000
    maxp.numGlyphs = 0  # Will be recalculated
    maxp.maxPoints = 0  # Will be recalculated
    maxp.maxContours = 0  # Will be recalculated
    maxp.maxCompositePoints = 0  # Will be recalculated
    maxp.maxCompositeContours = 0  # Will be recalculated
    maxp.maxZones = 1  # Default for non-hinted fonts
    maxp.maxTwilightPoints = 0  # Default
    maxp.maxStorage = 0  # Default
    maxp.maxFunctionDefs = 0  # Default
    maxp.maxInstructionDefs = 0  # Default
    maxp.maxStackElements = 0  # Default
    maxp.maxSizeOfInstructions = 0  # Default
    maxp.maxComponentElements = 0  # Will be recalculated
    maxp.maxComponentDepth = 0  # Will be recalculated
    font['loca'] = table__l_o_c_a()

    font.save(output_path)
    print(f"Successfully created {output_path}")

# --- Visual Report Generation ---
def generate_html_report(font_files, output_dir):
    """Generates an HTML file to display the fonts."""
    sample_text = "ABCDEF|<>()"

    style_rules = ""
    for font_file in font_files:
        font_name = os.path.splitext(font_file)[0]
        style_rules += f"""
        @font-face {{
            font-family: '{font_name}';
            src: url('{font_file}') format('truetype');
        }}"""

    body_content = ""
    for font_file in font_files:
        font_name = os.path.splitext(font_file)[0]
        body_content += f"""
    <div class="font-showcase">
        <h2>Font: <span class="font-spec">{font_name}</span></h2>"""
        for size in FONT_SIZES_PT:
            body_content += f"""
        <p style="font-family: '{font_name}'; font-size: {size}pt;">{size}pt: {sample_text}</p>"""
        body_content += "</div>"

    html_content = f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Font Test Report</title>
<style>
    body {{ font-family: sans-serif; padding: 2em; color: #333; background-color: #fdfdfd; }}
    .font-showcase {{ border: 1px solid #ddd; padding: 1.5em; margin-bottom: 2em; border-radius: 8px; background-color: #fff; }}
    h1 {{ text-align: center; }} h2 {{ border-bottom: 2px solid #eee; padding-bottom: 0.5em; margin-top: 0; }}
    .font-spec {{ font-family: monospace; background-color: #f0f0f0; padding: 2px 6px; border-radius: 4px; }}
    {style_rules}
</style></head><body><h1>Font Generation Test Report</h1>{body_content}</body></html>"""

    report_path = os.path.join(output_dir, "index.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully created HTML report at {report_path}")

# --- Main Execution ---
def main():
    """Main script to generate fonts and the report."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    generated_fonts = []
    for em_size in UNITS_PER_EM_VALUES:
        font_name = f"CircleTest-EM{em_size}"
        glyphs = {}

        # Adjust vertical alignment by setting a baseline and shifting glyphs
        ascent = int(em_size * 0.8)
        descent = -(em_size - ascent)
        center_y = (ascent + descent) / 2.0
        y_shift = center_y - (em_size / 2.0)


        # --- Define glyphs ---
        square_margin = 50
        square_thickness = 16
        square_dim = em_size - 2 * square_margin

        # Glyph 'A': Square overlapped with small circle hexagon
        glyphs['A'] = {
            'type': 'square_and_hexagon_circles',
            'cx': em_size / 2,
            'cy': center_y,
            'square_width': square_dim,
            'square_height': square_dim,
            'hex_radius': 300,
            'circle_radius': 80,
            'thickness': 16,
            'width': em_size
        }

        # Glyph 'B': Hexagon with three concentric circles
        glyphs['B'] = {
            'type': 'concentric_and_hexagon_circles',
            'cx': em_size / 2,
            'cy': center_y,
            'radii': [64, 128, 256],
            'hex_radius': 300,
            'circle_radius': 80,
            'thickness': 16,
            'width': em_size
        }

        # Glyph 'C' (Concentric circles, formerly 'F')
        glyphs['C'] = {
            'type': 'concentric_circles',
            'cx': em_size / 2,
            'cy': center_y,
            'radii': CIRCLE_RADII,
            'thickness': 16,
            'width': em_size
        }

        # Glyph 'D' (Hexagon of circles, formerly 'G')
        glyphs['D'] = {
            'type': 'hexagon_circles',
            'cx': em_size / 2,
            'cy': center_y,
            'hex_radius': 300,
            'circle_radius': 80,
            'thickness': 16,
            'width': em_size
        }

        # Glyph 'E' (Hollow Square, formerly 'H')
        glyphs['E'] = {
            'type': 'square',
            'x': square_margin,
            'y': square_margin + y_shift,
            'square_width': square_dim,
            'square_height': square_dim,
            'thickness': square_thickness,
            'width': em_size
        }

        # Glyph 'F' (Hexagon of smaller circles near edge, formerly 'I')
        glyphs['F'] = {
            'type': 'hexagon_circles',
            'cx': em_size / 2,
            'cy': center_y,
            'hex_radius': 450,
            'circle_radius': 50,
            'thickness': 16,
            'width': em_size
        }

        # Glyph '|' (vertical bar)
        thickness = em_size * 0.1
        bar_width = thickness
        bar_height = em_size * 0.7
        x_center = em_size / 2
        y_bottom = (em_size - bar_height) / 2
        points_bar = [
            (x_center - bar_width / 2, y_bottom),
            (x_center + bar_width / 2, y_bottom),
            (x_center + bar_width / 2, y_bottom + bar_height),
            (x_center - bar_width / 2, y_bottom + bar_height),
        ]
        glyphs['|'] = {'type': 'polygon', 'points': shift_points(points_bar, y_shift), 'width': em_size}

        # Glyph '<'
        x1, y1 = em_size * 0.7, em_size * 0.9
        x2, y2 = em_size * 0.7, em_size * 0.8
        x3, y3 = em_size * 0.4, em_size * 0.5
        x4, y4 = em_size * 0.7, em_size * 0.2
        x5, y5 = em_size * 0.7, em_size * 0.1
        x6, y6 = em_size * 0.3, em_size * 0.5
        points_lt = [(x1,y1), (x2,y2), (x3,y3), (x4,y4), (x5,y5), (x6,y6)]
        glyphs['<'] = {'type': 'polygon', 'points': shift_points(points_lt, y_shift), 'width': em_size}

        # Glyph '>'
        points_gt = [(em_size - x, y) for x, y in points_lt]
        glyphs['>'] = {'type': 'polygon', 'points': shift_points(points_gt, y_shift), 'width': em_size}

        # Glyphs for '(' and ')'
        paren_thickness = em_size * 0.08
        paren_ry = em_size * 0.4
        paren_rx = em_size * 0.1
        paren_cy = center_y

        # Glyph ')'
        paren_r_cx = em_size * 0.4
        outer_arc_r = arc_poly(paren_r_cx, paren_cy, paren_rx, paren_ry, -np.pi / 2, np.pi / 2)
        inner_arc_r = arc_poly(paren_r_cx, paren_cy, paren_rx - paren_thickness, paren_ry, np.pi / 2, -np.pi / 2)
        points_r_paren = outer_arc_r + inner_arc_r
        glyphs[')'] = {'type': 'polygon', 'points': points_r_paren, 'width': em_size}

        # Glyph '('
        paren_l_cx = em_size * 0.6
        outer_arc_l = arc_poly(paren_l_cx, paren_cy, paren_rx, paren_ry, np.pi / 2, 3 * np.pi / 2)
        inner_arc_l = arc_poly(paren_l_cx, paren_cy, paren_rx - paren_thickness, paren_ry, 3 * np.pi / 2, np.pi / 2)
        points_l_paren = outer_arc_l + inner_arc_l
        glyphs['('] = {'type': 'polygon', 'points': points_l_paren, 'width': em_size}

        output_file = os.path.join(OUTPUT_DIR, f"{font_name}.ttf")
        create_font(font_name, em_size, glyphs, output_file)
        generated_fonts.append(os.path.basename(output_file))

    generate_html_report(generated_fonts, OUTPUT_DIR)

if __name__ == "__main__":
    main()
