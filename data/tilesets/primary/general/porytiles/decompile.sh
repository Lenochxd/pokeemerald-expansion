# !/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/primary/general/porytiles/decompile.sh"
    exit 1
fi

porytiles decompile-primary -o ./data/tilesets/primary/general/porytiles ./data/tilesets/primary/general ./include/constants/metatile_behaviors.h
echo "Done! Don't forget to update tileset.asesprite"
