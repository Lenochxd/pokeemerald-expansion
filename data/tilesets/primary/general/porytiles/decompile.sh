#!/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/primary/general/porytiles/decompile.sh"
    exit 1
fi

porytiles decompile-tileset --metatile-attribute-size 2 gTileset_General
echo "Done! Source PNGs updated in data/tilesets/primary/general/porytiles_src/"
