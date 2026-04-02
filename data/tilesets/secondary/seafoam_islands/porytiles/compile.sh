# !/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/secondary/seafoam_islands/porytiles/compile.sh"
    exit 1
fi

porytiles compile-secondary -Wall -o ./data/tilesets/secondary/seafoam_islands ./data/tilesets/secondary/seafoam_islands/porytiles ./data/tilesets/primary/gibounet/porytiles ./include/constants/metatile_behaviors.h
