#!/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/secondary/haie_froide/porytiles/decompile.sh"
    exit 1
fi

porytiles decompile-tileset --metatile-attribute-size 2 --primary-pairing-mode manual --primary-pairing-partners gTileset_Snow -- gTileset_HaieFroide
echo "Done! Source PNGs updated in data/tilesets/secondary/haie_froide/porytiles_src/"
