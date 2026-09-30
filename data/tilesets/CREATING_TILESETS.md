# Creating a New Tileset with Porytiles V2

This documents the full workflow for adding a new primary or secondary tileset to this project using **porytiles 2.x** (`/usr/local/bin/porytiles`). All commands are run from the **repository root**.

> **Legacy tool:** `/usr/local/bin/porytiles-legacy` is V1 — do not use it for new tilesets.

---

## 1. Create the tileset in Porymap

Use Porymap to create the tileset. This generates:
- `data/tilesets/<primary|secondary>/<name>/` — binary assets (`metatiles.bin`, `metatile_attributes.bin`, `tiles.png`, `palettes/`)
- An entry in `src/data/tilesets/headers.h`
- INCBIN entries in `src/data/tilesets/graphics.h` and `src/data/tilesets/metatiles.h`

---

## 2. Create the porytiles source directory

V2 reads source PNGs from `porytiles_src/` (not `porytiles/`). Create it and add your layer files:

```
data/tilesets/<primary|secondary>/<name>/porytiles_src/
    bottom.png
    middle.png
    top.png
    attributes.csv
```

You can start with blank PNGs or copy from an existing tileset and edit in Aseprite/Porymap.

---

## 3. Bootstrap the porytiles_bin directory

V2 requires a `porytiles_bin/` directory with existing artifacts before the first compile. Copy the Porymap-generated binaries there:

```bash
mkdir -p data/tilesets/<primary|secondary>/<name>/porytiles_bin/palettes

# Copy binaries
cp data/tilesets/<primary|secondary>/<name>/metatiles.bin          data/tilesets/<primary|secondary>/<name>/porytiles_bin/
cp data/tilesets/<primary|secondary>/<name>/metatile_attributes.bin data/tilesets/<primary|secondary>/<name>/porytiles_bin/
cp data/tilesets/<primary|secondary>/<name>/tiles.png              data/tilesets/<primary|secondary>/<name>/porytiles_bin/
cp data/tilesets/<primary|secondary>/<name>/palettes/*.pal         data/tilesets/<primary|secondary>/<name>/porytiles_bin/palettes/
```

V2 expects exactly **16 palette slots** (00.pal–15.pal). Fill missing ones with blank palettes:

```bash
for i in $(seq -w 0 15); do
  f="data/tilesets/<primary|secondary>/<name>/porytiles_bin/palettes/${i}.pal"
  [ -f "$f" ] || printf 'JASC-PAL\n0100\n16\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n' > "$f"
done
```

---

## 4. Register the tileset as managed

V2 requires a manifest in `porytiles/tilesets/<gTileset_Name>/`. Create the directory and manifest (fields come from the struct in `src/data/tilesets/headers.h`):

```bash
mkdir -p porytiles/tilesets/gTileset_<Name>
```

Create `porytiles/tilesets/gTileset_<Name>/tileset-manifest.json`:

```json
{
  ".callback": "NULL",
  ".metatileAttributes": "gMetatileAttributes_<Name>",
  ".metatiles": "gMetatiles_<Name>",
  ".palettes": "gTilesetPalettes_<Name>",
  ".tiles": "gTilesetTiles_<Name>",
  "imported": true,
  "version": 1
}
```

If the tileset has an animation callback, set `".callback"` to it (e.g. `"InitTilesetAnim_<Name>"`).

---

## 5. Compile

Run from the repository root:

```bash
# Primary tileset
porytiles compile-tileset --metatile-attribute-size 2 gTileset_<Name>

# Secondary tileset paired with gTileset_General (automatic detection)
porytiles compile-tileset --metatile-attribute-size 2 gTileset_<Name>

# Secondary tileset paired with gTileset_Snow (must be explicit — auto picks wrong primary)
porytiles compile-tileset --metatile-attribute-size 2 \
  --primary-pairing-mode manual --primary-pairing-partners gTileset_Snow \
  -- gTileset_<Name>
```

> **`--metatile-attribute-size 2` is always required** for this project. pokeemerald-expansion declares multiple attribute mask layouts; V2 cannot auto-detect which to use.

On first run, V2 will:
- Update `src/data/tilesets/headers.h` to use `gTilesetXxx_PorytilesManaged_<Name>` symbols
- Add `PorytilesManaged_<Name>` INCBIN declarations to `graphics.h` and `metatiles.h`
- Write compiled output to `porytiles_bin/`
- Create `porytiles/tilesets/gTileset_<Name>/tileset.cache.json`

---

## 6. Add the compile/decompile scripts

Create `data/tilesets/<primary|secondary>/<name>/porytiles/compile.sh`:

```bash
#!/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/<primary|secondary>/<name>/porytiles/compile.sh"
    exit 1
fi

porytiles compile-tileset --metatile-attribute-size 2 gTileset_<Name>
# Add --primary-pairing-mode manual --primary-pairing-partners gTileset_Snow -- gTileset_<Name>
# if the partner primary is Snow (not auto-detected correctly).
```

Create `data/tilesets/<primary|secondary>/<name>/porytiles/decompile.sh`:

```bash
#!/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/<primary|secondary>/<name>/porytiles/decompile.sh"
    exit 1
fi

porytiles decompile-tileset --metatile-attribute-size 2 gTileset_<Name>
echo "Done! Source PNGs updated in data/tilesets/<primary|secondary>/<name>/porytiles_src/"
```

Make them executable: `chmod +x compile.sh decompile.sh`

---

## Directory layout after full setup

```
data/tilesets/secondary/<name>/
├── metatiles.bin               ← Porymap output (legacy, kept for reference)
├── metatile_attributes.bin     ← Porymap output (legacy)
├── tiles.png                   ← Porymap output (legacy)
├── palettes/                   ← Porymap output (legacy)
├── porytiles/                  ← Scripts + Aseprite source file
│   ├── compile.sh
│   ├── decompile.sh
│   └── tileset.aseprite
├── porytiles_src/              ← V2 source PNGs (edit these)
│   ├── bottom.png
│   ├── middle.png
│   ├── top.png
│   └── attributes.csv
└── porytiles_bin/              ← V2 compiled output (read by make)
    ├── metatiles.bin
    ├── metatile_attributes.bin
    ├── tiles.png
    └── palettes/

porytiles/tilesets/gTileset_<Name>/
├── tileset-manifest.json       ← Management registration
└── tileset.cache.json          ← Checksum cache (auto-generated)
```

---

## Key differences from V1

| V1 | V2 |
|----|----|
| `porytiles compile-secondary -o <bin> <src> <primary-src> <behaviors.h>` | `porytiles compile-tileset --metatile-attribute-size 2 gTileset_<Name>` |
| Source in `porytiles/` | Source in `porytiles_src/` |
| Output in tileset root | Output in `porytiles_bin/` |
| No management file required | Requires `porytiles/tilesets/<name>/tileset-manifest.json` |
| Partner primary via positional arg | Partner auto-detected; use `--primary-pairing-mode manual` if wrong |
