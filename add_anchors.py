from pathlib import Path

import fontforge as ff

# ==== CONSTANTS ====
ANCHOR_TABLE, ANCHOR_CLASS = "mrk", "top"
DIACRITICS = [0x301, 0x302, 0x304, 0x306, 0x311]
BASE_ANCHOR_THRESHOLD = 0.3
BASE_ANCHOR_DISTANCE = 60

# ==== FUNCTIONS ====

def log(data):
    ff.logWarning(str(data))


def add_anchor_class(font: ff.font):
    if ANCHOR_TABLE not in font.gpos_lookups:
        font.addLookup(ANCHOR_TABLE, "gpos_mark2base", (), (
            ("mark", (
                ("latn", ("dflt",)),
                ("DFLT", ("dflt",)), 
                ("cyrl", ("dflt",))
            )),
        ))
    else:
        ff.logWarning(f"Table {ANCHOR_TABLE} already exists!")
    
    if (subtable := ANCHOR_TABLE + "_sub") not in font.getLookupSubtables(ANCHOR_TABLE):
        font.addLookupSubtable(ANCHOR_TABLE, subtable)
    else:
        ff.logWarning(f"Subtable {subtable} already exists!") 

    if ANCHOR_CLASS in font.getLookupSubtableAnchorClasses(subtable):
        ff.logWarning(f"Anchor class {ANCHOR_CLASS} already exists!")
        return
    font.addAnchorClass(subtable, ANCHOR_CLASS)


def get_all_glyph_points(glyph: ff.glyph) -> list[ff.point]:
    points = []
    for contour in glyph.foreground:
        for point in contour:
            points.append(point)
    return points


def add_mark_anchors(font: ff.font):
    acute: ff.glyph = font[DIACRITICS[0]]
    points = list(filter(lambda p: p.on_curve, get_all_glyph_points(acute)))
    lowest_point = min(points, key=lambda p: p.y)
    acute.addAnchorPoint(ANCHOR_CLASS, "mark", lowest_point.x, lowest_point.y)

    for d in DIACRITICS[1:]:
        glyph: ff.glyph = font[d]
        xmin, ymin, xmax, _ = glyph.boundingBox()
        glyph.addAnchorPoint(ANCHOR_CLASS, "mark", (xmax+xmin)/2, ymin)


def add_base_anchors(font: ff.font):
    for glyph in font.glyphs():
        glyph: ff.glyph = glyph
        if not (0x401 <= glyph.unicode <= 0x451):
            continue

        _, ymin, _, ymax = glyph.boundingBox()
        height = ymax-ymin
        threshold = ymax - height * BASE_ANCHOR_THRESHOLD
        points = list(filter(lambda p: p.on_curve and p.y >= threshold, get_all_glyph_points(glyph)))

        min_x, max_x = min(points, key=lambda p: p.x).x, max(points, key=lambda p: p.x).x
        glyph.addAnchorPoint(ANCHOR_CLASS, "base", (min_x + max_x)/2, ymax + BASE_ANCHOR_DISTANCE)


def main():
    font: ff.font = ff.activeFont()
    font.encoding = "UnicodeBMP"

    add_anchor_class(font)
    add_mark_anchors(font)
    add_base_anchors(font)

    font.encoding = "compacted"


if __name__ == "__main__":
    main()
