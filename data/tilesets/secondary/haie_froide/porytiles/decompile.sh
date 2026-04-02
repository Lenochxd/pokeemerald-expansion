# !/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/secondary/haie_froide/porytiles/decompile.sh"
    exit 1
fi

porytiles decompile-secondary -o ./data/tilesets/secondary/haie_froide/porytiles ./data/tilesets/secondary/haie_froide ./data/tilesets/primary/snow ./include/constants/metatile_behaviors.h
echo "Done! Don't forget to update tileset.asesprite"
