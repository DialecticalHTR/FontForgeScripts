import fontforge as ff


TO_REMOVE = [
    0x301, 0x302, 0x304, 0x306, 0x311,
    ord("'")
]
KERN_TABLE = "krn"


def add_kern_table(font: ff.font):
    if KERN_TABLE not in font.gpos_lookups:
        font.addLookup(KERN_TABLE, "gpos_pair", (), (
            ("kern", (
                ("latn", ("dflt",)),
                ("DFLT", ("dflt",)), 
                ("cyrl", ("dflt",))
            )),
        ))
    else:
        ff.logWarning(f"Table {KERN_TABLE} already exists!")

    if (subtable := KERN_TABLE + "_sub") not in font.getLookupSubtables(KERN_TABLE):
        font.addLookupSubtable(KERN_TABLE, subtable)
    else:
        ff.logWarning(f"Subtable {subtable} already exists!") 


def main():
    font: ff.font = ff.activeFont()
    font.encoding = "UnicodeBMP"

    if KERN_TABLE in font.gpos_lookups:
        font.removeLookup(KERN_TABLE)
    add_kern_table(font)

    big = [
        glyph
        for glyph in font.glyphs()
        if glyph.unicode != -1 and chr(glyph.unicode) in "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁJ"
    ]
    small = [
        glyph
        for glyph in font.glyphs()
        if glyph.unicode != -1 and chr(glyph.unicode) in "йцукенгшщзхъфывапролджэячсмитьбюёj"
    ] 

    font.autoKern(
        f"{KERN_TABLE}_sub", 150,
        big, big,
        minKern=20, onlyCloser=False, touch=True
    )
    font.autoKern(
        f"{KERN_TABLE}_sub", 130,
        big, small,
        minKern=15, onlyCloser=False, touch=True
    )
    font.autoKern(
        f"{KERN_TABLE}_sub", 130,
        small, big,
        minKern=15, onlyCloser=False, touch=True
    )
    font.autoKern(
        f"{KERN_TABLE}_sub", 120,
        small, small,
        minKern=15, onlyCloser=True, touch=True
    )

    # font.selection.select(*TO_REMOVE)
    # font.selection.invert()
    # font.selection.select(*[
    #     glyphcode
    #     for glyph in font.glyphs()
    #     if 0x401 <= (glyphcode := glyph.unicode) <= 0x451
    # ])
    # font.autoKern(
    #     f"{KERN_TABLE}_sub",
    #     150, minKern=15, onlyCloser=True
    # )
    # font.selection.none()


    font.encoding = "compacted"


if __name__ == "__main__":
    main()
