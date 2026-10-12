#!/bin/bash
# Create a new porytiles-managed tileset.
#
# Usage: data/tilesets/new_tileset.sh [Name] [primary|secondary] [partner-primary]
#   Name             PascalCase, e.g. Omaiville or HaieFroide (symbol gTileset_<Name>)
#   primary|secondary  default: secondary
#   partner-primary    primary a secondary is paired with, default: gTileset_General
# Any missing argument is asked for interactively.

set -euo pipefail

cd "$(dirname "$0")/../.."

if [ ! -d porytiles/tilesets ] || [ ! -f src/data/tilesets/headers.h ]; then
    echo "Could not find the repository root. Run this from the repository."
    exit 1
fi

if ! command -v porytiles >/dev/null 2>&1; then
    echo "porytiles not found on PATH. Install porytiles 2.x first."
    exit 1
fi

NAME="${1:-}"
TYPE="${2:-}"
PARTNER="${3:-}"

if [ -z "$NAME" ]; then
    read -rp "Tileset name (PascalCase, e.g. Omaiville): " NAME || true
fi
if [[ ! "$NAME" =~ ^[A-Z][A-Za-z0-9]*$ ]]; then
    echo "Invalid name '$NAME'. Use PascalCase letters and digits, starting with a capital."
    exit 1
fi

if [ -z "$TYPE" ]; then
    read -rp "Type [secondary/primary] (default: secondary): " TYPE || true
    TYPE="${TYPE:-secondary}"
fi
case "$TYPE" in
    primary|secondary) ;;
    *) echo "Type must be 'primary' or 'secondary'."; exit 1 ;;
esac

if [ "$TYPE" = "secondary" ] && [ -z "$PARTNER" ]; then
    read -rp "Partner primary tileset (default: gTileset_General): " PARTNER || true
    PARTNER="${PARTNER:-gTileset_General}"
fi

SYMBOL="gTileset_$NAME"
FOLDER=$(echo "$NAME" | sed -E 's/([a-z0-9])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')
DIR="data/tilesets/$TYPE/$FOLDER"

if [ "$TYPE" = "primary" ] && [ ! -f data/tilesets/primary/general/porytiles_src/top.png ]; then
    echo "Missing data/tilesets/primary/general/porytiles_src/, needed as the base for new primaries."
    exit 1
fi

if grep -q "const struct Tileset $SYMBOL =" src/data/tilesets/headers.h; then
    echo "$SYMBOL already exists in src/data/tilesets/headers.h."
    exit 1
fi
if [ -e "$DIR" ] || [ -e "porytiles/tilesets/$SYMBOL" ]; then
    echo "$DIR or porytiles/tilesets/$SYMBOL already exists."
    exit 1
fi

PAIRING=""
SECONDARY_FLAG=""
if [ "$TYPE" = "secondary" ]; then
    SECONDARY_FLAG="--secondary"
    PAIRING="--primary-pairing-mode manual --primary-pairing-partners $PARTNER"
fi

porytiles create-tileset --metatile-attribute-size 2 $SECONDARY_FLAG $PAIRING -- "$SYMBOL"

if [ "$TYPE" = "primary" ]; then
    cp data/tilesets/primary/general/porytiles_src/{bottom.png,middle.png,top.png,attributes.csv} "$DIR/porytiles_src/"
fi

mkdir -p "$DIR/porytiles"

COMPILE_ARGS="$SYMBOL"
if [ "$TYPE" = "secondary" ] && [ "$PARTNER" != "gTileset_General" ]; then
    COMPILE_ARGS="$PAIRING -- $SYMBOL"
fi

cat > "$DIR/porytiles/compile.sh" <<EOF
#!/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./$DIR/porytiles/compile.sh"
    exit 1
fi

porytiles compile-tileset --metatile-attribute-size 2 $COMPILE_ARGS
EOF
cat > "$DIR/porytiles/decompile.sh" <<EOF
#!/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./$DIR/porytiles/decompile.sh"
    exit 1
fi

porytiles decompile-tileset --metatile-attribute-size 2 $SYMBOL
echo "Done! Source PNGs updated in $DIR/porytiles_src/"
EOF
chmod +x "$DIR/porytiles/compile.sh" "$DIR/porytiles/decompile.sh"

ASEPRITE_MADE=0
if command -v python3 >/dev/null 2>&1 && python3 -c "import PIL" >/dev/null 2>&1; then
    if python3 data/tilesets/make_aseprite.py "$DIR/porytiles_src" "$DIR/porytiles/tileset.aseprite"; then
        ASEPRITE_MADE=1
    fi
fi

echo
echo "Created $SYMBOL in $DIR"
echo
if [ "$ASEPRITE_MADE" = 1 ]; then
    echo "Created $DIR/porytiles/tileset.aseprite with layers bottom, middle, top."
else
    echo "Could not create tileset.aseprite (needs python3 with Pillow: pip install pillow)."
    echo "Paint the PNGs in $DIR/porytiles_src/ directly instead."
fi
cat <<EOF

Next steps:
  1. Paint the tileset. Either open $DIR/porytiles/tileset.aseprite in
     Aseprite and export each layer to $DIR/porytiles_src/<layer>.png
     (bottom.png, middle.png, top.png), keeping the canvas size, or edit those PNGs directly.
  2. Set metatile behaviors in $DIR/porytiles_src/attributes.csv (id,behavior).
  3. Compile: $DIR/porytiles/compile.sh
  4. Use gTileset_$NAME as the secondary tileset of a layout in Porymap.
  5. Build with make.
EOF
