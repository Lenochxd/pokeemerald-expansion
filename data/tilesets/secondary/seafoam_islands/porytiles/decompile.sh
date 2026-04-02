# !/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/secondary/seafoam_islands/porytiles/decompile.sh"
    exit 1
fi

porytiles decompile-secondary -o ./data/tilesets/secondary/seafoam_islands/porytiles ./data/tilesets/secondary/seafoam_islands ./data/tilesets/primary/gibounet ./include/constants/metatile_behaviors.h
echo "Done! Don't forget to update tileset.asesprite"
