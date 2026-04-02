# !/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/primary/gibounet/porytiles/compile.sh"
    exit 1
fi

porytiles compile-primary -Wall -o ./data/tilesets/primary/gibounet ./data/tilesets/primary/gibounet/porytiles ./include/constants/metatile_behaviors.h
