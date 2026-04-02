# !/bin/bash
if pwd | grep -q "porytiles"; then
    echo "Please run this script from the root of the repository."
    echo "./data/tilesets/secondary/haie_froide/porytiles/compile.sh"
    exit 1
fi

porytiles compile-secondary -Wall -o ./data/tilesets/secondary/haie_froide ./data/tilesets/secondary/haie_froide/porytiles ./data/tilesets/primary/snow/porytiles ./include/constants/metatile_behaviors.h
