from pathlib import Path

import fontforge as ff


def log(data):
    ff.logWarning(str(data))


specials = 'ыьэюяёj'
small = [ord(s) for s in specials.lower()]
big   = [ord(s) for s in specials.upper()]


def remove_copies(f: ff.font):
    original_encoding = f.encoding

    for glyph in f.glyphs():
        glyph: ff.glyph = glyph

        if (altuni := glyph.altuni) is not None:
            for alternate_data in altuni:
                unicode_value = alternate_data[0]
                alternate_glyph: ff.glyph = f[unicode_value]
                alternate_glyph.unlinkRef()
            
            glyph.altuni = None

    # Restore encoding
    f.encoding = original_encoding


def create_base(base: ff.font):
    base.encoding = "UnicodeBMP"
    base.selection.all()
    base.clear()

    current_dir = Path(base.path).parent
    letters_dir = current_dir / "letters.sfd"
    symbols_dir = current_dir / "symbols.sfd"
    log(symbols_dir)
    log(letters_dir)

    letters = ff.open(
        ff.openFilename("Select letters fontfile")
    )
    remove_copies(letters)
    letters.save(str(letters_dir))
    letters.close()

    symbols = ff.open(
        ff.openFilename("Select symbols fontfile")
    )
    remove_copies(symbols)

    # Symbols contain capital letters for some reason so we just... copy them!
    for b, s in zip(big, small): # bs indeed
        symbols.selection.select(b)
        symbols.copy()
        symbols.selection.select(s)
        symbols.paste()
    symbols.selection.none()
    symbols.save(str(symbols_dir))
    symbols.close()

    base.mergeFonts(str(letters_dir))
    base.mergeFonts(str(symbols_dir))

    letters_dir.unlink()
    symbols_dir.unlink()


if __name__ == "__main__":
    create_base(ff.activeFont())
