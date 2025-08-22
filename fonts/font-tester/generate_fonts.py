# generate_fonts.py
import os
from fontTools import ttLib
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._c_m_a_p import cmap_format_4, table__c_m_a_p
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables._h_e_a_d import table__h_e_a_d
from fontTools.ttLib.tables._h_h_e_a import table__h_h_e_a
from fontTools.ttLib.tables.O_S_2f_2 import table_O_S_2f_2
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from fontTools.ttLib.tables._p_o_s_t import table__p_o_s_t
from fontTools.ttLib.tables._m_a_x_p import table__m_a_x_p
from fontTools.ttLib.tables._l_o_c_a import table__l_o_c_a
from svg.path import parse_path, Move, Line, Arc, CubicBezier, QuadraticBezier, Close

# --- Configuration ---
OUTPUT_DIR = "output"
UNITS_PER_EM_VALUES = [1000, 2048]
CIRCLE_RADII = [100, 250, 400]  # In font units
FONT_SIZES_PT = [12, 24, 48, 72]  # For HTML report

# --- Helper Functions ---

def circle_to_svg_path(cx, cy, r):
    """Converts circle parameters to an SVG path string using cubic Beziers."""
    kappa = 0.552284749831
    kr = r * kappa
    return (
        f"M {cx},{cy+r} "
        f"C {cx+kr},{cy+r} {cx+r},{cy+kr} {cx+r},{cy} "
        f"C {cx+r},{cy-kr} {cx+kr},{cy-r} {cx},{cy-r} "
        f"C {cx-kr},{cy-r} {cx-r},{cy-kr} {cx-r},{cy} "
        f"C {cx-r},{cy+kr} {cx-kr},{cy+r} {cx},{cy+r} Z"
    )

def svg_path_to_glyph(svg_path, glyf_table):
    """Converts an SVG path string to a fontTools TTGlyph object."""
    pen = TTGlyphPen(glyf_table)
    path = parse_path(svg_path)

    current_pos = 0j
    for seg in path:
        if isinstance(seg, Move):
            pen.moveTo((seg.end.real, seg.end.imag))
            current_pos = seg.end
        elif isinstance(seg, Line):
            pen.lineTo((seg.end.real, seg.end.imag))
            current_pos = seg.end
        elif isinstance(seg, Arc):
            raise NotImplementedError("Arc segments are not supported.")
        elif isinstance(seg, CubicBezier):
            pen.curveTo(
                (seg.control1.real, seg.control1.imag),
                (seg.control2.real, seg.control2.imag),
                (seg.end.real, seg.end.imag)
            )
            current_pos = seg.end
        elif isinstance(seg, QuadraticBezier):
            pen.qCurveTo(
                (seg.control.real, seg.control.imag),
                (seg.end.real, seg.end.imag)
            )
            current_pos = seg.end
        elif isinstance(seg, Close):
            pen.closePath()
            if hasattr(path, 'start') and path.start:
                current_pos = path.start

    return pen.glyph()

# --- Core Font Generation ---

def create_font(font_name, units_per_em, glyphs_data, output_path):
    """Creates and saves a TTF font file from provided glyph data."""
    font = TTFont()
    glyph_order = ['.notdef'] + sorted(glyphs_data.keys())
    font.setGlyphOrder(glyph_order)

    # --- Glyf and Hmtx Tables ---
    glyf_table = font['glyf'] = {}
    hmtx_table = font['hmtx'] = {}

    glyf_table['.notdef'] = Glyph()
    hmtx_table['.notdef'] = (units_per_em, 0)

    for char, data in glyphs_data.items():
        glyph = svg_path_to_glyph(data['path'], glyf_table)
        glyf_table[char] = glyph
        lsb = int((data['width'] / 2) - data['radius'])
        hmtx_table[char] = (data['width'], lsb)

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
    head.unitsPerEm = units_per_em
    head.fontRevision = 1.0

    font['hhea'] = hhea = table__h_h_e_a()
    hhea.ascent = int(units_per_em * 0.85)
    hhea.descent = -int(units_per_em * 0.15)
    hhea.lineGap = 0

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
    os2.panose = b'\x00' * 10
    os2.ulUnicodeRange1, os2.ulCodePageRange1 = (1, 1)
    os2.achVendID = 'TEST'
    os2.fsSelection = 1 << 6
    os2.usFirstCharIndex = min(ord(c) for c in glyphs_data.keys())
    os2.usLastCharIndex = max(ord(c) for c in glyphs_data.keys())
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = (hhea.ascent, hhea.descent, 0)
    os2.usWinAscent, os2.usWinDescent = (hhea.ascent, abs(hhea.descent))

    font['name'] = name = table__n_a_m_e()
    name.setName(font_name, 1, 3, 1, 0x409)
    name.setName("Regular", 2, 3, 1, 0x409)
    name.setName(font_name, 4, 3, 1, 0x409)
    name.setName(font_name.replace(" ", ""), 6, 3, 1, 0x409)

    font['post'] = post = table__p_o_s_t()
    post.formatType = 2.0
    post.underlinePosition = -100
    post.underlineThickness = 50
    post.isFixedPitch = 0
    post.glyphOrder = glyph_order

    # fontTools will compute maxp and loca tables on save
    font['maxp'] = table__m_a_x_p()
    font['loca'] = table__l_o_c_a()

    font.save(output_path)
    print(f"Successfully created {output_path}")

# --- Visual Report Generation ---
def generate_html_report(font_files, output_dir):
    """Generates an HTML file to display the fonts."""
    sample_text = "".join([chr(ord('A') + i) for i in range(len(CIRCLE_RADII))])

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
        for i, radius in enumerate(CIRCLE_RADII):
            char = chr(ord('A') + i)
            center_x = em_size / 2
            center_y = em_size / 2
            glyphs[char] = {
                'radius': radius,
                'path': circle_to_svg_path(center_x, center_y, radius),
                'width': em_size
            }

        output_file = os.path.join(OUTPUT_DIR, f"{font_name}.ttf")
        create_font(font_name, em_size, glyphs, output_file)
        generated_fonts.append(os.path.basename(output_file))

    generate_html_report(generated_fonts, OUTPUT_DIR)

if __name__ == "__main__":
    main()
