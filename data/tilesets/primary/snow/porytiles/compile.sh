# !/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/primary/snow/porytiles/compile.sh"
    exit 1
fi

porytiles compile-primary -Wall -o ./data/tilesets/primary/snow ./data/tilesets/primary/snow/porytiles ./include/constants/metatile_behaviors.h
