from pathlib import Path

import fontforge as ff

# ==== CONSTANTS ====
ANCHOR_TABLE, ANCHOR_CLASS = "mrk", "top"
DIACRITICS = [0x301, 0x302, 0x304, 0x306, 0x311]
DONT_BRING_DOWN = [
    ord(s) for s in "'\"\u00AB\u00BB"
]
BASE_ANCHOR_THRESHOLD = 0.2
BASE_ANCHOR_DISTANCE = 40

# ==== FUNCTIONS ====

def log(data):
    ff.logWarning(str(data))


def bring_glyphs_to_baseline(font: ff.font):
    for glyph in font.glyphs():
        if glyph.unicode in DONT_BRING_DOWN:
            continue
        if not glyph.isWorthOutputting():
            continue

        bbox = glyph.boundingBox()
        ymin = bbox[1]
        
        if ymin > 0:
            shift = -ymin
            glyph.transform((1, 0, 0, 1, 0, shift))


def main():
    font: ff.font = ff.activeFont()
    font.encoding = "UnicodeBMP"
    
    font.selection.all()
    font.autoWidth(100, 10, 300)
    font.selection.none()
    bring_glyphs_to_baseline(font)

    glyph: ff.glyph = font[ord("'")]
    glyph.width = 0
    glyph.left_side_bearing = 0
    glyph.right_side_bearing = 0

    glyph: ff.glyph = font[ord(" ")]
    glyph.width = 300

    # Set diacritic width to 0
    for d in DIACRITICS:
        glyph: ff.glyph = font[d]
        glyph.width = 0
    
    font.encoding = "compacted"


if __name__ == "__main__":
    main()
