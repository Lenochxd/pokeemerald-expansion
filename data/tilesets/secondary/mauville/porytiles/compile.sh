#!/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/secondary/mauville/porytiles/compile.sh"
    exit 1
fi

porytiles compile-tileset --metatile-attribute-size 2 gTileset_Mauville
